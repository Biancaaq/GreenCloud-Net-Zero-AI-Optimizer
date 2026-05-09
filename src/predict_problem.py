import pandas as pd
import joblib


MODEL_PATH = "models/cooling_classifier.pkl"


def predict_problem(input_data: dict):
    saved_model = joblib.load(MODEL_PATH)

    pipeline = saved_model["pipeline"]
    label_encoder = saved_model["label_encoder"]
    features = saved_model["features"]

    df_input = pd.DataFrame([input_data])
    df_input = df_input[features]

    prediction = pipeline.predict(df_input)[0]
    probability = pipeline.predict_proba(df_input).max()

    label = label_encoder.inverse_transform([prediction])[0]

    return {
        "label": label,
        "confidence": round(float(probability), 3)
    }