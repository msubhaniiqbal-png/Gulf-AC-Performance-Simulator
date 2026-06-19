from CoolProp.CoolProp import PropsSI
import psychrolib
import streamlit as st
import pandas as pd
import numpy as np

fluid = "R134a"

T_evap = 10 + 273.15
P_evap = PropsSI("P", "T", T_evap, "Q", 1, fluid)

print("CoolProp works.")
print(f"R134a saturation pressure at 10°C: {P_evap/1000:.2f} kPa")

psychrolib.SetUnitSystem(psychrolib.SI)
print("PsychroLib works.")

print("pandas version:", pd.__version__)
print("numpy version:", np.__version__)



