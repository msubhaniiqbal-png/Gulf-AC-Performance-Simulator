from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from model_config import (
    DEFAULT_COMPRESSOR_EFFICIENCY,
    DEFAULT_CONDENSER_APPROACH_C,
    DEFAULT_EVAPORATOR_TEMP_C,
    DEFAULT_SUBCOOLING_C,
    DEFAULT_SUPERHEAT_C,
)
from vcc_model import vapor_compression_cycle


def run_high_ambient_analysis():
    outdoor_temps = list(range(40, 56))
    results = []

    for outdoor_temp_C in outdoor_temps:
        condenser_approach_C = DEFAULT_CONDENSER_APPROACH_C
        T_cond_C = outdoor_temp_C + condenser_approach_C

        result = vapor_compression_cycle(
            fluid="R134a",
            T_evap_C=DEFAULT_EVAPORATOR_TEMP_C,
            T_cond_C=T_cond_C,
            superheat_C=DEFAULT_SUPERHEAT_C,
            subcool_C=DEFAULT_SUBCOOLING_C,
            eta_comp=DEFAULT_COMPRESSOR_EFFICIENCY,
        )

        if not result["valid"]:
            print(
                f"Skipping outdoor_temp_C={outdoor_temp_C}, "
                f"T_cond_C={T_cond_C}: {' '.join(result['warnings'])}"
            )
            continue

        for warning in result["warnings"]:
            print(
                f"Warning at outdoor_temp_C={outdoor_temp_C}, "
                f"T_cond_C={T_cond_C}: {warning}"
            )

        result["outdoor_temp_C"] = outdoor_temp_C
        result["condenser_approach_C"] = condenser_approach_C
        results.append(result)

    df = pd.DataFrame(results)
    if df.empty:
        print("No valid high ambient analysis points were calculated.")
        return df

    baseline_COP = df.loc[
        df["outdoor_temp_C"] == df["outdoor_temp_C"].min(),
        "COP",
    ].iloc[0]
    df["cop_degradation_percent"] = (
        (baseline_COP - df["COP"]) / baseline_COP
    ) * 100

    print(df[[
        "outdoor_temp_C",
        "T_cond_C",
        "COP",
        "compressor_work_kJ_kg",
        "pressure_ratio",
        "cop_degradation_percent",
    ]])

    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/high_ambient_analysis.csv", index=False)

    plt.figure()
    plt.plot(df["outdoor_temp_C"], df["COP"], marker="o")
    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("COP")
    plt.title("COP Degradation at High Ambient Temperature")
    plt.grid(True)
    Path("figures").mkdir(exist_ok=True)
    plt.savefig("figures/cop_vs_outdoor_temp.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(
        df["outdoor_temp_C"],
        df["cop_degradation_percent"],
        marker="o",
    )
    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("COP Degradation (%)")
    plt.title("COP Degradation Percentage vs Outdoor Temperature")
    plt.grid(True)
    plt.savefig("figures/cop_degradation_percent.png", dpi=300)
    plt.close()

    return df


if __name__ == "__main__":
    run_high_ambient_analysis()
