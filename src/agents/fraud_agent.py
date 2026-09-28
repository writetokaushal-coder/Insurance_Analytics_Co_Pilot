from copy import deepcopy

from src.services.fraud_service import assess_fraud
from src.services.human_review_service import queue_review_if_required


def handle_fraud(claim_data: dict):
    payload = deepcopy(claim_data)

    claim_id = payload.pop("CLAIM_ID", None)

    if not claim_id:
        raise ValueError(
            "CLAIM_ID is required for fraud workflow tracking."
        )

    result = assess_fraud(payload)

    prediction = result.get("prediction", {})
    decision = result.get("decision", {})

    review_id = queue_review_if_required(
        domain="FRAUD",
        entity_id=str(claim_id),
        requested_action="fraud_investigation",
        decision=decision,
        ai_recommendation=decision.get(
            "recommended_action",
            "Fraud investigation",
        ),
        ai_score=prediction.get(
            "fraud_probability"
        ),
    )

    result["claim_id"] = claim_id
    result["human_review_id"] = review_id

    return {
        "agent": "fraud",
        "status": "completed",
        "result": result,
    }
