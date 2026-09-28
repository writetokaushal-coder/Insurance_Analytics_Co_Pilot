def build_missing_fields_message(
    intent: str,
    missing_fields: list,
    collected_fields: list,
):

    # Keep the message readable.
    visible_missing = (
        missing_fields[:8]
    )

    more_count = (
        len(
            missing_fields
        )
        -
        len(
            visible_missing
        )
    )

    missing_text = ", ".join(
        visible_missing
    )

    if more_count > 0:
        missing_text += (
            f" and {more_count} more"
        )


    if intent == "renewal":

        return (
            "I can check the renewal risk. "
            "Please provide the policy ID."
        )


    if intent == "fraud":

        return (
            "I have started the fraud-screening workflow. "
            f"I still need: {missing_text}. "
            "You can send the values gradually; "
            "I will keep the information in this session. "
            "A high fraud score will be treated as an "
            "investigation signal, not proof of fraud."
        )


    if intent == "underwriting":

        return (
            "I have started the underwriting assessment. "
            f"I still need: {missing_text}. "
            "You can provide the values gradually and "
            "I will keep them for this session. "
            "Any loaded or declined recommendation remains "
            "subject to human underwriting review."
        )


    return (
        "Please provide the missing information "
        f"for the workflow: {missing_text}."
    )


def build_completed_message(
    intent: str,
    tool_result: dict
):

    result = tool_result.get(
        "result",
        {}
    )

    # Existing services already create
    # human-readable messages.
    service_message = result.get(
        "message"
    )

    if service_message:
        return service_message


    return (
        f"The {intent} workflow completed successfully."
    )
