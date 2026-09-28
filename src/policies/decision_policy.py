# ==========================================================
# Deterministic business / safety policy layer
# ==========================================================

RESTRICTED_ACTIONS = {
    "change_premium",
    "approve_underwriting",
    "decline_underwriting",
    "apply_loading",
    "approve_claim",
    "reject_claim",
    "cancel_policy",
    "modify_coverage",
}


def evaluate_renewal_decision(
    prediction: dict
):

    risk_band = prediction[
        "risk_band"
    ]

    if risk_band == "High":

        return {
            "automation_allowed":
                False,

            "human_review_required":
                True,

            "recommended_action":
                "Priority retention review",

            "reason":
                "High non-renewal risk.",
        }

    if risk_band == "Medium":

        return {
            "automation_allowed":
                True,

            "human_review_required":
                False,

            "recommended_action":
                "Send reminder and monitor",

            "reason":
                "Moderate renewal risk.",
        }

    return {
        "automation_allowed":
            True,

        "human_review_required":
            False,

        "recommended_action":
            "Standard renewal journey",

        "reason":
            "Low renewal risk.",
    }


def evaluate_fraud_decision(
    prediction: dict
):

    fraud_prediction = prediction[
        "prediction"
    ]

    if fraud_prediction == "Fraud Risk":

        return {
            "automation_allowed":
                False,

            "human_review_required":
                True,

            "recommended_action":
                "Refer claim for fraud investigation",

            "reason":
                "Model detected elevated fraud risk.",

            "restriction":
                (
                    "The model output is a screening "
                    "signal, not proof of fraud. "
                    "Do not automatically reject the claim."
                ),
        }

    return {
        "automation_allowed":
            True,

        "human_review_required":
            False,

        "recommended_action":
            "Continue standard claim workflow",

        "reason":
            "No elevated fraud alert was triggered.",

        "restriction":
            (
                "No fraud alert is not equivalent "
                "to claim approval."
            ),
    }


def evaluate_underwriting_decision(
    prediction: dict
):

    decision = prediction[
        "decision"
    ]

    if decision == "Declined":

        return {
            "automation_allowed":
                False,

            "human_review_required":
                True,

            "recommended_action":
                "Senior underwriting review",

            "reason":
                (
                    "The model recommends decline. "
                    "A final decline requires human review."
                ),
        }

    if decision == "Approved with Loading":

        return {
            "automation_allowed":
                False,

            "human_review_required":
                True,

            "recommended_action":
                "Underwriter review for loading",

            "reason":
                (
                    "The recommendation can change "
                    "customer pricing."
                ),
        }

    return {
        "automation_allowed":
            True,

        "human_review_required":
            False,

        "recommended_action":
            "Continue standard underwriting workflow",

        "reason":
            "Model recommends standard approval.",
    }


def evaluate_requested_action(
    action: str
):

    if action in RESTRICTED_ACTIONS:

        return {
            "automation_allowed":
                False,

            "human_review_required":
                True,

            "reason":
                (
                    "This is a sensitive or "
                    "high-impact insurance action."
                ),
        }

    return {
        "automation_allowed":
            True,

        "human_review_required":
            False,

        "reason":
            "Action is allowed by the current policy layer.",
    }
