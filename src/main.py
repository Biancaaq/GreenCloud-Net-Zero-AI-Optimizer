from predict_problem import predict_problem
from rag_engine import RAGEngine


def main():
    input_data = {
        "Timestamp_Hour": 14,
        "Operator": "Operator_A",
        "Location": "Bucharest",
        "Ambient_Temp_C": 32.5,
        "Ambient_Hum_Pct": 64,
        "IT_Load_kW": 850,
        "Fan_Speed_Pct": 45,
        "Chiller_Status": "ON",
        "Cold_Aisle_Temp": 25.4,
        "Hot_Aisle_Temp": 39.1,
        "Rack_Inlet_Temp": 31.0,
        "HVAC_Power_kW": 320,
        "PUE": 1.72
    }

    prediction = predict_problem(input_data)

    label = prediction["label"]
    confidence = prediction["confidence"]

    rag = RAGEngine()
    solutions = rag.retrieve_solution(label, input_data)

    print("\n=== AI 1: Clasificare problemă ===")
    print(f"Label detectat: {label}")
    print(f"Încredere model: {confidence}")

    print("\n=== AI 2: RAG - Soluție recomandată ===")
    for solution in solutions:
        print(f"\nTitlu: {solution['title']}")
        print(f"Soluție: {solution['content']}")


if __name__ == "__main__":
    main()