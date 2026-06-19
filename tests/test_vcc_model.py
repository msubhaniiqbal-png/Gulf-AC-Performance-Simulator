from vcc_model import vapor_compression_cycle


def test_normal_r134a_cycle_is_valid():
    result = vapor_compression_cycle(
        fluid="R134a",
        T_evap_C=10,
        T_cond_C=50,
        superheat_C=5,
        subcool_C=5,
        eta_comp=0.70,
    )

    assert result["valid"] is True


def test_normal_r134a_cycle_has_positive_cop_and_pressure_ratio():
    result = vapor_compression_cycle(
        fluid="R134a",
        T_evap_C=10,
        T_cond_C=50,
        superheat_C=5,
        subcool_C=5,
        eta_comp=0.70,
    )

    assert result["COP"] > 0
    assert result["pressure_ratio"] > 0


def test_higher_condenser_temperature_reduces_cop():
    lower_condensing = vapor_compression_cycle(
        fluid="R134a",
        T_evap_C=10,
        T_cond_C=45,
        superheat_C=5,
        subcool_C=5,
        eta_comp=0.70,
    )
    higher_condensing = vapor_compression_cycle(
        fluid="R134a",
        T_evap_C=10,
        T_cond_C=60,
        superheat_C=5,
        subcool_C=5,
        eta_comp=0.70,
    )

    assert lower_condensing["valid"] is True
    assert higher_condensing["valid"] is True
    assert higher_condensing["COP"] < lower_condensing["COP"]


def test_above_critical_condition_returns_invalid_without_crashing():
    result = vapor_compression_cycle(
        fluid="R410A",
        T_evap_C=10,
        T_cond_C=75,
        superheat_C=5,
        subcool_C=5,
        eta_comp=0.70,
    )

    assert result["valid"] is False
    assert result["critical_margin_C"] <= 0
    assert any("critical temperature" in warning for warning in result["warnings"])


def test_near_critical_condition_returns_warning_without_crashing():
    result = vapor_compression_cycle(
        fluid="R410A",
        T_evap_C=10,
        T_cond_C=68,
        superheat_C=5,
        subcool_C=5,
        eta_comp=0.70,
    )

    assert result["warnings"]
    assert any("critical-temperature" in warning for warning in result["warnings"])
