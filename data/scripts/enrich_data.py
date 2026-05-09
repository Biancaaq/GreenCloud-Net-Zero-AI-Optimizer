import pandas as pd
import numpy as np

df = pd.read_csv("data_centers_europe_incomplete.csv")
print(f"Loaded {len(df)} real data centers.")

# Annual energy consumed by the whole facility (MWh/year)
# = IT capacity × hours in a year × PUE
# PUE > 1 means overhead (cooling, lighting, UPS losses) is included
df["Annual_Energy_MWh"] = (df["IT_Capacity_MW"] * 8760 * df["PUE"]).round(1)

# Annual CO2 emissions (tonnes/year)
# = energy in kWh × carbon intensity of local grid (gCO2/kWh) → convert to tonnes
df["Annual_CO2_tonnes"] = (
    df["Annual_Energy_MWh"] * 1000 *        # MWh → kWh
    df["Grid_Carbon_gCO2_kWh"] /            # × gCO2/kWh
    1_000_000                               # g → tonnes
).round(0)

# CUE — Carbon Usage Effectiveness (kgCO2 per kWh of IT energy consumed)
df["CUE_kgCO2_per_kWh"] = (df["Grid_Carbon_gCO2_kWh"] / 1000).round(4)

# Overhead ratio — fraction of energy that goes to cooling/UPS/lighting, not IT
df["Overhead_Ratio"] = (df["PUE"] - 1).round(3)

# Potential savings if PUE were improved to 1.10 (industry best-practice target)
TARGET_PUE = 1.10
df["Potential_Energy_Saving_MWh"] = np.where(
    df["PUE"] > TARGET_PUE,
    (df["IT_Capacity_MW"] * 8760 * (df["PUE"] - TARGET_PUE)).round(1),
    0
)
df["Potential_CO2_Saving_tonnes"] = (
    df["Potential_Energy_Saving_MWh"] * 1000 *
    df["Grid_Carbon_gCO2_kWh"] /
    1_000_000
).round(0)

df.to_csv("data_centers_enriched.csv", index=False)

print("\n=== Enriched columns added ===")
print("Annual_Energy_MWh, Annual_CO2_tonnes, CUE_kgCO2_per_kWh,")
print("Overhead_Ratio, Potential_Energy_Saving_MWh, Potential_CO2_Saving_tonnes")
print(f"\nSaved to: data_centers_enriched.csv")
print(df[["Operator", "Location", "PUE", "Annual_CO2_tonnes", "Potential_CO2_Saving_tonnes"]].to_string(index=False))