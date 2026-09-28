from typing import Optional, Literal

from pydantic import BaseModel, Field


class FraudRequest(
    BaseModel
):

    # Business identifier; not passed to the model
    CLAIM_ID: str

    CLAIM_AMOUNT: float = Field(
        gt=0
    )

    REPORTING_DELAY_DAYS: int = Field(
        ge=0
    )

    INCIDENT_MONTH: int = Field(
        ge=1,
        le=12
    )

    AGE: int = Field(
        ge=18,
        le=120
    )

    ANNUAL_INCOME: float = Field(
        ge=0
    )

    CREDIT_SCORE: int = Field(
        ge=0
    )

    SUM_INSURED: float = Field(
        gt=0
    )

    ANNUAL_PREMIUM: float = Field(
        ge=0
    )

    RISK_SCORE: float

    CLAIM_TYPE: str
    SOURCE: str
    CLAIM_SEVERITY: str

    GENDER: str
    MARITAL_STATUS: str
    OCCUPATION: str
    STATE: str

    CUSTOMER_RISK_SEGMENT: str

    POLICY_TYPE: str
    PAYMENT_MODE: str
    RISK_BAND: str


class UnderwritingRequest(
    BaseModel
):

    # Optional workflow identifier; not passed to model
    UNDERWRITING_ID: Optional[str] = None

    AGE: int = Field(
        ge=18,
        le=120
    )

    HEALTH_SCORE: float
    BMI: float = Field(
        gt=0
    )

    CREDIT_SCORE: int = Field(
        ge=0
    )

    LIFESTYLE: str
    MEDICAL_HISTORY_FLAG: str
    SMOKER_FLAG: str
    OCCUPATION_RISK: str


class HumanReviewResolution(
    BaseModel
):

    reviewed_by: str

    human_decision: Literal[
        "APPROVED",
        "MODIFIED",
        "REJECTED",
    ]

    human_comments: Optional[str] = None
