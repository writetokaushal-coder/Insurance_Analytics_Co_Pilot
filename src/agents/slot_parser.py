import re


def extract_policy_id(
    message: str
):
    match = re.search(
        r"\b(?:POL|POLICY)[-_ ]?\d+\b",
        message,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return (
        match.group(0)
        .upper()
        .replace(
            "POLICY",
            "POL"
        )
        .replace(
            " ",
            ""
        )
        .replace(
            "-",
            ""
        )
        .replace(
            "_",
            ""
        )
    )


def extract_claim_id(
    message: str
):
    match = re.search(
        r"\b(?:CLM|CLAIM)[-_ ]?\d+\b",
        message,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return (
        match.group(0)
        .upper()
        .replace(
            "CLAIM",
            "CLM"
        )
        .replace(
            " ",
            ""
        )
        .replace(
            "-",
            ""
        )
        .replace(
            "_",
            ""
        )
    )


def extract_key_value_slots(
    message: str
):
    """
    Parse simple text such as:

    AGE=45, BMI=29.1, HEALTH_SCORE=72,
    SMOKER_FLAG=Yes

    This is intentionally simple.
    Stage 18 LLM extraction will handle
    more natural free-form language.
    """

    slots = {}

    # Split on comma or semicolon.
    parts = re.split(
        r"[,;]",
        message
    )

    for part in parts:

        if "=" not in part:
            continue

        key, value = part.split(
            "=",
            1
        )

        key = (
            key
            .strip()
            .upper()
        )

        value = value.strip()

        if not key or not value:
            continue

        # Convert obvious numeric values.
        if re.fullmatch(
            r"-?\d+",
            value
        ):
            parsed_value = int(
                value
            )

        elif re.fullmatch(
            r"-?\d+\.\d+",
            value
        ):
            parsed_value = float(
                value
            )

        else:
            parsed_value = value

        slots[
            key
        ] = parsed_value

    return slots


def extract_basic_slots(
    message: str
):
    slots = (
        extract_key_value_slots(
            message
        )
    )

    policy_id = extract_policy_id(
        message
    )

    claim_id = extract_claim_id(
        message
    )

    if policy_id:
        slots[
            "policy_id"
        ] = policy_id

    if claim_id:
        slots[
            "CLAIM_ID"
        ] = claim_id

    return slots
