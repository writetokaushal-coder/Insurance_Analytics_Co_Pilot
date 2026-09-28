from sqlalchemy import text

from src.database import engine


def create_review(
    domain: str,
    entity_id: str,
    requested_action: str,
    ai_recommendation: str,
    reason: str,
    ai_score=None,
):

    # Avoid duplicate pending reviews for the same case/action.
    check_query = text(
        """
        SELECT TOP 1 REVIEW_ID
        FROM analytics.human_review_queue
        WHERE DOMAIN = :domain
          AND ENTITY_ID = :entity_id
          AND REQUESTED_ACTION = :requested_action
          AND STATUS = 'PENDING_REVIEW'
        ORDER BY CREATED_AT DESC
        """
    )

    insert_query = text(
        """
        INSERT INTO analytics.human_review_queue
        (
            DOMAIN,
            ENTITY_ID,
            REQUESTED_ACTION,
            AI_RECOMMENDATION,
            AI_SCORE,
            REASON,
            STATUS
        )
        OUTPUT INSERTED.REVIEW_ID
        VALUES
        (
            :domain,
            :entity_id,
            :requested_action,
            :ai_recommendation,
            :ai_score,
            :reason,
            'PENDING_REVIEW'
        )
        """
    )

    with engine.begin() as connection:

        existing = connection.execute(
            check_query,
            {
                "domain":
                    domain,

                "entity_id":
                    entity_id,

                "requested_action":
                    requested_action,
            },
        ).scalar()

        if existing is not None:
            return int(
                existing
            )

        review_id = connection.execute(
            insert_query,
            {
                "domain":
                    domain,

                "entity_id":
                    entity_id,

                "requested_action":
                    requested_action,

                "ai_recommendation":
                    ai_recommendation,

                "ai_score":
                    ai_score,

                "reason":
                    reason,
            },
        ).scalar_one()

    return int(
        review_id
    )


def get_pending_reviews(
    limit: int = 100
):

    limit = max(
        1,
        min(
            int(limit),
            500,
        ),
    )

    # TOP cannot always be parameterized consistently,
    # therefore limit is sanitized above before interpolation.
    query = text(
        f"""
        SELECT TOP {limit}
            *
        FROM analytics.human_review_queue
        WHERE STATUS = 'PENDING_REVIEW'
        ORDER BY CREATED_AT ASC
        """
    )

    with engine.connect() as connection:

        rows = (
            connection.execute(
                query
            )
            .mappings()
            .all()
        )

    return [
        dict(row)
        for row in rows
    ]


def resolve_review(
    review_id: int,
    reviewed_by: str,
    human_decision: str,
    human_comments=None,
):

    update_query = text(
        """
        UPDATE analytics.human_review_queue

        SET
            STATUS = 'COMPLETED',
            REVIEWED_AT = SYSUTCDATETIME(),
            REVIEWED_BY = :reviewed_by,
            HUMAN_DECISION = :human_decision,
            HUMAN_COMMENTS = :human_comments

        WHERE REVIEW_ID = :review_id
          AND STATUS = 'PENDING_REVIEW'
        """
    )

    with engine.begin() as connection:

        result = connection.execute(
            update_query,
            {
                "review_id":
                    review_id,

                "reviewed_by":
                    reviewed_by,

                "human_decision":
                    human_decision,

                "human_comments":
                    human_comments,
            },
        )

    return (
        result.rowcount > 0
    )
