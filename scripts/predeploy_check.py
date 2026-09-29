import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from sqlalchemy import text

PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / ".env")

critical_failures = []
warnings = []

def passed(message):
    print(f"[PASS] {message}")

def failed(message):
    print(f"[FAIL] {message}")
    critical_failures.append(message)

def warn(message):
    print(f"[WARN] {message}")
    warnings.append(message)

print("\nINSURANCE AI COPILOT — PRE-DEPLOY CHECK")
print("=" * 78)

required_files = [
    "models/renewal_xgboost_model.joblib",
    "models/renewal_churn_threshold.joblib",
    "models/fraud_xgboost_model.joblib",
    "models/fraud_threshold.joblib",
    "models/underwriting_xgboost_model.joblib",
    "models/underwriting_label_encoder.joblib",
    "api/main.py",
    "api/production.py",
    "dashboard/streamlit_app.py",
    "src/llm/copilot.py",
    "src/policies/decision_policy.py",
]

for relative_path in required_files:
    if (PROJECT_DIR / relative_path).exists():
        passed(relative_path)
    else:
        failed(f"Missing: {relative_path}")

try:
    from api.production import app
    paths = set(app.openapi()["paths"].keys())
    required_routes = {
        "/health", "/ready", "/version",
        "/portfolio/summary", "/policy/{policy_id}",
        "/predict/renewal/{policy_id}", "/predict/fraud", "/predict/underwriting",
        "/human-review/pending", "/human-review/{review_id}/resolve", "/chat/ai",
    }
    missing = required_routes - paths
    if missing:
        failed(f"Missing API routes: {sorted(missing)}")
    else:
        passed("Required API routes")
except Exception as error:
    failed(f"API import: {error}")

try:
    from src.database import engine
    with engine.connect() as connection:
        value = connection.execute(text("SELECT 1")).scalar()
        if value == 1:
            passed("SQL connection")
        else:
            failed("SQL SELECT 1")

        required_objects = [
            "analytics.policy_360",
            "analytics.human_review_queue",
            "analytics.ai_chat_sessions",
            "analytics.ai_chat_messages",
            "analytics.ai_tool_audit",
        ]
        for object_name in required_objects:
            exists = connection.execute(
                text("SELECT CASE WHEN OBJECT_ID(:object_name) IS NOT NULL THEN 1 ELSE 0 END"),
                {"object_name": object_name},
            ).scalar()
            if exists:
                passed(object_name)
            else:
                failed(f"Missing SQL object: {object_name}")

        rows = connection.execute(text("""
            SELECT POLICY_TYPE, COUNT(*) AS CNT
            FROM analytics.policy_360
            GROUP BY POLICY_TYPE
        """)).mappings().all()
        actual_types = {row["POLICY_TYPE"] for row in rows}
        expected_types = {
            "Health", "Motor", "Term Life", "Commercial",
            "Home", "Personal Accident", "Whole Life", "Travel",
        }
        missing_types = expected_types - actual_types
        if missing_types:
            failed(f"Missing policy types: {sorted(missing_types)}")
        else:
            passed("All 8 policy types present")
except Exception as error:
    failed(f"Database validation: {error}")

ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
expected_model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
try:
    response = requests.get(f"{ollama_url}/api/tags", timeout=10)
    response.raise_for_status()
    names = [item.get("name", "") for item in response.json().get("models", [])]
    if any(expected_model in name for name in names):
        passed(f"Ollama model: {expected_model}")
    else:
        failed(f"Ollama connected but {expected_model} is not installed.")
except Exception as error:
    failed(f"Ollama: {error}")

rag_index = PROJECT_DIR / "rag" / "index" / "knowledge_index.joblib"
if rag_index.exists():
    passed("RAG index")
else:
    warn("RAG index not built. Run: python -m scripts.build_knowledge_index")

gitignore_path = PROJECT_DIR / ".gitignore"
if gitignore_path.exists():
    content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
    if ".env" in content:
        passed(".env ignored by Git")
    else:
        failed(".gitignore does not protect .env")
else:
    failed(".gitignore missing")

env_path = PROJECT_DIR / ".env"
if env_path.exists():
    content = env_path.read_text(encoding="utf-8", errors="ignore")
    if "OPENAI_API_KEY=" in content:
        warn("OPENAI_API_KEY still exists in .env; remove it if Ollama is your only provider.")
    passed(".env exists")
else:
    failed(".env missing")

print("\n" + "=" * 78)
if warnings:
    print(f"Warnings: {len(warnings)}")
if critical_failures:
    print(f"Critical failures: {len(critical_failures)}")
    print("DEPLOYMENT STATUS: NOT READY")
    sys.exit(1)

print("DEPLOYMENT STATUS: READY FOR SMOKE TEST")
print("Next: start api.production:app and run the GUI smoke tests.")
