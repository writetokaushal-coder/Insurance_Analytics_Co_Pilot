from src.models.fraud_predictor import predict_fraud
from src.policies.decision_policy import evaluate_fraud_decision


def create_fraud_message(prediction, decision):

    probability = round(
        prediction["fraud_probability"] * 100,
        2
    )

    if prediction["prediction"] == "Fraud Risk":

        message = (
            f"This claim has {probability}% fraud-risk score. "
            f"It should be reviewed by a human fraud investigator. "
            f"This is only a risk flag, not proof of fraud. "
            f"The claim should not be automatically rejected."
        )

    else:

        message = (
            f"This claim has {probability}% fraud-risk score. "
            f"It does not cross the fraud-alert threshold. "
            f"It can continue through the standard claims workflow."
        )

    return message


def assess_fraud(claim_data):

    # Get fraud prediction
    prediction = predict_fraud(claim_data)

    # Apply business decision policy
    decision = evaluate_fraud_decision(prediction)

    # Create human-friendly message
    message = create_fraud_message(
        prediction,
        decision
    )

    # Final response
    result = {
        "prediction": prediction,
        "decision": decision,
        "message": message
    }

    return result