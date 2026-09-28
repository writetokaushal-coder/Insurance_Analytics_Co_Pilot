RENEWAL_REQUIRED_FIELDS = [
    "policy_id",
]


FRAUD_REQUIRED_FIELDS = [
    "CLAIM_ID",
    "CLAIM_AMOUNT",
    "REPORTING_DELAY_DAYS",
    "INCIDENT_MONTH",
    "AGE",
    "ANNUAL_INCOME",
    "CREDIT_SCORE",
    "SUM_INSURED",
    "ANNUAL_PREMIUM",
    "RISK_SCORE",
    "CLAIM_TYPE",
    "SOURCE",
    "CLAIM_SEVERITY",
    "GENDER",
    "MARITAL_STATUS",
    "OCCUPATION",
    "STATE",
    "CUSTOMER_RISK_SEGMENT",
    "POLICY_TYPE",
    "PAYMENT_MODE",
    "RISK_BAND",
]


UNDERWRITING_REQUIRED_FIELDS = [
    "AGE",
    "HEALTH_SCORE",
    "BMI",
    "CREDIT_SCORE",
    "LIFESTYLE",
    "MEDICAL_HISTORY_FLAG",
    "SMOKER_FLAG",
    "OCCUPATION_RISK",
]


WORKFLOW_SPECS = {
    "renewal": {
        "required_fields":
            RENEWAL_REQUIRED_FIELDS,

        "friendly_name":
            "renewal-risk assessment",
    },

    "fraud": {
        "required_fields":
            FRAUD_REQUIRED_FIELDS,

        "friendly_name":
            "fraud-risk screening",
    },

    "underwriting": {
        "required_fields":
            UNDERWRITING_REQUIRED_FIELDS,

        "friendly_name":
            "underwriting assessment",
    },
}


def get_required_fields(
    intent: str
):
    return (
        WORKFLOW_SPECS
        .get(
            intent,
            {}
        )
        .get(
            "required_fields",
            []
        )
    )


def get_missing_fields(
    intent: str,
    slots: dict
):
    required = get_required_fields(
        intent
    )

    return [
        field
        for field in required
        if slots.get(
            field
        ) in (
            None,
            "",
        )
    ]
