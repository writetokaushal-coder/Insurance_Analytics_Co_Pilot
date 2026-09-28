import pandas as pd
import numpy as np
import joblib

from pathlib import Path


# -----------------------------------
# Project paths
# -----------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_DIR / "models"


# -----------------------------------
# Load trained artifacts once
# -----------------------------------

MODEL_PATH = (
    MODELS_DIR
    / "underwriting_xgboost_model.joblib"
)

ENCODER_PATH = (
    MODELS_DIR
    / "underwriting_label_encoder.joblib"
)


underwriting_model = joblib.load(
    MODEL_PATH
)

underwriting_label_encoder = joblib.load(
    ENCODER_PATH
)


# -----------------------------------
# Recover model input schema
# -----------------------------------

if hasattr(
    underwriting_model,
    "feature_names_in_"
):
    UNDERWRITING_FEATURES = list(
        underwriting_model.feature_names_in_
    )
else:
    UNDERWRITING_FEATURES = [
        "AGE",
        "HEALTH_SCORE",
        "BMI",
        "CREDIT_SCORE",
        "LIFESTYLE",
        "MEDICAL_HISTORY_FLAG",
        "SMOKER_FLAG",
        "OCCUPATION_RISK",
    ]


# -----------------------------------
# Prediction
# -----------------------------------

def predict_underwriting(
    applicant_data: dict
):

    input_df = pd.DataFrame(
        [applicant_data]
    )

    missing_features = [
        col
        for col in UNDERWRITING_FEATURES
        if col not in input_df.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing underwriting features: "
            f"{missing_features}"
        )

    X = input_df[
        UNDERWRITING_FEATURES
    ]

    probabilities = (
        underwriting_model
        .predict_proba(X)[0]
    )

    predicted_class = int(
        np.argmax(
            probabilities
        )
    )

    decision = (
        underwriting_label_encoder
        .inverse_transform(
            [predicted_class]
        )[0]
    )

    probability_dict = {
        str(class_name):
            round(
                float(probability),
                4
            )

        for class_name, probability
        in zip(
            underwriting_label_encoder.classes_,
            probabilities
        )
    }

    confidence = float(
        probabilities[
            predicted_class
        ]
    )

    return {
        "decision":
            str(decision),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "probabilities":
            probability_dict,
    }
