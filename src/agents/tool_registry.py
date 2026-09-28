from src.agents.renewal_agent import (
    handle_renewal
)

from src.agents.fraud_agent import (
    handle_fraud
)

from src.agents.underwriting_agent import (
    handle_underwriting
)


def call_workflow_tool(
    intent: str,
    slots: dict
):

    if intent == "renewal":

        return handle_renewal(
            slots[
                "policy_id"
            ]
        )


    if intent == "fraud":

        claim_data = {
            key:
                value

            for key, value
            in slots.items()

            if key != "policy_id"
        }

        return handle_fraud(
            claim_data
        )


    if intent == "underwriting":

        applicant_data = {
            key:
                value

            for key, value
            in slots.items()

            if key not in {
                "policy_id",
                "CLAIM_ID",
            }
        }

        return handle_underwriting(
            applicant_data
        )


    raise ValueError(
        f"No tool registered for "
        f"intent: {intent}"
    )
