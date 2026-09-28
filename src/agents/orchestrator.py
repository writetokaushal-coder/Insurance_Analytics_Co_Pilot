import re

from src.agents.router import detect_intent
from src.agents.general_agent import (
    handle_general,
    handle_clarification,
)
from src.agents.renewal_agent import handle_renewal
from src.agents.fraud_agent import handle_fraud
from src.agents.underwriting_agent import handle_underwriting


def extract_policy_id(message: str):
    match = re.search(
        r"\b(?:POL|POLICY)[-_ ]?\d+\b",
        message,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    value = (
        match.group(0)
        .upper()
        .replace("POLICY", "POL")
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )

    return value


def run_orchestrator(
    message: str,
    policy_id: str = None,
    claim_data: dict = None,
    applicant_data: dict = None,
):
    route = detect_intent(message)
    intent = route["intent"]

    if intent == "clarification":
        return {
            "intent": intent,
            "routing": route,
            "response": handle_clarification(
                route.get("candidate_intents", [])
            ),
        }

    if intent == "general":
        return {
            "intent": intent,
            "routing": route,
            "response": handle_general(message),
        }

    if intent == "renewal":
        resolved_policy_id = (
            policy_id
            or extract_policy_id(message)
        )

        if not resolved_policy_id:
            return {
                "intent": "renewal",
                "routing": route,
                "response": {
                    "agent": "renewal",
                    "status": "needs_input",
                    "required_fields": ["policy_id"],
                    "message": (
                        "Please provide the policy ID "
                        "so I can assess renewal risk."
                    ),
                },
            }

        return {
            "intent": "renewal",
            "routing": route,
            "response": handle_renewal(
                resolved_policy_id
            ),
        }

    if intent == "fraud":
        if not claim_data:
            return {
                "intent": "fraud",
                "routing": route,
                "response": {
                    "agent": "fraud",
                    "status": "needs_input",
                    "required_fields": [
                        "CLAIM_ID",
                        "fraud model input fields",
                    ],
                    "message": (
                        "Please provide the claim information "
                        "required for fraud screening. "
                        "I will treat the result as an "
                        "investigation signal, not proof of fraud."
                    ),
                },
            }

        return {
            "intent": "fraud",
            "routing": route,
            "response": handle_fraud(
                claim_data
            ),
        }

    if intent == "underwriting":
        if not applicant_data:
            return {
                "intent": "underwriting",
                "routing": route,
                "response": {
                    "agent": "underwriting",
                    "status": "needs_input",
                    "required_fields": [
                        "AGE",
                        "HEALTH_SCORE",
                        "BMI",
                        "CREDIT_SCORE",
                        "LIFESTYLE",
                        "MEDICAL_HISTORY_FLAG",
                        "SMOKER_FLAG",
                        "OCCUPATION_RISK",
                    ],
                    "message": (
                        "Please provide the applicant risk "
                        "information so I can run underwriting "
                        "decision support."
                    ),
                },
            }

        return {
            "intent": "underwriting",
            "routing": route,
            "response": handle_underwriting(
                applicant_data
            ),
        }

    return {
        "intent": "general",
        "routing": route,
        "response": handle_general(message),
    }
