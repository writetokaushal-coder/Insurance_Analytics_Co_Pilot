import os
import sys
from pathlib import Path

import requests
from sqlalchemy import text


PROJECT_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)


def ok(message):
    print(f"[OK]      {message}")


def fail(message):
    print(f"[FAILED]  {message}")


def warning(message):
    print(f"[WARNING] {message}")


def check_file(relative_path):
    path = PROJECT_DIR / relative_path

    if path.exists():
        ok(relative_path)
        return True

    fail(relative_path)
    return False


def main():
    print()
    print("INSURANCE AI COPILOT — FINAL PROJECT CHECK")
    print("=" * 72)

    all_ok = True

    required_files = [
        "models/renewal_xgboost_model.joblib",
        "models/renewal_churn_threshold.joblib",
        "models/fraud_xgboost_model.joblib",
        "models/fraud_threshold.joblib",
        "models/underwriting_xgboost_model.joblib",
        "models/underwriting_label_encoder.joblib",
        "api/main.py",
        "api/chat_llm.py",
        "api/insights.py",
        "dashboard/streamlit_app.py",
        "dashboard/api_client.py",
        "src/database.py",
        "src/renewal_predictor.py",
        "src/models/fraud_predictor.py",
        "src/models/underwriting_predictor.py",
        "src/policies/decision_policy.py",
        "src/llm/config.py",
        "src/llm/copilot.py",
        "src/llm/tools.py",
    ]

    print()
    print("1. FILE CHECK")
    print("-" * 72)

    for item in required_files:
        if not check_file(item):
            all_ok = False

    print()
    print("2. API ROUTE CHECK")
    print("-" * 72)

    try:
        from api.main import app

        routes = set(
            app.openapi()["paths"].keys()
        )

        expected_routes = {
            "/",
            "/health",
            "/predict/renewal/{policy_id}",
            "/predict/fraud",
            "/predict/underwriting",
            "/human-review/pending",
            "/human-review/{review_id}/resolve",
            "/chat/ai",
            "/portfolio/summary",
            "/policy/{policy_id}",
        }

        for route in sorted(expected_routes):
            if route in routes:
                ok(route)
            else:
                fail(route)
                all_ok = False

    except Exception as error:
        fail(
            f"Could not load FastAPI routes: {error}"
        )
        all_ok = False

    print()
    print("3. DATABASE CHECK")
    print("-" * 72)

    try:
        from src.database import engine

        with engine.connect() as connection:
            value = connection.execute(
                text("SELECT 1")
            ).scalar()

        if value == 1:
            ok("SQL Server connection")
        else:
            fail("Unexpected SQL response")
            all_ok = False

    except Exception as error:
        fail(
            f"SQL Server connection: {error}"
        )
        all_ok = False

    print()
    print("4. POLICY 360 CHECK")
    print("-" * 72)

    try:
        from src.repositories.policy_repository import (
            get_portfolio_summary
        )

        summary = get_portfolio_summary()

        if summary.get("TOTAL_POLICIES"):
            ok(
                "Policy 360 portfolio summary "
                f"({summary['TOTAL_POLICIES']} policies)"
            )
        else:
            fail("Policy 360 returned no policies")
            all_ok = False

    except Exception as error:
        fail(
            f"Policy 360: {error}"
        )
        all_ok = False

    print()
    print("5. OLLAMA CHECK")
    print("-" * 72)

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434"
    )

    try:
        response = requests.get(
            f"{base_url}/api/tags",
            timeout=10,
        )

        response.raise_for_status()
        payload = response.json()

        model_names = [
            item.get("name", "")
            for item in payload.get("models", [])
        ]

        if model_names:
            ok("Ollama API")
            print(
                "          Models:",
                ", ".join(model_names)
            )
        else:
            warning(
                "Ollama connected but no models found"
            )

    except Exception as error:
        fail(
            f"Ollama: {error}"
        )
        all_ok = False

    print()
    print("6. ENVIRONMENT CHECK")
    print("-" * 72)

    env_path = PROJECT_DIR / ".env"

    if env_path.exists():
        ok(".env exists")

        env_text = env_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if "OPENAI_API_KEY=" in env_text:
            warning(
                "OPENAI_API_KEY still exists in .env. "
                "Remove it if Ollama is your only provider."
            )
    else:
        fail(".env not found")
        all_ok = False

    print()
    print("=" * 72)

    if all_ok:
        print(
            "FINAL RESULT: CORE PROJECT CHECK PASSED"
        )
        print()
        print(
            "The project is ready for final UI testing "
            "and repository cleanup."
        )
    else:
        print(
            "FINAL RESULT: SOME CHECKS FAILED"
        )
        print()
        print(
            "Fix the failed checks before deployment."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
