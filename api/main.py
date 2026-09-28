from fastapi import (
    FastAPI,
    HTTPException,
    Query,
)

from sqlalchemy import text

from api.schemas import (
    FraudRequest,
    UnderwritingRequest,
    HumanReviewResolution,
)

from src.database import engine

from src.services.renewal_service import (
    assess_renewal
)

from src.services.fraud_service import (
    assess_fraud
)

from src.services.underwriting_service import (
    assess_underwriting
)

from src.services.human_review_service import (
    queue_review_if_required,
    list_pending_reviews,
    complete_review,
)

from api.chat import router as chat_router

from api.chat_stateful import (
    router as stateful_chat_router
)

from api.chat_llm import (
    router as ai_copilot_router
)

from api.chat_admin import (
    router as ai_admin_router
)

from api.insights import (
    router as insights_router
)

app = FastAPI(
    title="Insurance AI Copilot API",
    description=(
        "Insurance analytics, ML decision support, "
        "guardrails and human-in-the-loop API."
    ),
    version="1.1.0",
)

app.include_router(
    insights_router
)

app.include_router(
    ai_admin_router
)

app.include_router(
    ai_copilot_router
)

app.include_router(
    stateful_chat_router
)

app.include_router(
    chat_router
)


@app.get("/")
def root():

    return {
        "name":
            "Insurance AI Copilot API",

        "version":
            "1.1.0",

        "modules": [
            "renewal",
            "fraud",
            "underwriting",
            "human_review",
        ],
    }


@app.get("/health")
def health():

    database_status = "unavailable"

    try:

        with engine.connect() as connection:

            connection.execute(
                text(
                    "SELECT 1"
                )
            )

        database_status = "healthy"

    except Exception:
        pass

    return {
        "api":
            "healthy",

        "database":
            database_status,
    }


@app.get(
    "/predict/renewal/{policy_id}"
)
def renewal_prediction(
    policy_id: str
):

    try:

        result = assess_renewal(
            policy_id
        )

        decision = result.get(
            "decision",
            {},
        )

        prediction = result.get(
            "prediction",
            {},
        )

        review_id = (
            queue_review_if_required(
                domain="RENEWAL",
                entity_id=policy_id,
                requested_action="retention_outreach",
                decision=decision,
                ai_recommendation=
                    decision.get(
                        "recommended_action",
                        "Retention review",
                    ),
                ai_score=
                    prediction.get(
                        "non_renewal_probability"
                    ),
            )
        )

        result[
            "human_review_id"
        ] = review_id

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to complete "
                "renewal assessment."
            ),
        )


@app.post(
    "/predict/fraud"
)
def fraud_prediction(
    request: FraudRequest
):

    try:

        payload = (
            request.model_dump()
        )

        claim_id = payload.pop(
            "CLAIM_ID"
        )

        result = assess_fraud(
            payload
        )

        prediction = result[
            "prediction"
        ]

        decision = result[
            "decision"
        ]

        review_id = (
            queue_review_if_required(
                domain="FRAUD",
                entity_id=claim_id,
                requested_action=
                    "fraud_investigation",
                decision=decision,
                ai_recommendation=
                    decision.get(
                        "recommended_action",
                        "Fraud investigation",
                    ),
                ai_score=
                    prediction.get(
                        "fraud_probability"
                    ),
            )
        )

        result[
            "claim_id"
        ] = claim_id

        result[
            "human_review_id"
        ] = review_id

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to complete "
                "fraud assessment."
            ),
        )


@app.post(
    "/predict/underwriting"
)
def underwriting_prediction(
    request: UnderwritingRequest
):

    try:

        payload = (
            request.model_dump()
        )

        underwriting_id = payload.pop(
            "UNDERWRITING_ID",
            None,
        )

        result = assess_underwriting(
            payload
        )

        prediction = result[
            "prediction"
        ]

        decision = result[
            "decision"
        ]

        entity_id = (
            underwriting_id
            or
            "NEW_APPLICATION"
        )

        review_id = (
            queue_review_if_required(
                domain="UNDERWRITING",
                entity_id=entity_id,
                requested_action=
                    "underwriting_decision",
                decision=decision,
                ai_recommendation=
                    prediction.get(
                        "decision",
                        "Underwriting review",
                    ),
                ai_score=
                    prediction.get(
                        "confidence"
                    ),
            )
        )

        result[
            "underwriting_id"
        ] = underwriting_id

        result[
            "human_review_id"
        ] = review_id

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to complete "
                "underwriting assessment."
            ),
        )


@app.get(
    "/human-review/pending"
)
def pending_human_reviews(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    )
):

    try:

        return {
            "items":
                list_pending_reviews(
                    limit=limit
                )
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                "human review queue."
            ),
        )


@app.post(
    "/human-review/{review_id}/resolve"
)
def resolve_human_review(
    review_id: int,
    request: HumanReviewResolution,
):

    try:

        return complete_review(
            review_id=review_id,
            reviewed_by=
                request.reviewed_by,
            human_decision=
                request.human_decision,
            human_comments=
                request.human_comments,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to resolve "
                "human review."
            ),
        )
