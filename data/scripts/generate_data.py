"""
STEP 2 — Generate Synthetic Data
==================================
Input:  data_centers_enriched.csv   (output of step1_enrich.py)
Output: data_centers_ml_ready.csv   (real + synthetic rows, ready for ML)

What it does:
- Takes the 15 enriched real rows as "anchors"
- Generates N synthetic rows per real row by adding realistic noise
- Recalculates all derived columns for each synthetic row
- Exports a combined dataset with real + synthetic rows

How the noise works:
- Each numeric column gets multiplied by a random factor (e.g. ±10%)
- This simulates real-world variation between similar facilities
- Values are clamped to realistic ranges (e.g. PUE never below 1.05)
"""

import pandas as pd
import numpy as np

N_SYNTHETIC_PER_ROW = 100    # 15 real × 5 = 75 synthetic → 90 total
                            # Change to 20 for ~300 rows if needed
RANDOM_SEED = 42
TARGET_PUE = 1.10

df_real = pd.read_csv("data_centers_enriched.csv")
print(f"Loaded {len(df_real)} enriched real rows.")

np.random.seed(RANDOM_SEED)

def recalculate(df):
    """Recalculate all derived columns after noise is applied."""
    df = df.copy()
    df["Annual_Energy_MWh"] = (df["IT_Capacity_MW"] * 8760 * df["PUE"]).round(1)
    df["Annual_CO2_tonnes"] = (
        df["Annual_Energy_MWh"] * 1000 * df["Grid_Carbon_gCO2_kWh"] / 1_000_000
    ).round(0)
    df["CUE_kgCO2_per_kWh"] = (df["Grid_Carbon_gCO2_kWh"] / 1000).round(4)
    df["Overhead_Ratio"] = (df["PUE"] - 1).round(3)
    df["Potential_Energy_Saving_MWh"] = np.where(
        df["PUE"] > TARGET_PUE,
        (df["IT_Capacity_MW"] * 8760 * (df["PUE"] - TARGET_PUE)).round(1),
        0
    )
    df["Potential_CO2_Saving_tonnes"] = (
        df["Potential_Energy_Saving_MWh"] * 1000 *
        df["Grid_Carbon_gCO2_kWh"] / 1_000_000
    ).round(0)
    return df

synthetic_rows = []

for _, row in df_real.iterrows():
    for _ in range(N_SYNTHETIC_PER_ROW):
        new_row = row.copy()

        # Add ±10-15% noise to raw input columns
        new_row["IT_Capacity_MW"] = round(max(0.5,
            row["IT_Capacity_MW"] * np.random.uniform(1.0, 0.2)
        ), 1)

        pue_noise = np.random.uniform(0.95, 1.05)
        new_row["PUE"] = round(max(1.05, min(2.2,
            row["PUE"] * pue_noise
        )), 3)
        new_row["WUE_L_kWh"] = round(max(0.01,
            row["WUE_L_kWh"] * np.random.uniform(0.90, 1.10)
        ), 3)
        new_row["Grid_Carbon_gCO2_kWh"] = round(max(5,
            row["Grid_Carbon_gCO2_kWh"] * np.random.uniform(0.95, 1.05)
        ), 1)

        new_row["Status"] = "synthetic"
        synthetic_rows.append(new_row)

df_synthetic = pd.DataFrame(synthetic_rows)
df_synthetic = recalculate(df_synthetic)

df_combined = pd.concat([df_real, df_synthetic], ignore_index=True)
df_combined = df_combined.round(2)
df_combined.to_csv("data_centers_ml_ready.csv", index=False)

print(f"Generated {len(df_synthetic)} synthetic rows.")
print(f"\n=== Final Dataset ===")
print(f"Real rows     : {len(df_real)}")
print(f"Synthetic rows: {len(df_synthetic)}")
print(f"Total rows    : {len(df_combined)}")
print(f"Columns       : {list(df_combined.columns)}")
print(f"\nSaved to: data_centers_ml_ready.csv")