from pathlib import Path

import pandas as pd

from cost_model import monthly_energy_cost
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


def run_cost_analysis():
    cooling_load_kW = 3.5
    operating_hours_per_day = 12
    tariff_QAR_per_kWh = PLACEHOLDER_TARIFF_QAR_PER_KWH

    scenarios = [
        {
            "scenario": "Clean baseline",
            "outdoor_temp_C": 40,
            "fouling_severity_index": 0,
        },
        {
            "scenario": "High heat",
            "outdoor_temp_C": 50,
            "fouling_severity_index": 0,
        },
        {
            "scenario": "High heat + dust",
            "outdoor_temp_C": 50,
            "fouling_severity_index": 20,
        },
    ]

    rows = []

    for scenario in scenarios:
        condenser_temp_C = adjusted_condenser_temperature(
            outdoor_temperature_C=scenario["outdoor_temp_C"],
            fouling_severity_index=scenario["fouling_severity_index"],
            approach_temperature_C=DEFAULT_CONDENSER_APPROACH_C,
        )

        cycle_result = vapor_compression_cycle(
            fluid="R134a",
            T_evap_C=DEFAULT_EVAPORATOR_TEMP_C,
            T_cond_C=condenser_temp_C,
            superheat_C=DEFAULT_SUPERHEAT_C,
            subcool_C=DEFAULT_SUBCOOLING_C,
            eta_comp=DEFAULT_COMPRESSOR_EFFICIENCY,
        )

        if not cycle_result["valid"]:
            print(
                f"Skipping scenario '{scenario['scenario']}': "
                f"{' '.join(cycle_result['warnings'])}"
            )
            continue

        for warning in cycle_result["warnings"]:
            print(f"Warning for scenario '{scenario['scenario']}': {warning}")

        cost_result = monthly_energy_cost(
            cooling_load_kW=cooling_load_kW,
            COP=cycle_result["COP"],
            operating_hours_per_day=operating_hours_per_day,
            tariff_QAR_per_kWh=tariff_QAR_per_kWh,
        )

        rows.append({
            "scenario": scenario["scenario"],
            "outdoor_temp_C": scenario["outdoor_temp_C"],
            "fouling_severity_index": scenario["fouling_severity_index"],
            "COP": cycle_result["COP"],
            "monthly_energy_kWh": cost_result["monthly_energy_kWh"],
            "monthly_cost_QAR": cost_result["monthly_cost_QAR"],
        })

    df = pd.DataFrame(rows)
    baseline_cost_QAR = df.loc[
        df["scenario"] == "Clean baseline",
        "monthly_cost_QAR",
    ].iloc[0]
    df["penalty_compared_to_baseline_QAR"] = (
        df["monthly_cost_QAR"] - baseline_cost_QAR
    )

    print(f"Tariff placeholder assumption: {PLACEHOLDER_TARIFF_QAR_PER_KWH} QAR/kWh")
    print(df.to_string(index=False))

    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/cost_analysis.csv", index=False)

    return df


if __name__ == "__main__":
    run_cost_analysis()
