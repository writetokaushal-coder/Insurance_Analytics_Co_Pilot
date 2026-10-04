from sqlalchemy import text
from functools import lru_cache  # 1. Ye naya import add kiya hai
from src.database import engine

def get_policy_summary(policy_id: str):
    query = text(
        """
        SELECT TOP 1
            POLICY_ID, CUSTOMER_ID, POLICY_TYPE, POLICY_STATUS,
            SALES_CHANNEL, PAYMENT_MODE, SUM_INSURED, ANNUAL_PREMIUM,
            RISK_SCORE, RISK_BAND, CUSTOMER_RISK_SEGMENT, STATE,
            HAS_PAYMENT_RECORD, TOTAL_CLAIMS, HAS_UNDERWRITING_RECORD,
            UW_DECISION, HAS_RENEWAL_RECORD, HAS_FINALIZED_RENEWAL,
            RENEWED_FLAG
        FROM analytics.policy_360
        WHERE POLICY_ID = :policy_id
        """
    )
    with engine.connect() as connection:
        row = (
            connection.execute(query, {"policy_id": policy_id})
            .mappings()
            .first()
        )

    if row is None:
        return None
    return dict(row)

# 2. Ye decorator function ke theek upar lagana hai
@lru_cache(maxsize=1)
def get_portfolio_summary():
    query = text(
        """
        SELECT
            COUNT(*) AS TOTAL_POLICIES,
            COUNT(DISTINCT CUSTOMER_ID) AS TOTAL_POLICY_CUSTOMERS,
            SUM(ANNUAL_PREMIUM) AS TOTAL_ANNUAL_PREMIUM,
            AVG(ANNUAL_PREMIUM) AS AVG_ANNUAL_PREMIUM,
            SUM(
                CASE WHEN POLICY_STATUS = 'Active' THEN 1 ELSE 0 END
            ) AS SOURCE_REPORTED_ACTIVE_POLICIES,
            SUM(
                CASE WHEN HAS_CLAIM_RECORD = 1 THEN 1 ELSE 0 END
            ) AS POLICIES_WITH_CLAIMS,
            SUM(
                CASE WHEN HAS_FINALIZED_RENEWAL = 1 THEN 1 ELSE 0 END
            ) AS FINALIZED_RENEWALS
        FROM analytics.policy_360
        """
    )

    with engine.connect() as connection:
        row = (
            connection.execute(query)
            .mappings()
            .first()
        )

    return dict(row) if row else {}

# Optional: Agar kabhi naya data aaye toh cache clear karne ke liye ek helper function
def clear_portfolio_cache():
    get_portfolio_summary.cache_clear()