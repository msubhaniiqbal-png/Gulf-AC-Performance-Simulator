from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from model_config import (
    DEFAULT_COMPRESSOR_EFFICIENCY,
    DEFAULT_CONDENSER_APPROACH_C,
    DEFAULT_EVAPORATOR_TEMP_C,
    DEFAULT_SUBCOOLING_C,
    DEFAULT_SUPERHEAT_C,
)
from vcc_model import vapor_compression_cycle


def run_refrigerant_comparison():
    refrigerants = ["R134a", "R32", "R410A", "R290"]
    outdoor_temps = list(range(40, 56))
    results = []

    for refrigerant in refrigerants:
        for outdoor_temp_C in outdoor_temps:
            condenser_temp_C = outdoor_temp_C + DEFAULT_CONDENSER_APPROACH_C

            try:
                result = vapor_compression_cycle(
                    fluid=refrigerant,
                    T_evap_C=DEFAULT_EVAPORATOR_TEMP_C,
                    T_cond_C=condenser_temp_C,
                    superheat_C=DEFAULT_SUPERHEAT_C,
                    subcool_C=DEFAULT_SUBCOOLING_C,
                    eta_comp=DEFAULT_COMPRESSOR_EFFICIENCY,
                )
            except Exception as exc:
                print(
                    "Warning: skipping "
                    f"{refrigerant} at outdoor_temp_C={outdoor_temp_C}, "
                    f"condenser_temp_C={condenser_temp_C}: {exc}"
                )
                continue

            if not result["valid"]:
                for warning in result["warnings"]:
                    print(
                        "Warning: skipping "
                        f"{refrigerant} at outdoor_temp_C={outdoor_temp_C}, "
                        f"condenser_temp_C={condenser_temp_C}: {warning}"
                    )
                continue

            for warning in result["warnings"]:
                print(
                    f"Warning for {refrigerant} at "
                    f"outdoor_temp_C={outdoor_temp_C}, "
                    f"condenser_temp_C={condenser_temp_C}: {warning}"
                )

            results.append({
                "refrigerant": refrigerant,
                "outdoor_temp_C": outdoor_temp_C,
                "condenser_temp_C": condenser_temp_C,
                "COP": result["COP"],
                "compressor_work_kJ_kg": result["compressor_work_kJ_kg"],
                "pressure_ratio": result["pressure_ratio"],
                "critical_margin_C": result.get("critical_margin_C"),
            })

    df = pd.DataFrame(results)

    print(df)

    if df.empty:
        print("No valid refrigerant comparison points were calculated.")
        return df

    plt.figure()
    for refrigerant in refrigerants:
        refrigerant_df = df[df["refrigerant"] == refrigerant]
        if refrigerant_df.empty:
            continue

        plt.plot(
            refrigerant_df["outdoor_temp_C"],
            refrigerant_df["COP"],
            marker="o",
            label=refrigerant,
        )

    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("COP")
    plt.title("COP Comparison by Refrigerant")
    plt.grid(True)
    plt.legend()
    Path("figures").mkdir(exist_ok=True)
    plt.savefig("figures/refrigerant_comparison.png", dpi=300)
    plt.close()

    if "critical_margin_C" in df.columns:
        plt.figure()
        for refrigerant in refrigerants:
            refrigerant_df = df[df["refrigerant"] == refrigerant]
            if refrigerant_df.empty:
                continue

            plt.plot(
                refrigerant_df["outdoor_temp_C"],
                refrigerant_df["critical_margin_C"],
                marker="o",
                label=refrigerant,
            )

        plt.axhline(0, color="red", linestyle="--", linewidth=1)
        plt.axhline(5, color="orange", linestyle="--", linewidth=1)
        plt.xlabel("Outdoor Temperature (°C)")
        plt.ylabel("Critical Temperature Margin (°C)")
        plt.title("Critical Temperature Margin by Refrigerant")
        plt.grid(True)
        plt.legend()
        plt.savefig("figures/critical_margin_comparison.png", dpi=300)
        plt.close()

    return df


if __name__ == "__main__":
    run_refrigerant_comparison()
