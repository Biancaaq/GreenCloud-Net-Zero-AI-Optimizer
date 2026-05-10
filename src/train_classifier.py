import pandas as pd
# pyrefly: ignore [missing-import]
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


DATASET_PATH = "data/cooling_data.csv"
MODEL_PATH = "data/models/cooling_classifier.pkl"

TARGET = "Efficiency_Label"

NUMERIC_FEATURES = [
    "Timestamp_Hour",
    "Ambient_Temp_C",
    "Ambient_Hum_Pct",
    "IT_Load_kW",
    "Fan_Speed_Pct"
]

CATEGORICAL_FEATURES = [
    "Operator",
    "Location",
    "Chiller_Status"
]


def main():
    df = pd.read_csv(DATASET_PATH)

    df = df.dropna()

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=10,
        max_depth=5,
        random_state=42,
        class_weight="balanced"
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    print(classification_report(
        y_test,
        predictions,
        target_names=label_encoder.classes_
    ))

    joblib.dump({
        "pipeline": pipeline,
        "label_encoder": label_encoder,
        "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES
    }, MODEL_PATH)

    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()