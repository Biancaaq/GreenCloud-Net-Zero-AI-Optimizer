import pandas as pd
import numpy as np

# CONFIGURATION
# Reduced to 720 hours (approx. 1 month) to keep file size manageable for local machines.
# Change to 8760 if a full year is required.
HOURS_TO_SIMULATE = 1000 
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def generate_dc_dataset():
    # List of 15 real-world data center locations and their base configurations
    dc_configs = [
        {'Operator': 'Microsoft', 'Location': 'Gavle', 'Country': 'Sweden', 'Capacity_MW': 120.0, 'Cooling': 'Free'},
        {'Operator': 'Microsoft', 'Location': 'Dublin', 'Country': 'Ireland', 'Capacity_MW': 105.0, 'Cooling': 'Chiller'},
        {'Operator': 'Microsoft', 'Location': 'Middenmeer', 'Country': 'Netherlands', 'Capacity_MW': 70.0, 'Cooling': 'Chiller'},
        {'Operator': 'Google', 'Location': 'Hamina', 'Country': 'Finland', 'Capacity_MW': 140.0, 'Cooling': 'Water'},
        {'Operator': 'Google', 'Location': 'St. Ghislain', 'Country': 'Belgium', 'Capacity_MW': 95.0, 'Cooling': 'Water'},
        {'Operator': 'Equinix', 'Location': 'Frankfurt', 'Country': 'Germany', 'Capacity_MW': 22.0, 'Cooling': 'Chiller'},
        {'Operator': 'Equinix', 'Location': 'Warsaw', 'Country': 'Poland', 'Capacity_MW': 10.5, 'Cooling': 'Chiller'},
        {'Operator': 'Equinix', 'Location': 'London', 'Country': 'UK', 'Capacity_MW': 32.0, 'Cooling': 'Chiller'},
        {'Operator': 'OVHcloud', 'Location': 'Gravelines', 'Country': 'France', 'Capacity_MW': 38.0, 'Cooling': 'Water'},
        {'Operator': 'Digital Realty', 'Location': 'Marseille', 'Country': 'France', 'Capacity_MW': 20.0, 'Cooling': 'Water'},
        {'Operator': 'Meta', 'Location': 'Lulea', 'Country': 'Sweden', 'Capacity_MW': 115.0, 'Cooling': 'Free'},
        {'Operator': 'Orange', 'Location': 'Val-de-Reuil', 'Country': 'France', 'Capacity_MW': 16.5, 'Cooling': 'Free'},
        {'Operator': 'Interxion', 'Location': 'Amsterdam', 'Country': 'Netherlands', 'Capacity_MW': 13.0, 'Cooling': 'Chiller'},
        {'Operator': 'Aruba.it', 'Location': 'Bergamo', 'Country': 'Italy', 'Capacity_MW': 58.0, 'Cooling': 'Chiller'},
        {'Operator': 'Green Mountain', 'Location': 'Stavanger', 'Country': 'Norway', 'Capacity_MW': 24.0, 'Cooling': 'Water'}
    ]

    all_data = []

    for dc in dc_configs:
        # Define climate baseline based on geography
        base_temp = 10 if dc['Country'] in ['Sweden', 'Finland', 'Norway'] else 18
        
        for h in range(HOURS_TO_SIMULATE):
            hour_of_day = h % 24
            
            # 1. External Weather Simulation
            ambient_temp = base_temp + 7 * np.sin(2 * np.pi * hour_of_day / 24) + np.random.normal(0, 3.5)
            ambient_hum = 60 + 15 * np.cos(2 * np.pi * h / 168) + np.random.normal(0, 6)

            # 2. IT Workload Simulation
            workload_factor = 0.25 + 0.65 * np.random.random()
            it_load_kw = dc['Capacity_MW'] * 1000 * workload_factor

            # 3. Cooling Control Logic
            chiller_status = 1 if (ambient_temp > 16 and "Free" not in dc['Cooling']) else 0
            
            if np.random.random() < 0.04:
                chiller_status = 0

            # CHAOS FACTOR: Simulate a suboptimal cooling setting in 15% of cases for ML training
            if np.random.random() < 0.15:
                fan_speed_pct = np.random.uniform(15, 35) # Fans set too low for current load
            else:
                fan_speed_pct = (38 + (workload_factor * 42) + (max(0, ambient_temp - 15) * 2.2))
            
            fan_speed_pct = min(100, max(8, fan_speed_pct))

            # 4. Thermal Dynamics Simulation
            dust_factor = np.random.uniform(1.0, 1.25)
            cold_aisle_temp = 20.0 + np.random.normal(0, 0.8)
            # Heat delta increases significantly if fan speed is insufficient for the IT load
            delta_t = (it_load_kw / (dc['Capacity_MW'] * 1000)) * 24 * (100 / fan_speed_pct) * dust_factor
            hot_aisle_temp = cold_aisle_temp + delta_t
            rack_inlet_temp = cold_aisle_temp + (delta_t * 0.27)

            # 5. Power Consumption & Efficiency (PUE)
            fan_power_kw = (fan_speed_pct**1.85) * 0.42
            chiller_power_kw = (it_load_kw * 0.36) if chiller_status == 1 else (it_load_kw * 0.05)
            hvac_power_kw = fan_power_kw + chiller_power_kw
            pue = (it_load_kw + hvac_power_kw) / it_load_kw

            fuzzy_offset = np.random.normal(0, 0.015)

            # 6. ML Labelling Logic
            if rack_inlet_temp + (fuzzy_offset * 50) > 27.8:
                label = "CRITICAL_OVERHEAT"
            elif pue + fuzzy_offset > 1.46:
                label = "INEFFICIENT_COOLING"
            elif pue + fuzzy_offset > 1.26:
                label = "STABLE"
            else:
                label = "OPTIMAL"

            # Append structured row with all 14 requested columns
            all_data.append({
                "Timestamp_Hour": h,
                "Operator": dc['Operator'],
                "Location": dc['Location'],
                "Ambient_Temp_C": round(ambient_temp, 1),
                "Ambient_Hum_Pct": round(ambient_hum, 1),
                "IT_Load_kW": round(it_load_kw, 2),
                "Fan_Speed_Pct": round(fan_speed_pct, 1),
                "Chiller_Status": chiller_status,
                "Cold_Aisle_Temp": round(cold_aisle_temp, 1),
                "Hot_Aisle_Temp": round(hot_aisle_temp, 1),
                "Rack_Inlet_Temp": round(rack_inlet_temp, 1),
                "HVAC_Power_kW": round(hvac_power_kw, 2),
                "PUE": round(pue, 3),
                "Efficiency_Label": label
            })

    return pd.DataFrame(all_data)

# Execute Generation
df = generate_dc_dataset()

# Save to CSV
output_file = "../cooling_data.csv"
df.to_csv(output_file, index=False)
