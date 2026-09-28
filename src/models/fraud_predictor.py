import pandas as pd
import joblib
from pathlib import Path


# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_DIR / "models"


# Model files
MODEL_PATH = MODELS_DIR / "fraud_xgboost_model.joblib"
THRESHOLD_PATH = MODELS_DIR / "fraud_threshold.joblib"


# Load model
fraud_model = joblib.load(MODEL_PATH)

# Load threshold
fraud_threshold = joblib.load(THRESHOLD_PATH)


# Get model feature names
if hasattr(fraud_model, "feature_names_in_"):
    FRAUD_FEATURES = list(fraud_model.feature_names_in_)
else:
    FRAUD_FEATURES = None


# Fraud prediction function
def predict_fraud(claim_data):

    # Convert input dictionary to DataFrame
    input_df = pd.DataFrame([claim_data])

    # Check required model features
    if FRAUD_FEATURES is not None:

        missing_features = [
            col for col in FRAUD_FEATURES
            if col not in input_df.columns
        ]

        if missing_features:
            raise ValueError(
                f"Missing fraud model features: {missing_features}"
            )

        # Keep only model features
        input_df = input_df[FRAUD_FEATURES]

    # Predict fraud probability
    fraud_probability = float(
        fraud_model.predict_proba(input_df)[0, 1]
    )

    # Apply threshold
    fraud_flag = int(
        fraud_probability >= fraud_threshold
    )

    # Create label
    if fraud_flag == 1:
        prediction = "Fraud Risk"
    else:
        prediction = "No Fraud Alert"

    # Final result
    result = {
        "fraud_probability": round(fraud_probability, 4),
        "fraud_risk_pct": round(fraud_probability * 100, 2),
        "prediction": prediction,
        "fraud_flag": fraud_flag,
        "threshold": float(fraud_threshold)
    }

    return result