from src.services.renewal_service import assess_renewal
from src.services.human_review_service import queue_review_if_required


def handle_renewal(policy_id: str):
    result = assess_renewal(policy_id)

    prediction = result.get("prediction", {})
    decision = result.get("decision", {})

    review_id = queue_review_if_required(
        domain="RENEWAL",
        entity_id=policy_id,
        requested_action="retention_outreach",
        decision=decision,
        ai_recommendation=decision.get(
            "recommended_action",
            "Retention review",
        ),
        ai_score=prediction.get(
            "non_renewal_probability"
        ),
    )

    result["human_review_id"] = review_id

    return {
        "agent": "renewal",
        "status": "completed",
        "result": result,
    }
