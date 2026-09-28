def handle_general(message: str):
    return {
        "agent": "general",
        "status": "needs_input",
        "message": (
            "I can currently help with renewal-risk assessment, "
            "fraud screening, and underwriting decision support. "
            "Tell me which area you want to work on and provide "
            "the relevant policy, claim, or applicant information."
        ),
    }


def handle_clarification(candidate_intents):
    options = ", ".join(candidate_intents)

    return {
        "agent": "general",
        "status": "needs_clarification",
        "message": (
            "Your request could relate to more than one workflow: "
            f"{options}. Please tell me which one you want me to handle first."
        ),
    }
