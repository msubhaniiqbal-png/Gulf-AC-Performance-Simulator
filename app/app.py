from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ac_profiles import AC_PROFILES
from cost_model import energy_cost_from_electric_power, monthly_energy_cost
from fouling import adjusted_condenser_temperature
from model_config import (
    DEFAULT_COMPRESSOR_EFFICIENCY,
    DEFAULT_CONDENSER_APPROACH_C,
    DEFAULT_EVAPORATOR_TEMP_C,
    DEFAULT_SUBCOOLING_C,
    DEFAULT_SUPERHEAT_C,
    PLACEHOLDER_TARIFF_QAR_PER_KWH,
)
from vcc_model import vapor_compression_cycle
from wattage_estimator import estimate_ac_wattage


REFRIGERANTS = ["R134a", "R32", "R410A", "R290"]
AC_TYPES = [
    "split_inverter",
    "split_non_inverter",
    "window_ac",
    "standing_ac",
    "ducted_unit",
]
ASSUMPTIONS_PATH = PROJECT_ROOT / "report" / "assumptions.md"


def get_default_scenario():
    profile = AC_PROFILES["split_inverter"]

    return {
        "refrigerant": "R134a",
        "outdoor_temp_C": 45,
        "fouling_severity_index": 10,
        "cooling_load_kW": 3.5,
        "operating_hours_per_day": 12,
        "tariff_QAR_per_kWh": PLACEHOLDER_TARIFF_QAR_PER_KWH,
        "compressor_efficiency": DEFAULT_COMPRESSOR_EFFICIENCY,
        "ac_type": "split_inverter",
        "tons": 1.5,
        "use_default_eer": True,
        "eer": profile["default_eer"],
        "duty_cycle": profile["default_duty_cycle"],
    }


def initialize_scenario():
    if "scenario" not in st.session_state:
        st.session_state["scenario"] = get_default_scenario()
        return

    scenario = st.session_state["scenario"]
    if (
        "fouling_percentage" in scenario
        and "fouling_severity_index" not in scenario
    ):
        scenario["fouling_severity_index"] = scenario.pop("fouling_percentage")


def sync_form_widgets_from_scenario():
    if not st.session_state.pop("sync_scenario_form", False):
        return

    scenario = st.session_state["scenario"]
    st.session_state["scenario_refrigerant"] = scenario["refrigerant"]
    st.session_state["scenario_outdoor_temp_C"] = scenario["outdoor_temp_C"]
    st.session_state["scenario_fouling_severity_index"] = scenario[
        "fouling_severity_index"
    ]
    st.session_state["scenario_cooling_load_kW"] = scenario["cooling_load_kW"]
    st.session_state["scenario_operating_hours_per_day"] = scenario[
        "operating_hours_per_day"
    ]
    st.session_state["scenario_tariff_QAR_per_kWh"] = scenario[
        "tariff_QAR_per_kWh"
    ]
    st.session_state["scenario_compressor_efficiency"] = scenario[
        "compressor_efficiency"
    ]
    st.session_state["scenario_ac_type"] = scenario["ac_type"]
    st.session_state["scenario_tons"] = scenario["tons"]
    st.session_state["scenario_use_default_eer"] = scenario["use_default_eer"]
    st.session_state["scenario_eer"] = scenario["eer"]
    st.session_state["scenario_duty_cycle"] = scenario["duty_cycle"]


def calculate_cycle(
    refrigerant,
    outdoor_temp_C,
    fouling_severity_index,
    compressor_efficiency,
):
    condenser_temp_C = adjusted_condenser_temperature(
        outdoor_temperature_C=outdoor_temp_C,
        fouling_severity_index=fouling_severity_index,
        approach_temperature_C=DEFAULT_CONDENSER_APPROACH_C,
    )

    cycle_result = vapor_compression_cycle(
        fluid=refrigerant,
        T_evap_C=DEFAULT_EVAPORATOR_TEMP_C,
        T_cond_C=condenser_temp_C,
        superheat_C=DEFAULT_SUPERHEAT_C,
        subcool_C=DEFAULT_SUBCOOLING_C,
        eta_comp=compressor_efficiency,
    )

    return condenser_temp_C, cycle_result


@st.cache_data(show_spinner=False)
def build_cop_chart_data(
    refrigerant,
    fouling_severity_index,
    compressor_efficiency,
):
    rows = []
    warnings = []

    for outdoor_temp_C in range(30, 56):
        try:
            condenser_temp_C, cycle_result = calculate_cycle(
                refrigerant=refrigerant,
                outdoor_temp_C=outdoor_temp_C,
                fouling_severity_index=fouling_severity_index,
                compressor_efficiency=compressor_efficiency,
            )
        except Exception as exc:
            warnings.append(
                f"Skipped {refrigerant} at {outdoor_temp_C}°C outdoor "
                f"temperature: {exc}"
            )
            continue

        if not cycle_result["valid"]:
            warnings.append(
                f"Skipped {refrigerant} at {outdoor_temp_C}°C outdoor "
                f"temperature: {' '.join(cycle_result['warnings'])}"
            )
            continue

        for warning in cycle_result["warnings"]:
            warnings.append(
                f"{refrigerant} at {outdoor_temp_C}°C outdoor temperature: "
                f"{warning}"
            )

        rows.append({
            "outdoor_temp_C": outdoor_temp_C,
            "condenser_temp_C": condenser_temp_C,
            "COP": cycle_result["COP"],
        })

    return pd.DataFrame(rows), warnings


@st.cache_data(show_spinner=False)
def build_wattage_chart_data(
    ac_type,
    tons,
    fouling_severity_index,
    selected_eer,
    duty_cycle,
):
    rows = []

    for outdoor_temp_C in range(30, 56):
        estimate = estimate_ac_wattage(
            ac_type=ac_type,
            tons=tons,
            outdoor_temp_C=outdoor_temp_C,
            fouling_severity_index=fouling_severity_index,
            eer=selected_eer,
            duty_cycle=duty_cycle,
        )

        rows.append({
            "outdoor_temp_C": outdoor_temp_C,
            "average_watts": estimate["average_watts"],
        })

    return pd.DataFrame(rows)


def display_cycle_warning(warning):
    lower_warning = warning.lower()
    if "severe" in lower_warning or "invalid condition" in lower_warning:
        st.error(warning)
    elif "caution" in lower_warning or "warning" in lower_warning:
        st.warning(warning)
    else:
        st.info(warning)


def format_state_value(value):
    if value is None:
        return "N/A"

    return f"{value:.3f}"


def format_temperature_metric(value):
    if value is None:
        return "N/A"

    return f"{value:.1f} °C"


def build_cycle_state_table(cycle_result):
    x4_quality = cycle_result.get("x4_quality")
    state_4_notes = "Constant-enthalpy expansion outlet"
    if x4_quality is not None and 0 <= x4_quality <= 1:
        state_4_notes = f"{state_4_notes}; quality = {x4_quality:.3f}"

    return pd.DataFrame([
        {
            "State": "State 1",
            "Description": "Compressor inlet / evaporator outlet",
            "Temperature (°C)": format_state_value(cycle_result.get("T1_C")),
            "Enthalpy (kJ/kg)": format_state_value(cycle_result.get("h1_kJ_kg")),
            "Entropy (kJ/kg·K)": format_state_value(
                cycle_result.get("s1_kJ_kgK")
            ),
            "Notes": "Superheated vapor",
        },
        {
            "State": "State 2s",
            "Description": "Ideal compressor outlet",
            "Temperature (°C)": format_state_value(cycle_result.get("T2s_C")),
            "Enthalpy (kJ/kg)": format_state_value(cycle_result.get("h2s_kJ_kg")),
            "Entropy (kJ/kg·K)": format_state_value(
                cycle_result.get("s2s_kJ_kgK")
            ),
            "Notes": "Isentropic reference state",
        },
        {
            "State": "State 2",
            "Description": "Real compressor outlet",
            "Temperature (°C)": format_state_value(cycle_result.get("T2_C")),
            "Enthalpy (kJ/kg)": format_state_value(cycle_result.get("h2_kJ_kg")),
            "Entropy (kJ/kg·K)": format_state_value(
                cycle_result.get("s2_kJ_kgK")
            ),
            "Notes": "Discharge state",
        },
        {
            "State": "State 3",
            "Description": "Condenser outlet",
            "Temperature (°C)": format_state_value(cycle_result.get("T3_C")),
            "Enthalpy (kJ/kg)": format_state_value(cycle_result.get("h3_kJ_kg")),
            "Entropy (kJ/kg·K)": format_state_value(
                cycle_result.get("s3_kJ_kgK")
            ),
            "Notes": "Subcooled liquid",
        },
        {
            "State": "State 4",
            "Description": "Expansion valve outlet / evaporator inlet",
            "Temperature (°C)": format_state_value(cycle_result.get("T4_C")),
            "Enthalpy (kJ/kg)": format_state_value(cycle_result.get("h4_kJ_kg")),
            "Entropy (kJ/kg·K)": format_state_value(
                cycle_result.get("s4_kJ_kgK")
            ),
            "Notes": state_4_notes,
        },
    ])


def render_sidebar_form():
    scenario = st.session_state["scenario"]
    current_profile = AC_PROFILES.get(
        scenario["ac_type"],
        AC_PROFILES["split_inverter"],
    )

    st.sidebar.title("Gulf AC Scenario Inputs")
    if st.session_state.pop("scenario_updated", False):
        st.sidebar.success("Simulation inputs updated.")

    with st.sidebar.form("scenario_form"):
        refrigerant = st.selectbox(
            "Refrigerant",
            REFRIGERANTS,
            index=REFRIGERANTS.index(scenario["refrigerant"]),
            key="scenario_refrigerant",
        )
        outdoor_temp_C = st.slider(
            "Outdoor temperature (°C)",
            30,
            55,
            int(scenario["outdoor_temp_C"]),
            key="scenario_outdoor_temp_C",
        )
        fouling_severity_index = st.slider(
            "Dust fouling severity index",
            0,
            30,
            int(scenario["fouling_severity_index"]),
            key="scenario_fouling_severity_index",
        )
        st.caption(
            "The fouling severity index is a scenario index, not a measured "
            "physical percentage of dust mass, fin blockage, or UA loss."
        )
        cooling_load_kW = st.slider(
            "Cooling load (kW)",
            1.0,
            10.0,
            float(scenario["cooling_load_kW"]),
            0.1,
            key="scenario_cooling_load_kW",
        )
        operating_hours_per_day = st.slider(
            "Operating hours per day",
            1,
            24,
            int(scenario["operating_hours_per_day"]),
            key="scenario_operating_hours_per_day",
        )
        tariff_QAR_per_kWh = st.number_input(
            "Tariff QAR/kWh",
            min_value=0.0,
            value=float(scenario["tariff_QAR_per_kWh"]),
            step=0.01,
            key="scenario_tariff_QAR_per_kWh",
        )
        st.caption("Tariff is a placeholder assumption, not an official tariff.")
        compressor_efficiency = st.slider(
            "Compressor efficiency",
            0.60,
            0.85,
            float(scenario["compressor_efficiency"]),
            0.01,
            key="scenario_compressor_efficiency",
        )
        ac_type = st.selectbox(
            "AC type",
            AC_TYPES,
            index=AC_TYPES.index(scenario["ac_type"]),
            key="scenario_ac_type",
        )
        tons = st.slider(
            "Tons",
            0.5,
            10.0,
            float(scenario["tons"]),
            0.5,
            key="scenario_tons",
        )
        use_default_eer = st.checkbox(
            "Use default EER",
            value=bool(scenario["use_default_eer"]),
            key="scenario_use_default_eer",
        )
        eer = st.number_input(
            "EER",
            min_value=1.0,
            value=float(scenario.get("eer", current_profile["default_eer"])),
            step=0.1,
            disabled=use_default_eer,
            key="scenario_eer",
        )
        duty_cycle = st.slider(
            "Duty cycle",
            0.10,
            1.00,
            float(scenario.get("duty_cycle", current_profile["default_duty_cycle"])),
            0.05,
            key="scenario_duty_cycle",
        )

        submitted = st.form_submit_button("Update simulation")

    if submitted:
        previous_ac_type = scenario["ac_type"]
        previous_profile = AC_PROFILES.get(
            previous_ac_type,
            AC_PROFILES["split_inverter"],
        )
        selected_profile = AC_PROFILES[ac_type]

        if use_default_eer:
            stored_eer = selected_profile["default_eer"]
        elif (
            previous_ac_type != ac_type
            and scenario["use_default_eer"]
            and eer == previous_profile["default_eer"]
        ):
            stored_eer = selected_profile["default_eer"]
        else:
            stored_eer = eer

        if (
            previous_ac_type != ac_type
            and duty_cycle == previous_profile["default_duty_cycle"]
        ):
            stored_duty_cycle = selected_profile["default_duty_cycle"]
        else:
            stored_duty_cycle = duty_cycle

        st.session_state["scenario"] = {
            "refrigerant": refrigerant,
            "outdoor_temp_C": outdoor_temp_C,
            "fouling_severity_index": fouling_severity_index,
            "cooling_load_kW": cooling_load_kW,
            "operating_hours_per_day": operating_hours_per_day,
            "tariff_QAR_per_kWh": tariff_QAR_per_kWh,
            "compressor_efficiency": compressor_efficiency,
            "ac_type": ac_type,
            "tons": tons,
            "use_default_eer": use_default_eer,
            "eer": stored_eer,
            "duty_cycle": stored_duty_cycle,
        }
        st.session_state["scenario_updated"] = True
        st.session_state["sync_scenario_form"] = True
        st.rerun()

    return st.session_state["scenario"]


def render_thermodynamic_tab(scenario):
    st.header("Idealized Thermodynamic Cycle")
    st.info(
        "This model is intended to study COP and refrigerant-cycle sensitivity "
        "under simplified assumptions."
    )
    st.caption(
        "The thermodynamic model and wattage estimator are complementary but "
        "independent. Differences between their power estimates are expected."
    )
    st.caption("Tariff is a placeholder assumption, not an official tariff.")

    try:
        condenser_temp_C, cycle_result = calculate_cycle(
            refrigerant=scenario["refrigerant"],
            outdoor_temp_C=scenario["outdoor_temp_C"],
            fouling_severity_index=scenario["fouling_severity_index"],
            compressor_efficiency=scenario["compressor_efficiency"],
        )
        if not cycle_result["valid"]:
            st.error(
                "Cycle result is invalid for the selected condition. COP and "
                "cost outputs are not shown."
            )
            for warning in cycle_result["warnings"]:
                display_cycle_warning(warning)
            critical_cols = st.columns(2)
            critical_cols[0].metric(
                "Refrigerant critical temperature",
                format_temperature_metric(cycle_result.get("Tcrit_C")),
            )
            critical_cols[1].metric(
                "Critical temperature margin",
                format_temperature_metric(cycle_result.get("critical_margin_C")),
            )
            st.caption(
                "Critical temperature margin indicates how close the selected "
                "condenser condition is to the refrigerant critical point. "
                "Small margins reduce physical reliability of the idealized "
                "cycle output."
            )
            return

        for warning in cycle_result["warnings"]:
            display_cycle_warning(warning)

        cost_result = monthly_energy_cost(
            cooling_load_kW=scenario["cooling_load_kW"],
            COP=cycle_result["COP"],
            operating_hours_per_day=scenario["operating_hours_per_day"],
            tariff_QAR_per_kWh=scenario["tariff_QAR_per_kWh"],
        )
    except Exception as exc:
        st.error(f"Unable to calculate this thermodynamic condition: {exc}")
        return

    performance_cols = st.columns(6)
    performance_cols[0].metric(
        "Adjusted condenser temperature",
        f"{condenser_temp_C:.1f} °C",
    )
    performance_cols[1].metric("COP", f"{cycle_result['COP']:.2f}")
    performance_cols[2].metric(
        "Compressor work",
        f"{cycle_result['compressor_work_kJ_kg']:.2f} kJ/kg",
    )
    performance_cols[3].metric(
        "Pressure ratio",
        f"{cycle_result['pressure_ratio']:.2f}",
    )
    performance_cols[4].metric(
        "Critical temperature",
        format_temperature_metric(cycle_result.get("Tcrit_C")),
    )
    performance_cols[5].metric(
        "Critical margin",
        format_temperature_metric(cycle_result.get("critical_margin_C")),
    )
    st.caption(
        "Critical temperature margin indicates how close the selected condenser "
        "condition is to the refrigerant critical point. Small margins reduce "
        "physical reliability of the idealized cycle output."
    )

    cost_cols = st.columns(3)
    cost_cols[0].metric(
        "Monthly energy",
        f"{cost_result['monthly_energy_kWh']:,.1f} kWh",
    )
    cost_cols[1].metric(
        "Monthly cost",
        f"{cost_result['monthly_cost_QAR']:,.2f} QAR",
    )
    cost_cols[2].metric(
        "Electrical power",
        f"{cost_result['electrical_power_kW']:.2f} kW",
    )

    st.subheader("Cycle state points")
    st.caption(
        "State values are from an idealized vapor-compression cycle and should "
        "be interpreted as sensitivity outputs, not manufacturer-validated "
        "equipment data."
    )
    st.dataframe(
        build_cycle_state_table(cycle_result),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("COP vs Outdoor Temperature")
    chart_df, chart_warnings = build_cop_chart_data(
        refrigerant=scenario["refrigerant"],
        fouling_severity_index=scenario["fouling_severity_index"],
        compressor_efficiency=scenario["compressor_efficiency"],
    )
    for warning in chart_warnings[:3]:
        display_cycle_warning(warning)
    if len(chart_warnings) > 3:
        display_cycle_warning(
            f"{len(chart_warnings) - 3} additional chart points were skipped."
        )

    if chart_df.empty:
        st.warning("No valid COP chart points for the selected inputs.")
    else:
        st.line_chart(chart_df, x="outdoor_temp_C", y="COP")


def render_wattage_tab(scenario):
    st.header("Practical EER-Based Wattage Estimate")
    st.info(
        "This estimate is based on EER, duty cycle, and scenario multipliers. "
        "It is not a measured or manufacturer-calibrated power prediction."
    )
    st.caption(
        "The thermodynamic model and wattage estimator are complementary but "
        "independent. Differences between their power estimates are expected."
    )
    st.info(
        "These are engineering estimates based on simplified assumptions. "
        "Results should be validated using manufacturer data or measured "
        "power consumption."
    )
    st.caption("Tariff is a placeholder assumption, not an official tariff.")

    selected_eer = None if scenario["use_default_eer"] else scenario["eer"]
    wattage_result = estimate_ac_wattage(
        ac_type=scenario["ac_type"],
        tons=scenario["tons"],
        outdoor_temp_C=scenario["outdoor_temp_C"],
        fouling_severity_index=scenario["fouling_severity_index"],
        eer=selected_eer,
        duty_cycle=scenario["duty_cycle"],
    )

    average_kW = wattage_result["average_watts"] / 1000
    cost_result = energy_cost_from_electric_power(
        electric_power_kW=average_kW,
        operating_hours_per_day=scenario["operating_hours_per_day"],
        tariff_QAR_per_kWh=scenario["tariff_QAR_per_kWh"],
    )

    overview_cols = st.columns(4)
    overview_cols[0].metric("AC type", wattage_result["display_name"])
    overview_cols[1].metric("Tons", f"{scenario['tons']:.1f}")
    overview_cols[2].metric(
        "Cooling capacity BTU/hr",
        f"{wattage_result['cooling_capacity_BTU_hr']:,.0f}",
    )
    overview_cols[3].metric(
        "Cooling capacity kW",
        f"{wattage_result['cooling_capacity_kW']:.2f} kW",
    )

    wattage_cols = st.columns(3)
    wattage_cols[0].metric(
        "Base input watts",
        f"{wattage_result['base_input_watts']:,.0f} W",
    )
    wattage_cols[1].metric(
        "Adjusted running watts",
        f"{wattage_result['adjusted_running_watts']:,.0f} W",
    )
    wattage_cols[2].metric(
        "Average watts",
        f"{wattage_result['average_watts']:,.0f} W",
    )

    cost_cols = st.columns(3)
    cost_cols[0].metric(
        "Monthly kWh",
        f"{cost_result['monthly_energy_kWh']:,.1f} kWh",
    )
    cost_cols[1].metric(
        "Monthly cost QAR",
        f"{cost_result['monthly_cost_QAR']:,.2f} QAR",
    )
    cost_cols[2].metric("EER used", f"{wattage_result['eer']:.1f}")

    st.subheader("Average Watts vs Outdoor Temperature")
    wattage_chart_df = build_wattage_chart_data(
        ac_type=scenario["ac_type"],
        tons=scenario["tons"],
        fouling_severity_index=scenario["fouling_severity_index"],
        selected_eer=selected_eer,
        duty_cycle=scenario["duty_cycle"],
    )
    st.line_chart(wattage_chart_df, x="outdoor_temp_C", y="average_watts")


def render_assumptions_tab():
    st.header("Assumptions & Scope")
    st.info(
        "This project is a student sensitivity simulator, not a professional "
        "HVAC design tool or manufacturer-calibrated equipment predictor."
    )

    if not ASSUMPTIONS_PATH.exists():
        st.warning("Assumptions documentation is not available.")
        return

    st.markdown(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))


def main():
    st.set_page_config(
        page_title="Gulf AC Performance, Wattage & Cost Estimator",
        layout="wide",
    )
    initialize_scenario()
    sync_form_widgets_from_scenario()

    st.title("Gulf AC Performance, Wattage & Cost Estimator")
    st.info(
        "This dashboard contains two related but separate models. The CoolProp "
        "cycle model studies idealized thermodynamic sensitivity. The wattage "
        "model estimates practical power and cost using EER, tonnage, duty "
        "cycle, temperature, and fouling assumptions. Results are trend "
        "estimates, not manufacturer-calibrated predictions."
    )
    scenario = render_sidebar_form()

    thermodynamic_tab, wattage_tab, assumptions_tab = st.tabs([
        "Idealized Thermodynamic Cycle",
        "Practical EER-Based Wattage Estimate",
        "Assumptions & Scope",
    ])

    with thermodynamic_tab:
        render_thermodynamic_tab(scenario)

    with wattage_tab:
        render_wattage_tab(scenario)

    with assumptions_tab:
        render_assumptions_tab()


if __name__ == "__main__":
    main()
