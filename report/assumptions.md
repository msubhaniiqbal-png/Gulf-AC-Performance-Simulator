# Model Assumptions

This project uses simplified engineering assumptions to estimate AC and HVAC
performance degradation under Gulf high ambient conditions. The outputs
should be treated as indicative simulation results, not certified equipment
ratings or official cost estimates.

## Sensitivity Simulator Scope

This project is intended to show trends and relative changes in AC performance.
It should not be used for final equipment selection, procurement, compliance,
or design decisions without real manufacturer data and field validation.

| Assumption | Example |
| --- | --- |
| Condenser approach | Condenser temperature is estimated as outdoor temperature + 10°C |
| Evaporator temperature | Evaporator temperature is fixed at 10°C |
| Compressor efficiency | Compressor isentropic efficiency is assumed to be 70% |
| Dust fouling severity index | Dust fouling is modeled as an assumed effective condenser temperature increase |
| Tariff | Electricity tariff is a placeholder unless verified from an official source |
| Cooling load | Cooling load is assumed constant in the cost model |

## Dust Fouling Severity Assumption

The fouling severity index is a scenario index, not a measured physical
percentage of dust mass, fin blockage, or UA loss. In the current model:

- index 0 = clean condenser scenario
- index 10 = mild/moderate degradation scenario
- index 20 = severe degradation scenario
- index 30 = extreme degradation scenario

The current model approximates dust fouling by increasing the effective
condenser temperature. This represents the idea that a dirtier condenser
rejects heat less effectively, forcing the system to operate at a higher
condensing temperature.

This assumption is useful for sensitivity analysis, but it should not be
interpreted as field-calibrated performance degradation.

## Fixed Evaporator Temperature Assumption

The evaporator temperature is fixed as a simplifying control assumption. This
allows the model to isolate condenser-side effects caused by outdoor heat,
condenser approach temperature, refrigerant selection, and dust fouling
severity.

In real AC systems, evaporator temperature may vary with indoor load, humidity,
refrigerant charge, airflow, superheat control, and equipment design.

## Practical Wattage Model Assumption

The practical wattage estimator uses AC tonnage, EER, duty cycle, outdoor
temperature, and simplified temperature/fouling multipliers. These multipliers
are scenario assumptions, not manufacturer performance curves.

The wattage model is included to estimate practical cost scenarios, while the
CoolProp model is included to study thermodynamic sensitivity. The two models
are related but not physically coupled.

## Critical Temperature Screening

The model checks whether the condenser temperature approaches or exceeds the
selected refrigerant's critical temperature. Results near the critical point are
treated as caution or severe screening cases because small changes in condition
can strongly affect the idealized cycle calculation.

This screening is not a replacement for manufacturer operating envelopes,
compressor maps, refrigerant safety guidance, or equipment-specific limits.

These assumptions are intended to make the first version transparent and easy
to adjust. Future versions can replace them with manufacturer data, measured
power consumption, local tariff schedules, or calibrated field observations.

## Future Work

Potential future improvements include:

- humidity and latent load modeling
- calibrated condenser fouling or UA degradation model
- manufacturer performance curve comparison
- compressor map or operating envelope checks
- annual weather-based Doha simulation
- P-h or T-s cycle diagrams

These are potential improvements, not current project features.
