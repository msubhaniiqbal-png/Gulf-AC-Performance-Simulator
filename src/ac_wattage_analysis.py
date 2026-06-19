from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from wattage_estimator import estimate_ac_wattage


def run_ac_wattage_analysis():
    ac_types = [
        "split_inverter",
        "split_non_inverter",
        "window_ac",
        "standing_ac",
    ]
    tons = 1.5
    outdoor_temps = list(range(30, 56))
    fouling_severity_index = 10
    results = []

    for ac_type in ac_types:
        for outdoor_temp_C in outdoor_temps:
            estimate = estimate_ac_wattage(
                ac_type=ac_type,
                tons=tons,
                outdoor_temp_C=outdoor_temp_C,
                fouling_severity_index=fouling_severity_index,
            )

            results.append({
                "ac_type": ac_type,
                "display_name": estimate["display_name"],
                "tons": tons,
                "outdoor_temp_C": outdoor_temp_C,
                "fouling_severity_index": fouling_severity_index,
                "average_watts": estimate["average_watts"],
                "adjusted_running_watts": estimate["adjusted_running_watts"],
                "cooling_capacity_kW": estimate["cooling_capacity_kW"],
                "temperature_multiplier": estimate["temperature_multiplier"],
                "fouling_multiplier": estimate["fouling_multiplier"],
            })

    df = pd.DataFrame(results)
    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/ac_wattage_analysis.csv", index=False)

    summary_df = df[df["outdoor_temp_C"].isin([35, 45, 50])]
    print(summary_df[[
        "display_name",
        "outdoor_temp_C",
        "average_watts",
        "adjusted_running_watts",
        "cooling_capacity_kW",
        "temperature_multiplier",
        "fouling_multiplier",
    ]].to_string(index=False))

    plt.figure()
    for ac_type in ac_types:
        ac_df = df[df["ac_type"] == ac_type]
        plt.plot(
            ac_df["outdoor_temp_C"],
            ac_df["average_watts"],
            marker="o",
            label=ac_df["display_name"].iloc[0],
        )

    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("Average Watts")
    plt.title("Estimated AC Average Wattage vs Outdoor Temperature")
    plt.grid(True)
    plt.legend()
    Path("figures").mkdir(exist_ok=True)
    plt.savefig("figures/ac_wattage_comparison.png", dpi=300)
    plt.close()

    return df


if __name__ == "__main__":
    run_ac_wattage_analysis()
