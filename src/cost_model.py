from model_config import DEFAULT_DAYS_PER_MONTH


# Use monthly_energy_cost() when starting from a cooling load and COP.
def monthly_energy_cost(
    cooling_load_kW,
    COP,
    operating_hours_per_day,
    tariff_QAR_per_kWh,
    days_per_month=DEFAULT_DAYS_PER_MONTH,
):
    """
    Estimate monthly HVAC electrical energy use and cost from cooling load.
    """
    if COP <= 0:
        raise ValueError("COP must be greater than zero")

    electrical_power_kW = cooling_load_kW / COP
    daily_energy_kWh = electrical_power_kW * operating_hours_per_day
    monthly_energy_kWh = daily_energy_kWh * days_per_month
    monthly_cost_QAR = monthly_energy_kWh * tariff_QAR_per_kWh

    return {
        "electrical_power_kW": electrical_power_kW,
        "daily_energy_kWh": daily_energy_kWh,
        "monthly_energy_kWh": monthly_energy_kWh,
        "monthly_cost_QAR": monthly_cost_QAR,
    }


# Use energy_cost_from_electric_power() when electrical power is already known.
def energy_cost_from_electric_power(
    electric_power_kW,
    operating_hours_per_day,
    tariff_QAR_per_kWh,
    days_per_month=DEFAULT_DAYS_PER_MONTH,
):
    """
    Estimate energy use and cost from already-estimated electrical power.
    """
    daily_energy_kWh = electric_power_kW * operating_hours_per_day
    monthly_energy_kWh = daily_energy_kWh * days_per_month
    monthly_cost_QAR = monthly_energy_kWh * tariff_QAR_per_kWh

    return {
        "electric_power_kW": electric_power_kW,
        "daily_energy_kWh": daily_energy_kWh,
        "monthly_energy_kWh": monthly_energy_kWh,
        "monthly_cost_QAR": monthly_cost_QAR,
        "tariff_QAR_per_kWh": tariff_QAR_per_kWh,
        "days_per_month": days_per_month,
    }
