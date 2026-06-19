# Assumption-based AC profiles for early-stage wattage estimates.
#
# These values are placeholders intended for scenario modeling only. They
# should be validated or replaced with real equipment nameplate data,
# manufacturer performance tables, or measured field data before using the
# estimator for procurement, billing, or engineering decisions.

AC_PROFILES = {
    "split_inverter": {
        "display_name": "Split AC - Inverter",
        "default_eer": 12.0,
        "default_duty_cycle": 0.65,
        "temperature_sensitivity": "medium",
        "fouling_sensitivity": "medium",
        "notes": (
            "Placeholder profile for inverter split AC units. Inverter units "
            "can modulate output, so average power depends strongly on load."
        ),
    },
    "split_non_inverter": {
        "display_name": "Split AC - Non-inverter",
        "default_eer": 10.0,
        "default_duty_cycle": 0.80,
        "temperature_sensitivity": "medium",
        "fouling_sensitivity": "medium",
        "notes": (
            "Placeholder profile for fixed-speed split AC units. Average power "
            "is represented with a simplified duty-cycle assumption."
        ),
    },
    "window_ac": {
        "display_name": "Window / Wall AC",
        "default_eer": 9.0,
        "default_duty_cycle": 0.85,
        "temperature_sensitivity": "high",
        "fouling_sensitivity": "medium",
        "notes": (
            "Placeholder profile for compact window or wall AC units, which "
            "often have lower efficiency than modern split systems."
        ),
    },
    "standing_ac": {
        "display_name": "Standing / Portable AC",
        "default_eer": 8.0,
        "default_duty_cycle": 0.90,
        "temperature_sensitivity": "high",
        "fouling_sensitivity": "high",
        "notes": (
            "Placeholder profile for standing or portable AC units. Actual "
            "performance varies widely with installation and exhaust setup."
        ),
    },
    "ducted_unit": {
        "display_name": "Ducted HVAC Unit",
        "default_eer": 9.5,
        "default_duty_cycle": 0.80,
        "temperature_sensitivity": "medium",
        "fouling_sensitivity": "high",
        "notes": (
            "Placeholder profile for ducted units. Duct losses, fan power, and "
            "installation quality can significantly change real wattage."
        ),
    },
}
