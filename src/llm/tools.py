from langchain_core.tools import tool

from src.agents.renewal_agent import (
    handle_renewal
)

from src.agents.fraud_agent import (
    handle_fraud
)

from src.agents.underwriting_agent import (
    handle_underwriting
)

from src.repositories.policy_repository import (
    get_policy_summary,
    get_portfolio_summary,
)

from src.llm.knowledge import (
    search_knowledge
)


@tool
def renewal_assessment(
    policy_id: str
) -> dict:
    """
    Assess non-renewal risk for an existing policy ID.
    Use this for renewal, lapse, retention, or non-renewal questions.
    """

    return handle_renewal(
        policy_id
    )


@tool
def policy_summary(
    policy_id: str
) -> dict:
    """
    Retrieve factual Policy-360 context for one policy ID.
    Use this before explaining policy-level details.
    """

    result = get_policy_summary(
        policy_id
    )


    if result is None:

        return {
            "found":
                False,

            "policy_id":
                policy_id,
        }


    return {
        "found":
            True,

        "policy":
            result,
    }


@tool
def portfolio_summary() -> dict:
    """
    Retrieve top-level portfolio KPIs from the trusted SQL Policy-360 table.
    """

    return get_portfolio_summary()


@tool
def fraud_screening(
    CLAIM_ID: str,
    CLAIM_AMOUNT: float,
    REPORTING_DELAY_DAYS: int,
    INCIDENT_MONTH: int,
    AGE: int,
    ANNUAL_INCOME: float,
    CREDIT_SCORE: int,
    SUM_INSURED: float,
    ANNUAL_PREMIUM: float,
    RISK_SCORE: float,
    CLAIM_TYPE: str,
    SOURCE: str,
    CLAIM_SEVERITY: str,
    GENDER: str,
    MARITAL_STATUS: str,
    OCCUPATION: str,
    STATE: str,
    CUSTOMER_RISK_SEGMENT: str,
    POLICY_TYPE: str,
    PAYMENT_MODE: str,
    RISK_BAND: str,
) -> dict:
    """
    Screen a claim for elevated fraud risk.
    This is an investigation signal only, not proof of fraud.
    """

    claim_data = {
        "CLAIM_ID":
            CLAIM_ID,

        "CLAIM_AMOUNT":
            CLAIM_AMOUNT,

        "REPORTING_DELAY_DAYS":
            REPORTING_DELAY_DAYS,

        "INCIDENT_MONTH":
            INCIDENT_MONTH,

        "AGE":
            AGE,

        "ANNUAL_INCOME":
            ANNUAL_INCOME,

        "CREDIT_SCORE":
            CREDIT_SCORE,

        "SUM_INSURED":
            SUM_INSURED,

        "ANNUAL_PREMIUM":
            ANNUAL_PREMIUM,

        "RISK_SCORE":
            RISK_SCORE,

        "CLAIM_TYPE":
            CLAIM_TYPE,

        "SOURCE":
            SOURCE,

        "CLAIM_SEVERITY":
            CLAIM_SEVERITY,

        "GENDER":
            GENDER,

        "MARITAL_STATUS":
            MARITAL_STATUS,

        "OCCUPATION":
            OCCUPATION,

        "STATE":
            STATE,

        "CUSTOMER_RISK_SEGMENT":
            CUSTOMER_RISK_SEGMENT,

        "POLICY_TYPE":
            POLICY_TYPE,

        "PAYMENT_MODE":
            PAYMENT_MODE,

        "RISK_BAND":
            RISK_BAND,
    }


    return handle_fraud(
        claim_data
    )


@tool
def underwriting_assessment(
    AGE: int,
    HEALTH_SCORE: float,
    BMI: float,
    CREDIT_SCORE: int,
    LIFESTYLE: str,
    MEDICAL_HISTORY_FLAG: str,
    SMOKER_FLAG: str,
    OCCUPATION_RISK: str,
    UNDERWRITING_ID: str = "",
) -> dict:
    """
    Run underwriting decision support for an applicant.
    Loaded or declined recommendations may require human review.
    """

    applicant_data = {
        "AGE":
            AGE,

        "HEALTH_SCORE":
            HEALTH_SCORE,

        "BMI":
            BMI,

        "CREDIT_SCORE":
            CREDIT_SCORE,

        "LIFESTYLE":
            LIFESTYLE,

        "MEDICAL_HISTORY_FLAG":
            MEDICAL_HISTORY_FLAG,

        "SMOKER_FLAG":
            SMOKER_FLAG,

        "OCCUPATION_RISK":
            OCCUPATION_RISK,
    }


    if UNDERWRITING_ID:

        applicant_data[
            "UNDERWRITING_ID"
        ] = UNDERWRITING_ID


    return handle_underwriting(
        applicant_data
    )


@tool
def search_insurance_knowledge(
    query: str
) -> dict:
    """
    Search local insurance/process knowledge files in rag/knowledge.
    Use for domain, process, policy wording, or project-document questions.
    """

    return search_knowledge(
        query=query,
        top_k=4,
    )


INSURANCE_TOOLS = [
    renewal_assessment,
    policy_summary,
    portfolio_summary,
    fraud_screening,
    underwriting_assessment,
    search_insurance_knowledge,
]
