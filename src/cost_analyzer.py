import os
import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENERGY_PRICES_PATH = os.path.join(PROJECT_ROOT, "data", "energy_prices.csv")


def analyze_costs(input_data: dict, solution: dict):
    prices_df = pd.read_csv(ENERGY_PRICES_PATH)

    location = input_data["Location"]

    row = prices_df[prices_df["Location"] == location]

    if row.empty:
        raise ValueError(f"No energy price data found for location: {location}")

    energy_price = float(row.iloc[0]["Energy_Price_EUR_per_kWh"])
    carbon_intensity = float(row.iloc[0]["Carbon_Intensity_gCO2_per_kWh"])

    hvac_power = float(input_data["HVAC_Power_kW"])

    hourly_cost = hvac_power * energy_price
    daily_cost = hourly_cost * 24
    monthly_cost = daily_cost * 30

    hourly_co2_kg = hvac_power * carbon_intensity / 1000
    monthly_co2_kg = hourly_co2_kg * 24 * 30

    saving_pct = float(solution.get("estimated_saving_pct", 0))

    estimated_hourly_saving = hourly_cost * saving_pct / 100
    estimated_monthly_saving = monthly_cost * saving_pct / 100
    estimated_monthly_co2_reduction = monthly_co2_kg * saving_pct / 100

    optimized_hourly_cost = hourly_cost - estimated_hourly_saving
    optimized_monthly_cost = monthly_cost - estimated_monthly_saving

    return {
        "location": location,
        "energy_price_eur_per_kwh": energy_price,
        "carbon_intensity_gco2_per_kwh": carbon_intensity,
        "current_hourly_cost_eur": round(hourly_cost, 2),
        "current_monthly_cost_eur": round(monthly_cost, 2),
        "optimized_hourly_cost_eur": round(optimized_hourly_cost, 2),
        "optimized_monthly_cost_eur": round(optimized_monthly_cost, 2),
        "estimated_saving_pct": saving_pct,
        "estimated_monthly_saving_eur": round(estimated_monthly_saving, 2),
        "current_monthly_co2_kg": round(monthly_co2_kg, 2),
        "estimated_monthly_co2_reduction_kg": round(estimated_monthly_co2_reduction, 2)
    }