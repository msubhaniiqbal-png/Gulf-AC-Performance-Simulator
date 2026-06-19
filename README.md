# Gulf AC Performance Sensitivity Simulator

A Python and Streamlit-based HVAC sensitivity simulator that combines an
idealized vapor-compression cycle model with a practical AC wattage and cost
estimator for Gulf high-ambient and dust-fouling scenarios.

## Model Scope

This project is a sensitivity simulator, not a manufacturer-calibrated AC
prediction tool.

It is designed to study how changes in outdoor temperature, condenser approach
temperature, refrigerant choice, simplified dust fouling severity, EER, duty
cycle, and AC type affect estimated COP, compressor work, wattage, and monthly
cost.

The results should be interpreted as engineering trends, not exact equipment
predictions. The model does not include manufacturer performance curves,
measured field data, compressor maps, humidity/latent load modeling, or
calibrated condenser UA degradation.

## Why This Project Matters

Cooling demand is a major energy driver across Qatar and the wider Gulf region.
High outdoor temperatures can significantly reduce AC performance, while dust
and condenser fouling can reduce heat rejection and increase electricity use.
This project connects simplified thermodynamic analysis with practical power and
monthly cost estimates, helping show how operating conditions affect both HVAC
performance and energy cost.

## What The Project Does

- CoolProp vapor-compression cycle model
- COP, compressor work, cooling effect, and pressure ratio calculation
- State-point temperatures, enthalpies, and entropies
- Discharge temperature screening
- Critical temperature margin warnings
- Refrigerant comparison
- Dust fouling severity analysis
- AC tonnage-to-wattage estimator
- Inverter and non-inverter practical power estimation
- kWh and monthly QAR cost estimation
- Streamlit dashboard

## Methodology

The project has two complementary but independent estimation modes.

The idealized thermodynamic cycle uses CoolProp to evaluate a simplified
vapor-compression refrigeration cycle. Condenser temperature is estimated as:

```text
condenser temperature = outdoor temperature + condenser approach + fouling penalty
```

The practical wattage estimator uses AC tonnage, EER, duty cycle, temperature
multipliers, and fouling multipliers to estimate electrical power and monthly
energy cost. It is not directly coupled to the CoolProp cycle.

## Why There Are Two Models

This project contains two related but separate modeling tracks.

### 1. Thermodynamic Cycle Model

The CoolProp-based vapor-compression model calculates refrigerant cycle
behavior. It estimates COP, compressor work, pressure ratio, discharge
temperature, and critical temperature margin.

This model is useful for understanding how condenser temperature, refrigerant
choice, and fouling assumptions affect idealized cycle performance.

### 2. Practical Wattage and Cost Model

The wattage estimator starts from AC tonnage, EER, duty cycle, outdoor
temperature, and fouling severity. It estimates running watts, average watts,
daily energy use, monthly energy use, and monthly cost.

This model is useful for practical cost scenarios, but it is assumption-based
and not manufacturer-calibrated.

The two models are not expected to match exactly because they use different
inputs and answer different questions.

## Key Equations

```text
cooling effect = h1 - h4
compressor work = h2 - h1
COP = cooling effect / compressor work
electrical power = cooling load / COP
cooling capacity = tons x 12000 BTU/hr
input watts = BTU/hr / EER
monthly cost = kWh x tariff
```

## Current Outputs

- COP vs outdoor temperature
- Refrigerant comparison
- Critical margin comparison
- Dust fouling COP degradation
- Condenser approach sensitivity
- AC wattage comparison
- Monthly cost comparison

## Assumptions And Limitations

This is a sensitivity simulator, not a calibrated prediction tool. Results
should not be treated as certified equipment ratings, manufacturer performance
data, or official cost estimates.

Current limitations include:

- Not manufacturer-calibrated
- Not field-validated
- Fixed evaporator temperature
- Simplified condenser approach temperature
- Simplified dust fouling severity index
- Placeholder electricity tariff
- Practical wattage model is independent from the CoolProp cycle

## How To Run

Run these commands from the project root:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python src/high_ambient_analysis.py
python src/refrigerant_comparison.py
python src/approach_sensitivity.py
python src/ac_cost_comparison.py
streamlit run app/app.py
```

## Portfolio Value

This project demonstrates thermodynamics, HVAC fundamentals, Python simulation,
engineering assumptions, energy cost analysis, dashboard development, and
Gulf-specific engineering thinking. It is intended as a mechanical engineering
portfolio project and conversation starter for HVAC, facilities, energy, and
cooling-sector roles.

## Future Work

- Humidity and psychrometric model
- Manufacturer performance curve validation
- Measured power data comparison
- Calibrated fouling or UA model
- Qatar weather-file annual simulation
- District cooling or chiller extension
