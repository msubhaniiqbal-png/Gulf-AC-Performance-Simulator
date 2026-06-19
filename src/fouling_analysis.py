from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from fouling import adjusted_condenser_temperature
from model_config import (
    DEFAULT_COMPRESSOR_EFFICIENCY,
    DEFAULT_CONDENSER_APPROACH_C,
    DEFAULT_EVAPORATOR_TEMP_C,
    DEFAULT_SUBCOOLING_C,
    DEFAULT_SUPERHEAT_C,
)
from vcc_model import vapor_compression_cycle


def run_fouling_analysis():
    outdoor_temps = list(range(40, 56))
    # The fouling severity index is a scenario index, not a measured physical
    # percentage of dust mass, fin blockage, or UA loss.
    fouling_levels = [0, 10, 20]
    results = []

    for fouling_severity_index in fouling_levels:
        for outdoor_temp_C in outdoor_temps:
            T_cond_C = adjusted_condenser_temperature(
                outdoor_temperature_C=outdoor_temp_C,
                fouling_severity_index=fouling_severity_index,
                approach_temperature_C=DEFAULT_CONDENSER_APPROACH_C,
            )

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
                    f"fouling_severity_index={fouling_severity_index}, "
                    f"T_cond_C={T_cond_C}: {' '.join(result['warnings'])}"
                )
                continue

            for warning in result["warnings"]:
                print(
                    f"Warning at outdoor_temp_C={outdoor_temp_C}, "
                    f"fouling_severity_index={fouling_severity_index}, "
                    f"T_cond_C={T_cond_C}: {warning}"
                )

            result["outdoor_temp_C"] = outdoor_temp_C
            result["fouling_severity_index"] = fouling_severity_index
            results.append(result)

    df = pd.DataFrame(results)
    if df.empty:
        print("No valid fouling analysis points were calculated.")
        return df

    baseline_COP = df.loc[
        (df["fouling_severity_index"] == 0)
        & (df["outdoor_temp_C"] == df["outdoor_temp_C"].min()),
        "COP",
    ].iloc[0]
    df["cop_degradation_percent"] = (
        (baseline_COP - df["COP"]) / baseline_COP
    ) * 100

    print_df = df[[
        "outdoor_temp_C",
        "fouling_severity_index",
        "T_cond_C",
        "COP",
        "compressor_work_kJ_kg",
        "pressure_ratio",
        "cop_degradation_percent",
    ]].copy()
    print_df = print_df.rename(columns={
        "fouling_severity_index": "Dust fouling severity index",
    })
    print(print_df)

    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/fouling_analysis.csv", index=False)

    plt.figure()
    for fouling_severity_index in fouling_levels:
        fouling_df = df[
            df["fouling_severity_index"] == fouling_severity_index
        ]
        plt.plot(
            fouling_df["outdoor_temp_C"],
            fouling_df["COP"],
            marker="o",
            label=f"{fouling_severity_index} severity index",
        )

    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("COP")
    plt.title("COP Degradation from Condenser Dust Fouling Severity")
    plt.grid(True)
    plt.legend()
    Path("figures").mkdir(exist_ok=True)
    plt.savefig("figures/fouling_effect.png", dpi=300)
    plt.close()

    plt.figure()
    for fouling_severity_index in fouling_levels:
        fouling_df = df[
            df["fouling_severity_index"] == fouling_severity_index
        ]
        plt.plot(
            fouling_df["outdoor_temp_C"],
            fouling_df["cop_degradation_percent"],
            marker="o",
            label=f"{fouling_severity_index} severity index",
        )

    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("COP Degradation (%)")
    plt.title("COP Degradation Percentage from Dust Fouling Severity")
    plt.grid(True)
    plt.legend()
    plt.savefig("figures/fouling_cop_degradation_percent.png", dpi=300)
    plt.close()

    return df


if __name__ == "__main__":
    run_fouling_analysis()
