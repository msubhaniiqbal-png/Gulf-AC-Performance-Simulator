from wattage_estimator import estimate_ac_wattage


def test_estimated_cooling_capacity_increases_with_tons():
    small = estimate_ac_wattage(
        ac_type="split_inverter",
        tons=1,
        outdoor_temp_C=35,
        fouling_severity_index=0,
    )
    large = estimate_ac_wattage(
        ac_type="split_inverter",
        tons=2,
        outdoor_temp_C=35,
        fouling_severity_index=0,
    )

    assert large["cooling_capacity_kW"] > small["cooling_capacity_kW"]
    assert large["cooling_capacity_BTU_hr"] > small["cooling_capacity_BTU_hr"]


def test_average_watts_is_positive():
    result = estimate_ac_wattage(
        ac_type="split_inverter",
        tons=1.5,
        outdoor_temp_C=35,
        fouling_severity_index=0,
    )

    assert result["average_watts"] > 0


def test_higher_outdoor_temperature_increases_average_watts():
    mild = estimate_ac_wattage(
        ac_type="split_inverter",
        tons=1.5,
        outdoor_temp_C=35,
        fouling_severity_index=0,
    )
    hot = estimate_ac_wattage(
        ac_type="split_inverter",
        tons=1.5,
        outdoor_temp_C=45,
        fouling_severity_index=0,
    )

    assert hot["average_watts"] > mild["average_watts"]


def test_higher_fouling_severity_increases_average_watts():
    clean = estimate_ac_wattage(
        ac_type="split_inverter",
        tons=1.5,
        outdoor_temp_C=45,
        fouling_severity_index=0,
    )
    fouled = estimate_ac_wattage(
        ac_type="split_inverter",
        tons=1.5,
        outdoor_temp_C=45,
        fouling_severity_index=20,
    )

    assert fouled["average_watts"] > clean["average_watts"]
