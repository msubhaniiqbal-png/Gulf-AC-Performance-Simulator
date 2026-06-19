import pytest

from cost_model import energy_cost_from_electric_power, monthly_energy_cost


def test_monthly_energy_cost_from_cooling_load_and_cop():
    result = monthly_energy_cost(
        cooling_load_kW=6,
        COP=3,
        operating_hours_per_day=10,
        tariff_QAR_per_kWh=0.20,
        days_per_month=30,
    )

    assert result["electrical_power_kW"] == pytest.approx(2)
    assert result["daily_energy_kWh"] == pytest.approx(20)
    assert result["monthly_energy_kWh"] == pytest.approx(600)
    assert result["monthly_cost_QAR"] == pytest.approx(120)


def test_energy_cost_from_electric_power():
    result = energy_cost_from_electric_power(
        electric_power_kW=2,
        operating_hours_per_day=10,
        tariff_QAR_per_kWh=0.20,
        days_per_month=30,
    )

    assert result["electric_power_kW"] == pytest.approx(2)
    assert result["daily_energy_kWh"] == pytest.approx(20)
    assert result["monthly_energy_kWh"] == pytest.approx(600)
    assert result["monthly_cost_QAR"] == pytest.approx(120)
    assert result["tariff_QAR_per_kWh"] == pytest.approx(0.20)
    assert result["days_per_month"] == 30


def test_monthly_energy_cost_rejects_invalid_cop():
    with pytest.raises(ValueError, match="COP must be greater than zero"):
        monthly_energy_cost(
            cooling_load_kW=6,
            COP=0,
            operating_hours_per_day=10,
            tariff_QAR_per_kWh=0.20,
        )
