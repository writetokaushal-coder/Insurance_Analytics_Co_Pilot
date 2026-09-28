from src.repositories.human_review_repository import (
    create_review,
    get_pending_reviews,
    resolve_review,
)


def queue_review_if_required(
    domain: str,
    entity_id: str,
    requested_action: str,
    decision: dict,
    ai_recommendation: str,
    ai_score=None,
):

    if not decision.get(
        "human_review_required",
        False,
    ):
        return None

    review_id = create_review(
        domain=domain,
        entity_id=entity_id,
        requested_action=requested_action,
        ai_recommendation=ai_recommendation,
        ai_score=ai_score,
        reason=decision.get(
            "reason",
            "Human review required.",
        ),
    )

    return review_id


def list_pending_reviews(
    limit: int = 100
):

    return get_pending_reviews(
        limit=limit
    )


def complete_review(
    review_id: int,
    reviewed_by: str,
    human_decision: str,
    human_comments=None,
):

    allowed_decisions = {
        "APPROVED",
        "MODIFIED",
        "REJECTED",
    }

    if human_decision not in allowed_decisions:

        raise ValueError(
            "human_decision must be one of: "
            "APPROVED, MODIFIED, REJECTED"
        )

    updated = resolve_review(
        review_id=review_id,
        reviewed_by=reviewed_by,
        human_decision=human_decision,
        human_comments=human_comments,
    )

    if not updated:
        raise ValueError(
            "Pending review was not found "
            "or was already completed."
        )

    return {
        "review_id":
            review_id,

        "status":
            "COMPLETED",

        "human_decision":
            human_decision,
    }
