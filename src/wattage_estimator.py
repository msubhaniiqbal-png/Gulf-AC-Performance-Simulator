from ac_profiles import AC_PROFILES
from unit_conversions import (
    btu_per_hr_to_watts_input,
    tons_to_btu_per_hr,
    tons_to_kw_cooling,
)


TEMPERATURE_RATES = {
    "low": 0.008,
    "medium": 0.012,
    "high": 0.016,
}

FOULING_RATES = {
    "low": 0.002,
    "medium": 0.004,
    "high": 0.006,
}


def get_temperature_multiplier(outdoor_temp_C, sensitivity):
    """
    Return a simple outdoor-temperature multiplier for estimated input watts.

    The baseline is 35 C. Higher outdoor temperatures increase estimated
    wattage. This is an assumption-based curve, not manufacturer data.
    """
    if sensitivity not in TEMPERATURE_RATES:
        raise ValueError(f"Unknown temperature sensitivity: {sensitivity}")

    degrees_above_baseline = outdoor_temp_C - 35
    multiplier = 1 + (degrees_above_baseline * TEMPERATURE_RATES[sensitivity])

    return max(0.85, multiplier)


def get_fouling_multiplier(fouling_severity_index, sensitivity):
    """
    Return a simple fouling multiplier for estimated input watts.

    The fouling severity index is a scenario index, not a measured physical
    percentage of dust mass, fin blockage, or UA loss. It is represented as an
    input-power penalty for early scenario modeling and should be validated
    with real data.
    """
    if sensitivity not in FOULING_RATES:
        raise ValueError(f"Unknown fouling sensitivity: {sensitivity}")
    if not 0 <= fouling_severity_index <= 30:
        raise ValueError("fouling_severity_index must be between 0 and 30")

    return 1 + (fouling_severity_index * FOULING_RATES[sensitivity])


def estimate_ac_wattage(
    ac_type,
    tons,
    outdoor_temp_C,
    fouling_severity_index,
    eer=None,
    duty_cycle=None,
    inverter=None,
):
    """
    Estimate average AC wattage from tonnage, EER, temperature, and fouling.

    Tons are cooling capacity, not electrical wattage. This estimator converts
    tons to cooling capacity, estimates running watts from EER, then applies
    simple temperature, dust fouling severity, and duty-cycle assumptions.
    """
    if ac_type not in AC_PROFILES:
        valid_types = ", ".join(sorted(AC_PROFILES))
        raise ValueError(f"Unknown ac_type: {ac_type}. Valid types: {valid_types}")
    if tons <= 0:
        raise ValueError("tons must be greater than zero")

    profile = AC_PROFILES[ac_type]
    selected_eer = eer if eer is not None else profile["default_eer"]
    selected_duty_cycle = (
        duty_cycle if duty_cycle is not None else profile["default_duty_cycle"]
    )

    if selected_eer <= 0:
        raise ValueError("eer must be greater than zero")
    if not 0 <= selected_duty_cycle <= 1:
        raise ValueError("duty_cycle must be between 0 and 1")

    cooling_capacity_BTU_hr = tons_to_btu_per_hr(tons)
    cooling_capacity_kW = tons_to_kw_cooling(tons)
    base_input_watts = btu_per_hr_to_watts_input(
        btu_per_hr=cooling_capacity_BTU_hr,
        eer=selected_eer,
    )

    temperature_multiplier = get_temperature_multiplier(
        outdoor_temp_C=outdoor_temp_C,
        sensitivity=profile["temperature_sensitivity"],
    )
    fouling_multiplier = get_fouling_multiplier(
        fouling_severity_index=fouling_severity_index,
        sensitivity=profile["fouling_sensitivity"],
    )

    adjusted_running_watts = (
        base_input_watts * temperature_multiplier * fouling_multiplier
    )
    average_watts = adjusted_running_watts * selected_duty_cycle

    notes = profile["notes"]
    if inverter is not None:
        notes = (
            f"{notes} Inverter flag was set to {inverter}; this simple model "
            "uses the selected AC profile and duty cycle for the estimate."
        )

    return {
        "ac_type": ac_type,
        "display_name": profile["display_name"],
        "tons": tons,
        "cooling_capacity_BTU_hr": cooling_capacity_BTU_hr,
        "cooling_capacity_kW": cooling_capacity_kW,
        "eer": selected_eer,
        "base_input_watts": base_input_watts,
        "temperature_multiplier": temperature_multiplier,
        "fouling_multiplier": fouling_multiplier,
        "adjusted_running_watts": adjusted_running_watts,
        "duty_cycle": selected_duty_cycle,
        "average_watts": average_watts,
        "notes": notes,
    }
