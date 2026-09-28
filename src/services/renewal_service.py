from src.renewal_predictor import (
    predict_renewal
)

from src.policies.decision_policy import (
    evaluate_renewal_decision
)


# -----------------------------------
# Human-friendly response
# -----------------------------------

def create_renewal_message(
    prediction,
    decision
):

    risk_pct = prediction[
        "non_renewal_risk_pct"
    ]

    risk_band = prediction[
        "risk_band"
    ]


    if risk_band == "High":

        return (
            f"This policy currently shows "
            f"a {risk_pct}% estimated risk "
            f"of non-renewal. "
            f"It should be prioritized for "
            f"human retention review. "
            f"The system will not automatically "
            f"change premium, coverage, or offer "
            f"financial concessions."
        )


    elif risk_band == "Medium":

        return (
            f"This policy currently shows "
            f"a moderate non-renewal risk "
            f"of {risk_pct}%. "
            f"A reminder and monitoring "
            f"workflow is appropriate."
        )


    else:

        return (
            f"This policy currently shows "
            f"a relatively low estimated "
            f"non-renewal risk of "
            f"{risk_pct}%. "
            f"It can remain in the standard "
            f"renewal journey."
        )


# -----------------------------------
# Complete renewal assessment
# -----------------------------------

def assess_renewal(
    policy_id: str
):

    # ML prediction
    prediction = predict_renewal(
        policy_id
    )


    # Apply deterministic
    # business / HITL rules
    decision = (
        evaluate_renewal_decision(
            prediction
        )
    )


    # Human-readable response
    message = create_renewal_message(
        prediction,
        decision
    )


    return {

        "prediction":
            prediction,

        "decision":
            decision,

        "message":
            message
    }