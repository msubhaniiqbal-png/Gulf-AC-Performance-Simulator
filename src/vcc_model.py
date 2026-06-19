from CoolProp.CoolProp import PropsSI

from model_config import (
    DEFAULT_COMPRESSOR_EFFICIENCY,
    DEFAULT_EVAPORATOR_TEMP_C,
    DEFAULT_SUBCOOLING_C,
    DEFAULT_SUPERHEAT_C,
)


def validate_vapor_compression_inputs(
    fluid,
    T_evap_C,
    T_cond_C,
    superheat_C,
    subcool_C,
    eta_comp,
):
    """
    Validate vapor-compression cycle inputs before property calculations.

    Returns a dictionary with valid, warnings, and critical-temperature data.
    """
    warnings = []
    has_blocking_error = False

    if T_cond_C <= T_evap_C:
        warnings.append(
            "Condenser temperature must be greater than evaporator temperature."
        )
        has_blocking_error = True

    if not 0 < eta_comp <= 1:
        warnings.append(
            "Compressor isentropic efficiency must be greater than 0 and less "
            "than or equal to 1."
        )
        has_blocking_error = True

    if superheat_C < 0:
        warnings.append("Superheat should not be negative.")
        has_blocking_error = True

    if subcool_C < 0:
        warnings.append("Subcooling should not be negative.")
        has_blocking_error = True

    Tcrit_K = None
    Tcrit_C = None
    critical_margin_C = None

    try:
        Tcrit_K = PropsSI("Tcrit", fluid)
        Tcrit_C = Tcrit_K - 273.15
        critical_margin_C = Tcrit_C - T_cond_C
    except Exception as exc:
        warnings.append(
            "Critical temperature could not be checked for refrigerant "
            f"'{fluid}': {exc}"
        )
        has_blocking_error = True
        return {
            "valid": False,
            "warnings": warnings,
            "Tcrit_K": Tcrit_K,
            "Tcrit_C": Tcrit_C,
            "critical_margin_C": critical_margin_C,
        }

    if critical_margin_C <= 0:
        warnings.append(
            "Invalid condition: condenser temperature is at or above the "
            "refrigerant critical temperature. Cycle calculation is not "
            "physically meaningful."
        )
        has_blocking_error = True
    elif critical_margin_C <= 5:
        warnings.append(
            "Severe critical-temperature warning: condenser temperature is "
            "within 5°C of the refrigerant critical temperature. Results are "
            "highly sensitive and should not be interpreted as real equipment "
            "performance."
        )
    elif critical_margin_C <= 10:
        warnings.append(
            "Critical-temperature caution: condenser temperature is within "
            "10°C of the refrigerant critical temperature."
        )

    return {
        "valid": not has_blocking_error,
        "warnings": warnings,
        "Tcrit_K": Tcrit_K,
        "Tcrit_C": Tcrit_C,
        "critical_margin_C": critical_margin_C,
    }


def _invalid_cycle_result(fluid, T_evap_C, T_cond_C, validation):
    return {
        "fluid": fluid,
        "T_evap_C": T_evap_C,
        "T_cond_C": T_cond_C,
        "Tcrit_C": validation["Tcrit_C"],
        "critical_margin_C": validation["critical_margin_C"],
        "T1_C": None,
        "T2_C": None,
        "T2s_C": None,
        "T3_C": None,
        "T4_C": None,
        "discharge_temp_C": None,
        "COP": None,
        "cooling_effect_kJ_kg": None,
        "compressor_work_kJ_kg": None,
        "P_evap_kPa": None,
        "P_cond_kPa": None,
        "pressure_ratio": None,
        "h1_kJ_kg": None,
        "h2_kJ_kg": None,
        "h2s_kJ_kg": None,
        "h3_kJ_kg": None,
        "h4_kJ_kg": None,
        "s1_kJ_kgK": None,
        "s2s_kJ_kgK": None,
        "s2_kJ_kgK": None,
        "s3_kJ_kgK": None,
        "s4_kJ_kgK": None,
        "x4_quality": None,
        "warnings": validation["warnings"],
        "valid": False,
    }


def _safe_propssi(output, name1, value1, name2, value2, fluid, warnings, label):
    try:
        return PropsSI(output, name1, value1, name2, value2, fluid)
    except Exception as exc:
        warnings.append(f"Unable to calculate {label}: {exc}")
        return None


def vapor_compression_cycle(
    fluid="R134a",
    T_evap_C=DEFAULT_EVAPORATOR_TEMP_C,
    T_cond_C=45,
    superheat_C=DEFAULT_SUPERHEAT_C,
    subcool_C=DEFAULT_SUBCOOLING_C,
    eta_comp=DEFAULT_COMPRESSOR_EFFICIENCY,
):
    """
    Simple vapor-compression refrigeration cycle model.

    State 1: Compressor inlet, superheated vapor
    State 2: Compressor outlet, real compression
    State 3: Condenser outlet, subcooled liquid
    State 4: Expansion valve outlet, constant enthalpy expansion

    Returns performance values in kJ/kg, kPa, and dimensionless COP.
    """

    validation = validate_vapor_compression_inputs(
        fluid=fluid,
        T_evap_C=T_evap_C,
        T_cond_C=T_cond_C,
        superheat_C=superheat_C,
        subcool_C=subcool_C,
        eta_comp=eta_comp,
    )
    warnings = validation["warnings"].copy()

    if not validation["valid"]:
        return _invalid_cycle_result(fluid, T_evap_C, T_cond_C, validation)

    # Convert Celsius to Kelvin
    T_evap_K = T_evap_C + 273.15
    T_cond_K = T_cond_C + 273.15

    # Saturation pressures
    P_evap = PropsSI("P", "T", T_evap_K, "Q", 1, fluid)
    P_cond = PropsSI("P", "T", T_cond_K, "Q", 0, fluid)

    # State 1: superheated vapor at compressor inlet
    T1 = T_evap_K + superheat_C
    h1 = PropsSI("H", "T", T1, "P", P_evap, fluid)
    s1 = PropsSI("S", "T", T1, "P", P_evap, fluid)

    # State 2s: ideal isentropic compressor outlet
    h2s = PropsSI("H", "P", P_cond, "S", s1, fluid)
    s2s = s1

    # State 2: real compressor outlet
    h2 = h1 + (h2s - h1) / eta_comp

    # State 3: subcooled liquid leaving condenser
    T3 = T_cond_K - subcool_C
    h3 = PropsSI("H", "T", T3, "P", P_cond, fluid)

    # State 4: after expansion valve, h4 = h3
    h4 = h3

    T1_C = T1 - 273.15
    T2_C = _safe_propssi(
        "T",
        "P",
        P_cond,
        "H",
        h2,
        fluid,
        warnings,
        "real compressor outlet temperature",
    )
    if T2_C is not None:
        T2_C -= 273.15

    T2s_C = _safe_propssi(
        "T",
        "P",
        P_cond,
        "H",
        h2s,
        fluid,
        warnings,
        "ideal compressor outlet temperature",
    )
    if T2s_C is not None:
        T2s_C -= 273.15

    T3_C = T3 - 273.15
    T4_C = _safe_propssi(
        "T",
        "P",
        P_evap,
        "H",
        h4,
        fluid,
        warnings,
        "expansion valve outlet temperature",
    )
    if T4_C is None:
        T4_C = T_evap_C
        warnings.append(
            "State 4 temperature approximated as evaporator saturation temperature."
        )
    else:
        T4_C -= 273.15

    s2 = _safe_propssi(
        "S",
        "P",
        P_cond,
        "H",
        h2,
        fluid,
        warnings,
        "real compressor outlet entropy",
    )
    s3 = _safe_propssi(
        "S",
        "P",
        P_cond,
        "H",
        h3,
        fluid,
        warnings,
        "condenser outlet entropy",
    )
    s4 = _safe_propssi(
        "S",
        "P",
        P_evap,
        "H",
        h4,
        fluid,
        warnings,
        "expansion valve outlet entropy",
    )
    x4_quality = _safe_propssi(
        "Q",
        "P",
        P_evap,
        "H",
        h4,
        fluid,
        warnings,
        "expansion valve outlet vapor quality",
    )

    # Performance calculations
    cooling_effect = h1 - h4
    compressor_work = h2 - h1
    cop = cooling_effect / compressor_work
    pressure_ratio = P_cond / P_evap
    valid = True

    if T2_C is not None:
        if T2_C >= 100:
            warnings.append(
                "High discharge temperature screening warning: compressor outlet "
                "temperature exceeds 100°C. This is a generic screening threshold, "
                "not a manufacturer compressor-envelope check."
            )
        if T2_C >= 120:
            warnings.append(
                "Severe discharge temperature screening warning: compressor "
                "outlet temperature exceeds 120°C. Real compressor operation "
                "should be checked against manufacturer limits."
            )

    if cop <= 0:
        warnings.append(
            "Calculated COP is less than or equal to zero; the result is not "
            "physically meaningful."
        )
        valid = False

    if pressure_ratio > 5:
        warnings.append(
            "Pressure ratio caution warning: pressure ratio exceeds 5. This is "
            "a generic screening threshold, not a compressor-envelope check."
        )

    if pressure_ratio > 8:
        warnings.append(
            "Severe pressure ratio warning: pressure ratio exceeds 8. Real "
            "compressor operation should be checked against manufacturer limits."
        )

    if cooling_effect <= 0:
        warnings.append(
            "Calculated cooling effect is less than or equal to zero; the "
            "cycle is not providing useful refrigeration."
        )
        valid = False

    return {
        "fluid": fluid,
        "T_evap_C": T_evap_C,
        "T_cond_C": T_cond_C,
        "Tcrit_C": validation["Tcrit_C"],
        "critical_margin_C": validation["critical_margin_C"],
        "T1_C": T1_C,
        "T2_C": T2_C,
        "T2s_C": T2s_C,
        "T3_C": T3_C,
        "T4_C": T4_C,
        "discharge_temp_C": T2_C,
        "COP": cop,
        "cooling_effect_kJ_kg": cooling_effect / 1000,
        "compressor_work_kJ_kg": compressor_work / 1000,
        "P_evap_kPa": P_evap / 1000,
        "P_cond_kPa": P_cond / 1000,
        "pressure_ratio": pressure_ratio,
        "h1_kJ_kg": h1 / 1000,
        "h2_kJ_kg": h2 / 1000,
        "h2s_kJ_kg": h2s / 1000,
        "h3_kJ_kg": h3 / 1000,
        "h4_kJ_kg": h4 / 1000,
        "s1_kJ_kgK": s1 / 1000,
        "s2s_kJ_kgK": s2s / 1000,
        "s2_kJ_kgK": None if s2 is None else s2 / 1000,
        "s3_kJ_kgK": None if s3 is None else s3 / 1000,
        "s4_kJ_kgK": None if s4 is None else s4 / 1000,
        "x4_quality": x4_quality,
        "warnings": warnings,
        "valid": valid,
    }


if __name__ == "__main__":
    results = vapor_compression_cycle(
        fluid="R134a",
        T_evap_C=DEFAULT_EVAPORATOR_TEMP_C,
        T_cond_C=50,
        superheat_C=DEFAULT_SUPERHEAT_C,
        subcool_C=DEFAULT_SUBCOOLING_C,
        eta_comp=DEFAULT_COMPRESSOR_EFFICIENCY,
    )

    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
