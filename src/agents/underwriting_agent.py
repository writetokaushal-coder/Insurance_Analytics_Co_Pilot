from copy import deepcopy

from src.services.underwriting_service import assess_underwriting
from src.services.human_review_service import queue_review_if_required


def handle_underwriting(applicant_data: dict):
    payload = deepcopy(applicant_data)

    underwriting_id = payload.pop(
        "UNDERWRITING_ID",
        None,
    )

    result = assess_underwriting(payload)

    prediction = result.get("prediction", {})
    decision = result.get("decision", {})

    entity_id = (
        str(underwriting_id)
        if underwriting_id
        else "NEW_APPLICATION"
    )

    review_id = queue_review_if_required(
        domain="UNDERWRITING",
        entity_id=entity_id,
        requested_action="underwriting_decision",
        decision=decision,
        ai_recommendation=prediction.get(
            "decision",
            "Underwriting review",
        ),
        ai_score=prediction.get(
            "confidence"
        ),
    )

    result["underwriting_id"] = underwriting_id
    result["human_review_id"] = review_id

    return {
        "agent": "underwriting",
        "status": "completed",
        "result": result,
    }
