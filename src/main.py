import os
import pandas as pd
from predict_problem import predict_problem
from rag_engine import RAGEngine
from cost_analyzer import analyze_costs

# Configuration - use absolute paths relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "base_dataset_data_centers.csv")

# Initialize RAG once (heavy operation)
rag_engine = RAGEngine()

def run_optimization_pipeline(location_name: str):
    """
    Main function to run the full AI pipeline for a specific data center location.
    Returns a dictionary with all results or prints them directly.
    """
    try:
        # 1. Load and clean dataset
        df = pd.read_csv(DATASET_PATH)
        df.columns = [c.strip() for c in df.columns] # Clean column names

        # 2. Find the row for the selected location
        location_data = df[df['Location'] == location_name]

        if location_data.empty:
            return {"success": False, "error": f"Location '{location_name}' not found."}

        row = location_data.iloc[0]

        # 3. Map input data with fallbacks (the "bulletproof" mapping)
        input_data = {
            "Timestamp_Hour": row.get("Timestamp_Hour", 12),
            "Operator": row.get("Operator", "Hyperscale Operator"),
            "Location": row.get("Location", location_name),
            "Ambient_Temp_C": row.get("Amb_Temp (°C)", 15.0),
            "Ambient_Hum_Pct": row.get("Amb_Hum_Pct", 50.0),
            "IT_Load_kW": row.get("IT_Load (kW)", 0.0),
            "Fan_Speed_Pct": row.get("Fan_Speed (%)", 0.0),
            "Chiller_Status": row.get("Chiller_Status", 0),
            "PUE": row.get("PUE", 1.0),
            "Rack_Inlet_Temp": row.get("Rack_Inlet (°C)", 22.0),
            
            # Secondary/Calculated fields
            "HVAC_Power_kW": float(row.get("IT_Load (kW)", 0)) * (float(row.get("PUE", 1.1)) - 1.0),
            "Cold_Aisle_Temp": row.get("Rack_Inlet (°C)", 22.0) - 1.5,
            "Hot_Aisle_Temp": row.get("Rack_Inlet (°C)", 22.0) + 15.0
        }

        # 4. AI 1: Classification
        prediction = predict_problem(input_data)
        
        # 5. AI 2: RAG Recommendation
        solution = rag_engine.retrieve_solution(prediction["label"], input_data)[0]

        # 6. Economics Analysis
        cost_analysis = analyze_costs(input_data, solution)

        # 7. Comprehensive Result Object
        results = {
            "success": True,
            "input_snapshot": input_data,
            "prediction": prediction,
            "solution": solution,
            "economics": cost_analysis,
            "real_label": row.get("Label (Expected)", "N/A")
        }

        # Display the detailed results in terminal
        display_formatted_output(results)
        
        return results

    except Exception as e:
        return {"success": False, "error": str(e)}

def display_formatted_output(res):
    """Original detailed print layout you liked."""
    data = res["input_snapshot"]
    pred = res["prediction"]
    sol = res["solution"]
    cost = res["economics"]

    print("\n" + "="*60)
    print(f" PROCESSING DATA CENTER: {data['Location']} ")
    print("="*60)

    print("\n=== INPUT DATA ===")
    for key, value in data.items():
        print(f"{key}: {value}")

    print("\n=== AI 1: PROBLEM CLASSIFICATION ===")
    print(f"Real dataset label: {res['real_label']}")
    print(f"Predicted label: {pred['label']}")
    print(f"Model confidence: {pred['confidence']}")

    print("\n=== AI 2: RAG RECOMMENDATION ===")
    print(f"Title: {sol['title']}")
    print(f"Risk level: {sol['risk_level']}")
    print(f"Description: {sol['content']}")

    print("\nRecommended actions:")
    for action in sol["recommended_actions"]:
        print(f"- {action}")

    print("\nExpected impact:")
    print(sol["expected_impact"])

    print("\n=== COST AND SUSTAINABILITY ANALYSIS ===")
    print(f"Location: {cost['location']}")
    print(f"Current monthly HVAC cost: {cost['current_monthly_cost_eur']} EUR")
    print(f"Estimated monthly savings: {cost['estimated_monthly_saving_eur']} EUR")
    print(f"CO2 reduction: {cost['estimated_monthly_co2_reduction_kg']} kg")
    print("\n" + "="*60)

if __name__ == "__main__":
    # Now it works by just specifying the name!
    # This simulates a click on the map.
    run_optimization_pipeline("Dublin")