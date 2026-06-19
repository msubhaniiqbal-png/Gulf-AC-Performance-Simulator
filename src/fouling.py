from model_config import DEFAULT_CONDENSER_APPROACH_C


def fouling_temperature_penalty(fouling_severity_index):
    """
    Return condenser temperature penalty in Celsius for fouling severity.

    The fouling severity index is a scenario index, not a measured physical
    percentage of dust mass, fin blockage, or UA loss.

    Assumption: each severity-index point adds 0.4 C to condenser temperature.
    """
    if not 0 <= fouling_severity_index <= 30:
        raise ValueError("fouling_severity_index must be between 0 and 30")

    return fouling_severity_index * 0.4


def adjusted_condenser_temperature(
    outdoor_temperature_C,
    fouling_severity_index,
    approach_temperature_C=DEFAULT_CONDENSER_APPROACH_C,
):
    """
    Return condenser temperature adjusted for ambient, approach, and fouling.

    The fouling severity index is a scenario index, not a measured physical
    percentage of dust mass, fin blockage, or UA loss.
    """
    return (
        outdoor_temperature_C
        + approach_temperature_C
        + fouling_temperature_penalty(fouling_severity_index)
    )
