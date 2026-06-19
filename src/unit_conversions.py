def tons_to_btu_per_hr(tons):
    """
    Convert cooling capacity from refrigeration tons to BTU/hr.

    Tons represent cooling capacity, not electrical wattage.
    1 refrigeration ton = 12,000 BTU/hr.
    """
    return tons * 12000


def tons_to_kw_cooling(tons):
    """
    Convert cooling capacity from refrigeration tons to kW cooling.

    Tons represent cooling capacity, not electrical wattage.
    1 refrigeration ton = 3.517 kW cooling.
    """
    return tons * 3.517


def btu_per_hr_to_watts_input(btu_per_hr, eer):
    """
    Estimate electrical input watts from cooling capacity and EER.

    BTU/hr is cooling capacity, not electrical wattage. EER converts cooling
    output to estimated electrical input with watts = BTU/hr / EER.
    """
    if eer <= 0:
        raise ValueError("eer must be greater than zero")

    return btu_per_hr / eer


def kw_cooling_to_kw_input(kw_cooling, cop):
    """
    Estimate electrical input kW from cooling capacity and COP.

    kW cooling is cooling capacity, not electrical wattage. COP converts
    cooling output to estimated electrical input with electrical kW =
    cooling kW / COP.
    """
    if cop <= 0:
        raise ValueError("cop must be greater than zero")

    return kw_cooling / cop
