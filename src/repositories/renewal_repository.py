import pandas as pd

from sqlalchemy import text

from src.database import engine


def get_renewal_features(
    policy_id: str
):

    query = text(
        """
        SELECT *
        FROM analytics.renewal_model_features
        WHERE POLICY_ID = :policy_id
        """
    )

    with engine.connect() as connection:

        policy_df = pd.read_sql(
            query,
            connection,
            params={
                "policy_id":
                    policy_id
            },
        )

    return policy_df
