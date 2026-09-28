from pathlib import Path

PROJECT_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)

EXPECTED_ARTIFACTS = [
    "models/renewal_xgboost_model.joblib",
    "models/renewal_churn_threshold.joblib",
    "models/fraud_xgboost_model.joblib",
    "models/fraud_threshold.joblib",
    "models/underwriting_xgboost_model.joblib",
    "models/underwriting_label_encoder.joblib",
]


def test_model_artifacts_exist():
    missing = []

    for relative_path in EXPECTED_ARTIFACTS:
        path = PROJECT_DIR / relative_path

        if not path.exists():
            missing.append(relative_path)

    assert not missing, (
        f"Missing model artifacts: {missing}"
    )
