import sys
from pathlib import Path
import pandas as pd
import joblib
from src.repositories.renewal_repository import (get_renewal_features)


# Project root
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Add project root to Python path
sys.path.insert(0, str(PROJECT_DIR))


# Import project module
from src.model_features import ALL_FEATURES


MODELS_DIR = PROJECT_DIR / "models"
DATA_DIR = PROJECT_DIR / "data" / "curated"


# -----------------------------------
# Model paths
# -----------------------------------

MODEL_PATH = MODELS_DIR / "renewal_xgboost_model.joblib"
THRESHOLD_PATH = MODELS_DIR / "renewal_churn_threshold.joblib"


# -----------------------------------
# Load model and threshold
# -----------------------------------

renewal_model = joblib.load(MODEL_PATH)
renewal_threshold = joblib.load(THRESHOLD_PATH)


# -----------------------------------
# Load renewal dataset
# -----------------------------------

# renewal_data = pd.read_csv(
#     DATA_DIR / "renewal_model_dataset.csv",
#     low_memory=False
# )


# -----------------------------------
# Risk band function
# -----------------------------------

def get_risk_band(probability):

    medium_cutoff = renewal_threshold / 2

    if probability >= renewal_threshold:
        return "High"

    elif probability >= medium_cutoff:
        return "Medium"

    else:
        return "Low"


# -----------------------------------
# Prediction function
# -----------------------------------
def predict_renewal(policy_id):

    # Get policy data
    policy_row = get_renewal_features(policy_id)

    # Check policy exists
    if policy_row.empty:
        raise ValueError(f"Policy {policy_id} not found.")

    # Check required features
    missing_features = [
        col for col in ALL_FEATURES
        if col not in policy_row.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing model features: {missing_features}"
        )

    # Select model features
    X = policy_row[ALL_FEATURES]

    # Predict non-renewal probability
    probability = float(
        renewal_model.predict_proba(X)[0, 1]
    )

    # High risk flag
    high_risk_flag = int(
        probability >= renewal_threshold
    )

    # Risk band
    risk_band = get_risk_band(probability)

    # Customer id
    customer_id = str(
        policy_row["CUSTOMER_ID"].iloc[0]
    )

    # Final result
    result = {
        "policy_id": policy_id,
        "customer_id": customer_id,
        "non_renewal_probability": round(probability, 4),
        "non_renewal_risk_pct": round(probability * 100, 2),
        "risk_band": risk_band,
        "high_risk_flag": high_risk_flag,
        "threshold": float(renewal_threshold)
    }

    return result




# if __name__ == "__main__":

#     policy_id = renewal_data["POLICY_ID"].iloc[0]

#     result = predict_renewal(policy_id)

#     print(result)