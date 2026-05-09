import pandas as pd

from predict_problem import predict_problem
from rag_engine import RAGEngine
from cost_analyzer import analyze_costs


DATASET_PATH = "data/cooling_dataset.csv"


def load_sample_from_dataset(row_index: int = 0):
    df = pd.read_csv(DATASET_PATH)

    row = df.iloc[row_index]

    input_data = {
        "Timestamp_Hour": row["Timestamp_Hour"],
        "Operator": row["Operator"],
        "Location": row["Location"],
        "Ambient_Temp_C": row["Ambient_Temp_C"],
        "Ambient_Hum_Pct": row["Ambient_Hum_Pct"],
        "IT_Load_kW": row["IT_Load_kW"],
        "Fan_Speed_Pct": row["Fan_Speed_Pct"],
        "Chiller_Status": row["Chiller_Status"],
        "Cold_Aisle_Temp": row["Cold_Aisle_Temp"],
        "Hot_Aisle_Temp": row["Hot_Aisle_Temp"],
        "Rack_Inlet_Temp": row["Rack_Inlet_Temp"],
        "HVAC_Power_kW": row["HVAC_Power_kW"],
        "PUE": row["PUE"]
    }

    real_label = row["Efficiency_Label"]

    return input_data, real_label


def main():
    input_data, real_label = load_sample_from_dataset(row_index=259)

    prediction = predict_problem(input_data)

    predicted_label = prediction["label"]
    confidence = prediction["confidence"]

    rag = RAGEngine()
    solutions = rag.retrieve_solution(predicted_label, input_data)

    solution = solutions[0]

    cost_analysis = analyze_costs(input_data, solution)

    print("\n=== INPUT DATA ===")
    for key, value in input_data.items():
        print(f"{key}: {value}")

    print("\n=== AI 1: PROBLEM CLASSIFICATION ===")
    print(f"Real dataset label: {real_label}")
    print(f"Predicted label: {predicted_label}")
    print(f"Model confidence: {confidence}")

    print("\n=== AI 2: RAG RECOMMENDATION ===")
    print(f"Title: {solution['title']}")
    print(f"Risk level: {solution['risk_level']}")
    print(f"Description: {solution['content']}")

    print("\nRecommended actions:")
    for action in solution["recommended_actions"]:
        print(f"- {action}")

    print("\nExpected impact:")
    print(solution["expected_impact"])

    print("\n=== COST AND SUSTAINABILITY ANALYSIS ===")
    print(f"Location: {cost_analysis['location']}")
    print(f"Energy price: {cost_analysis['energy_price_eur_per_kwh']} EUR/kWh")
    print(f"Carbon intensity: {cost_analysis['carbon_intensity_gco2_per_kwh']} gCO2/kWh")

    print(f"Current hourly HVAC cost: {cost_analysis['current_hourly_cost_eur']} EUR")
    print(f"Current monthly HVAC cost: {cost_analysis['current_monthly_cost_eur']} EUR")

    print(f"Optimized hourly HVAC cost: {cost_analysis['optimized_hourly_cost_eur']} EUR")
    print(f"Optimized monthly HVAC cost: {cost_analysis['optimized_monthly_cost_eur']} EUR")

    print(f"Estimated saving percentage: {cost_analysis['estimated_saving_pct']}%")
    print(f"Estimated monthly savings: {cost_analysis['estimated_monthly_saving_eur']} EUR")

    print(f"Current monthly CO2 emissions: {cost_analysis['current_monthly_co2_kg']} kg")
    print(f"Estimated monthly CO2 reduction: {cost_analysis['estimated_monthly_co2_reduction_kg']} kg")


if __name__ == "__main__":
    main()