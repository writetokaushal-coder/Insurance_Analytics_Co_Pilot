from pathlib import Path


PROJECT_DIR = Path(
    __file__
).resolve().parent


required_files = [

    # -----------------------------------
    # ML artifacts
    # -----------------------------------
    "models/renewal_xgboost_model.joblib",
    "models/renewal_churn_threshold.joblib",

    "models/fraud_xgboost_model.joblib",
    "models/fraud_threshold.joblib",

    "models/underwriting_xgboost_model.joblib",
    "models/underwriting_label_encoder.joblib",


    # -----------------------------------
    # Curated model data
    # -----------------------------------
    "data/curated/renewal_model_dataset.csv",
    "data/curated/fraud_model_dataset.csv",
    "data/curated/underwriting_model_dataset.csv",


    # -----------------------------------
    # Predictors
    # -----------------------------------
    "src/renewal_predictor.py",
    "src/models/fraud_predictor.py",
    "src/models/underwriting_predictor.py",


    # -----------------------------------
    # Database / repositories
    # -----------------------------------
    "src/database.py",
    "src/repositories/renewal_repository.py",
    "src/repositories/human_review_repository.py",


    # -----------------------------------
    # Services
    # -----------------------------------
    "src/services/renewal_service.py",
    "src/services/fraud_service.py",
    "src/services/underwriting_service.py",
    "src/services/human_review_service.py",


    # -----------------------------------
    # Guardrails
    # -----------------------------------
    "src/policies/decision_policy.py",


    # -----------------------------------
    # API
    # -----------------------------------
    "api/__init__.py",
    "api/main.py",
    "api/schemas.py",


    # -----------------------------------
    # Human review SQL
    # -----------------------------------
    "sql/03_human_review_queue.sql",


    # -----------------------------------
    # Feature sync
    # -----------------------------------
    "scripts/sync_ml_feature_tables.py",


    # -----------------------------------
    # Configuration
    # -----------------------------------
    ".env",
    ".gitignore",
]


print()
print(
    "INSURANCE AI COPILOT PROJECT AUDIT"
)

print(
    "=" * 70
)


missing = []


for relative_path in required_files:

    path = (
        PROJECT_DIR
        / relative_path
    )

    if path.exists():

        print(
            f"[OK]      {relative_path}"
        )

    else:

        print(
            f"[MISSING] {relative_path}"
        )

        missing.append(
            relative_path
        )


print()
print(
    "=" * 70
)


if missing:

    print(
        f"Missing items: {len(missing)}"
    )

    print()
    print(
        "Fix the missing items before "
        "starting the agentic AI layer."
    )

else:

    print(
        "ALL REQUIRED APPLICATION-LAYER "
        "FILES EXIST."
    )

    print()
    print(
        "Next checkpoint: run SQL human-review "
        "table setup, sync ML features, then "
        "start FastAPI smoke testing."
    )
