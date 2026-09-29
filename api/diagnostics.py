import os
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from src.database import engine

router = APIRouter(tags=["diagnostics"])
PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_FILES = [
    "renewal_xgboost_model.joblib",
    "renewal_churn_threshold.joblib",
    "fraud_xgboost_model.joblib",
    "fraud_threshold.joblib",
    "underwriting_xgboost_model.joblib",
    "underwriting_label_encoder.joblib",
]

@router.get("/ready")
def readiness():
    checks = {}
    ready = True

    try:
        with engine.connect() as connection:
            value = connection.execute(text("SELECT 1")).scalar()
        checks["database"] = "healthy" if value == 1 else "unhealthy"
        ready = ready and value == 1
    except Exception as error:
        checks["database"] = f"error: {error}"
        ready = False

    missing_models = [
        name for name in MODEL_FILES
        if not (PROJECT_DIR / "models" / name).exists()
    ]
    if missing_models:
        checks["models"] = {"status": "missing", "files": missing_models}
        ready = False
    else:
        checks["models"] = "healthy"

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        checks["ollama"] = "healthy"
    except Exception as error:
        checks["ollama"] = f"error: {error}"
        ready = False

    rag_index = PROJECT_DIR / "rag" / "index" / "knowledge_index.joblib"
    checks["rag_index"] = "ready" if rag_index.exists() else "not_built"

    payload = {"ready": ready, "checks": checks}
    if not ready:
        raise HTTPException(status_code=503, detail=payload)
    return payload

@router.get("/version")
def version():
    return {
        "name": "Insurance AI Copilot",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("APP_ENV", "development"),
    }
