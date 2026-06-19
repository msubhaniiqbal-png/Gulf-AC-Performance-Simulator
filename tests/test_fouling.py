import pytest

from fouling import adjusted_condenser_temperature, fouling_temperature_penalty


def test_zero_fouling_severity_gives_zero_penalty():
    assert fouling_temperature_penalty(0) == pytest.approx(0)


def test_higher_fouling_severity_gives_higher_condenser_temperature():
    low_fouling = adjusted_condenser_temperature(
        outdoor_temperature_C=45,
        fouling_severity_index=5,
        approach_temperature_C=10,
    )
    high_fouling = adjusted_condenser_temperature(
        outdoor_temperature_C=45,
        fouling_severity_index=20,
        approach_temperature_C=10,
    )

    assert high_fouling > low_fouling


def test_adjusted_condenser_temperature_is_outdoor_plus_approach_plus_penalty():
    outdoor_temperature_C = 45
    fouling_severity_index = 10
    approach_temperature_C = 10

    expected = (
        outdoor_temperature_C
        + approach_temperature_C
        + fouling_temperature_penalty(fouling_severity_index)
    )

    assert adjusted_condenser_temperature(
        outdoor_temperature_C=outdoor_temperature_C,
        fouling_severity_index=fouling_severity_index,
        approach_temperature_C=approach_temperature_C,
    ) == pytest.approx(expected)
