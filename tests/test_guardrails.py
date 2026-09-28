from src.policies.decision_policy import (
    evaluate_fraud_decision,
    evaluate_underwriting_decision,
)


def test_fraud_alert_requires_human_review():
    prediction = {
        "prediction": "Fraud Risk"
    }

    decision = evaluate_fraud_decision(
        prediction
    )

    assert decision["human_review_required"] is True
    assert decision["automation_allowed"] is False


def test_underwriting_decline_requires_human_review():
    prediction = {
        "decision": "Declined"
    }

    decision = evaluate_underwriting_decision(
        prediction
    )

    assert decision["human_review_required"] is True
    assert decision["automation_allowed"] is False


def test_underwriting_loading_requires_human_review():
    prediction = {
        "decision": "Approved with Loading"
    }

    decision = evaluate_underwriting_decision(
        prediction
    )

    assert decision["human_review_required"] is True
