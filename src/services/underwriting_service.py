from src.models.underwriting_predictor import (
    predict_underwriting
)

from src.policies.decision_policy import (
    evaluate_underwriting_decision
)


def create_underwriting_message(
    prediction,
    decision,
):

    recommendation = prediction[
        "decision"
    ]

    confidence_pct = prediction.get(
        "confidence_pct"
    )

    if recommendation == "Declined":

        return (
            f"The underwriting model currently "
            f"recommends decline"
            f"{f' with {confidence_pct}% confidence' if confidence_pct is not None else ''}. "
            f"This is decision support only. "
            f"A final decline must be reviewed "
            f"by a human underwriter."
        )

    if recommendation == "Approved with Loading":

        return (
            f"The underwriting model recommends "
            f"approval with additional premium loading"
            f"{f' with {confidence_pct}% confidence' if confidence_pct is not None else ''}. "
            f"Because this can change customer pricing, "
            f"a human underwriter must review the case."
        )

    return (
        f"The underwriting model currently recommends "
        f"standard approval"
        f"{f' with {confidence_pct}% confidence' if confidence_pct is not None else ''}. "
        f"The case can continue through the normal "
        f"underwriting workflow, subject to existing "
        f"business controls."
    )


def assess_underwriting(
    applicant_data: dict
):

    prediction = predict_underwriting(
        applicant_data
    )

    decision = (
        evaluate_underwriting_decision(
            prediction
        )
    )

    message = (
        create_underwriting_message(
            prediction,
            decision,
        )
    )

    return {
        "prediction":
            prediction,

        "decision":
            decision,

        "message":
            message,
    }
