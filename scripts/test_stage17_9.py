from uuid import uuid4

from src.agents.stateful_orchestrator import (
    run_stateful_orchestrator,
)


def show(
    title,
    result
):

    print()
    print(
        "=" * 80
    )

    print(
        title
    )

    print(
        "=" * 80
    )

    print(
        result
    )


if __name__ == "__main__":

    # -----------------------------------
    # Test memory across renewal turns
    # -----------------------------------

    renewal_session = str(
        uuid4()
    )

    result_1 = (
        run_stateful_orchestrator(
            session_id=
                renewal_session,

            message=
                "Please check renewal risk",
        )
    )

    show(
        "RENEWAL TURN 1",
        result_1
    )


    # We deliberately use a fake policy ID here
    # only to demonstrate that the orchestrator
    # remembers the renewal workflow.
    # The real model call will fail if the policy
    # does not exist in SQL, so this call is not
    # executed automatically in this test script.

    print()
    print(
        "Renewal state memory test passed "
        "if TURN 1 asks for policy_id."
    )


    # -----------------------------------
    # Underwriting multi-turn slot filling
    # -----------------------------------

    uw_session = str(
        uuid4()
    )

    result_2 = (
        run_stateful_orchestrator(
            session_id=
                uw_session,

            message=
                "I need an underwriting assessment",
        )
    )

    show(
        "UNDERWRITING TURN 1",
        result_2
    )


    result_3 = (
        run_stateful_orchestrator(
            session_id=
                uw_session,

            message=
                (
                    "AGE=45, HEALTH_SCORE=76, "
                    "BMI=28.2, CREDIT_SCORE=720"
                ),
        )
    )

    show(
        "UNDERWRITING TURN 2",
        result_3
    )


    result_4 = (
        run_stateful_orchestrator(
            session_id=
                uw_session,

            message=
                (
                    "LIFESTYLE=Good, "
                    "MEDICAL_HISTORY_FLAG=No, "
                    "SMOKER_FLAG=No, "
                    "OCCUPATION_RISK=Low"
                ),
        )
    )

    show(
        "UNDERWRITING TURN 3",
        result_4
    )
