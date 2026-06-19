from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from model_config import (
    DEFAULT_COMPRESSOR_EFFICIENCY,
    DEFAULT_EVAPORATOR_TEMP_C,
    DEFAULT_SUBCOOLING_C,
    DEFAULT_SUPERHEAT_C,
)
from vcc_model import vapor_compression_cycle


def run_approach_sensitivity(refrigerant="R134a"):
    outdoor_temps = list(range(35, 56))
    condenser_approaches_C = [8, 10, 12, 15]
    rows = []

    for approach_C in condenser_approaches_C:
        for outdoor_temp_C in outdoor_temps:
            T_cond_C = outdoor_temp_C + approach_C

            try:
                result = vapor_compression_cycle(
                    fluid=refrigerant,
                    T_evap_C=DEFAULT_EVAPORATOR_TEMP_C,
                    T_cond_C=T_cond_C,
                    superheat_C=DEFAULT_SUPERHEAT_C,
                    subcool_C=DEFAULT_SUBCOOLING_C,
                    eta_comp=DEFAULT_COMPRESSOR_EFFICIENCY,
                )
            except Exception as exc:
                print(
                    "Warning: skipping "
                    f"approach_C={approach_C}, "
                    f"outdoor_temp_C={outdoor_temp_C}, "
                    f"T_cond_C={T_cond_C}: {exc}"
                )
                continue

            warning_text = " | ".join(result["warnings"])
            if not result["valid"]:
                print(
                    "Warning: skipping "
                    f"approach_C={approach_C}, "
                    f"outdoor_temp_C={outdoor_temp_C}, "
                    f"T_cond_C={T_cond_C}: {warning_text}"
                )
                continue

            for warning in result["warnings"]:
                print(
                    f"Warning for approach_C={approach_C}, "
                    f"outdoor_temp_C={outdoor_temp_C}, "
                    f"T_cond_C={T_cond_C}: {warning}"
                )

            rows.append({
                "refrigerant": refrigerant,
                "outdoor_temp_C": outdoor_temp_C,
                "condenser_approach_C": approach_C,
                "T_cond_C": T_cond_C,
                "COP": result["COP"],
                "compressor_work_kJ_kg": result["compressor_work_kJ_kg"],
                "pressure_ratio": result["pressure_ratio"],
                "critical_margin_C": result.get("critical_margin_C"),
                "warnings": warning_text,
            })

    df = pd.DataFrame(rows)
    if df.empty:
        print("No valid condenser approach sensitivity points were calculated.")
        return df

    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/approach_sensitivity.csv", index=False)

    print(df[[
        "outdoor_temp_C",
        "condenser_approach_C",
        "T_cond_C",
        "COP",
        "compressor_work_kJ_kg",
        "pressure_ratio",
        "critical_margin_C",
    ]])

    plt.figure()
    for approach_C in condenser_approaches_C:
        approach_df = df[df["condenser_approach_C"] == approach_C]
        if approach_df.empty:
            continue

        plt.plot(
            approach_df["outdoor_temp_C"],
            approach_df["COP"],
            marker="o",
            label=f"{approach_C}°C approach",
        )

    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("COP")
    plt.title(f"COP Sensitivity to Condenser Approach Temperature ({refrigerant})")
    plt.grid(True)
    plt.legend()
    Path("figures").mkdir(exist_ok=True)
    plt.savefig("figures/approach_sensitivity_cop.png", dpi=300)
    plt.close()

    return df


if __name__ == "__main__":
    run_approach_sensitivity()
