from pathlib import Path

import pandas as pd

from cost_model import energy_cost_from_electric_power
from model_config import PLACEHOLDER_TARIFF_QAR_PER_KWH
from wattage_estimator import estimate_ac_wattage


def run_ac_cost_comparison():
    operating_hours_per_day = 12
    tariff_QAR_per_kWh = PLACEHOLDER_TARIFF_QAR_PER_KWH

    scenarios = [
        {
            "scenario": "Split inverter clean baseline",
            "ac_type": "split_inverter",
            "tons": 1.5,
            "outdoor_temp_C": 35,
            "fouling_severity_index": 0,
        },
        {
            "scenario": "Split inverter high heat + mild dust severity",
            "ac_type": "split_inverter",
            "tons": 1.5,
            "outdoor_temp_C": 45,
            "fouling_severity_index": 10,
        },
        {
            "scenario": "Split inverter extreme heat + severe dust severity",
            "ac_type": "split_inverter",
            "tons": 1.5,
            "outdoor_temp_C": 50,
            "fouling_severity_index": 20,
        },
        {
            "scenario": "Split non-inverter clean baseline",
            "ac_type": "split_non_inverter",
            "tons": 1.5,
            "outdoor_temp_C": 35,
            "fouling_severity_index": 0,
        },
        {
            "scenario": "Split non-inverter high heat + mild dust severity",
            "ac_type": "split_non_inverter",
            "tons": 1.5,
            "outdoor_temp_C": 45,
            "fouling_severity_index": 10,
        },
        {
            "scenario": "Split non-inverter extreme heat + severe dust severity",
            "ac_type": "split_non_inverter",
            "tons": 1.5,
            "outdoor_temp_C": 50,
            "fouling_severity_index": 20,
        },
        {
            "scenario": "Window AC high heat + mild dust severity",
            "ac_type": "window_ac",
            "tons": 1.5,
            "outdoor_temp_C": 45,
            "fouling_severity_index": 10,
        },
        {
            "scenario": "Standing AC high heat + mild dust severity",
            "ac_type": "standing_ac",
            "tons": 1.5,
            "outdoor_temp_C": 45,
            "fouling_severity_index": 10,
        },
    ]

    rows = []

    for scenario in scenarios:
        wattage_result = estimate_ac_wattage(
            ac_type=scenario["ac_type"],
            tons=scenario["tons"],
            outdoor_temp_C=scenario["outdoor_temp_C"],
            fouling_severity_index=scenario["fouling_severity_index"],
        )

        average_kW = wattage_result["average_watts"] / 1000

        cost_result = energy_cost_from_electric_power(
            electric_power_kW=average_kW,
            operating_hours_per_day=operating_hours_per_day,
            tariff_QAR_per_kWh=tariff_QAR_per_kWh,
        )

        rows.append({
            "scenario": scenario["scenario"],
            "ac_type": scenario["ac_type"],
            "display_name": wattage_result["display_name"],
            "tons": scenario["tons"],
            "outdoor_temp_C": scenario["outdoor_temp_C"],
            "fouling_severity_index": scenario["fouling_severity_index"],
            "average_watts": wattage_result["average_watts"],
            "monthly_kWh": cost_result["monthly_energy_kWh"],
            "monthly_cost_QAR": cost_result["monthly_cost_QAR"],
        })

    df = pd.DataFrame(rows)
    baseline_cost_QAR = df.loc[
        df["scenario"] == "Split inverter clean baseline",
        "monthly_cost_QAR",
    ].iloc[0]
    df["penalty_vs_split_inverter_clean_baseline_QAR"] = (
        df["monthly_cost_QAR"] - baseline_cost_QAR
    )

    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/ac_cost_comparison.csv", index=False)

    print(
        "Tariff is a placeholder assumption and should be replaced with "
        "verified local tariff data."
    )

    print_df = df[[
        "scenario",
        "display_name",
        "tons",
        "outdoor_temp_C",
        "fouling_severity_index",
        "average_watts",
        "monthly_kWh",
        "monthly_cost_QAR",
        "penalty_vs_split_inverter_clean_baseline_QAR",
    ]].copy()
    print_df = print_df.rename(columns={
        "display_name": "AC type",
        "outdoor_temp_C": "outdoor temperature",
        "fouling_severity_index": "Dust fouling severity index",
        "monthly_kWh": "monthly kWh",
        "monthly_cost_QAR": "monthly cost QAR",
        "penalty_vs_split_inverter_clean_baseline_QAR": (
            "penalty compared to split inverter clean baseline"
        ),
    })

    print(print_df.to_string(index=False))

    return df


if __name__ == "__main__":
    run_ac_cost_comparison()
