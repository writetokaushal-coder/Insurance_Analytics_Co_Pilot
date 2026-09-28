from src.agents.router import (
    detect_intent
)

from src.agents.conversation_state import (
    conversation_store
)

from src.agents.slot_parser import (
    extract_basic_slots
)

from src.agents.workflow_specs import (
    get_missing_fields
)

from src.agents.tool_registry import (
    call_workflow_tool
)

from src.agents.response_builder import (
    build_missing_fields_message,
    build_completed_message,
)


SUPPORTED_INTENTS = {
    "renewal",
    "fraud",
    "underwriting",
}


def _append_history(
    state: dict,
    role: str,
    message: str
):

    state[
        "history"
    ].append({
        "role":
            role,

        "message":
            message,
    })

    # Prevent unlimited memory growth
    state[
        "history"
    ] = state[
        "history"
    ][-20:]


def run_stateful_orchestrator(
    session_id: str,
    message: str,
    context: dict = None,
):

    state = conversation_store.get(
        session_id
    )

    _append_history(
        state,
        "user",
        message
    )


    # -----------------------------------
    # Route current message
    # -----------------------------------

    route = detect_intent(
        message
    )

    detected_intent = route[
        "intent"
    ]


    # If current text is only supplying a value
    # (for example "POL123"), keep the workflow
    # already active in this conversation.
    if (
        detected_intent
        not in SUPPORTED_INTENTS
        and
        state.get(
            "active_intent"
        )
        in SUPPORTED_INTENTS
    ):
        intent = state[
            "active_intent"
        ]

    elif (
        detected_intent
        in SUPPORTED_INTENTS
    ):
        intent = detected_intent

        # Starting a different workflow clears
        # old workflow-specific slots.
        if (
            state.get(
                "active_intent"
            )
            not in (
                None,
                intent,
            )
        ):
            state[
                "slots"
            ] = {}

        state[
            "active_intent"
        ] = intent

    else:

        intent = None


    # -----------------------------------
    # No supported workflow detected
    # -----------------------------------

    if intent is None:

        assistant_message = (
            "I can currently work with renewal risk, "
            "fraud screening, and underwriting assessment. "
            "Tell me which one you want to work on."
        )

        _append_history(
            state,
            "assistant",
            assistant_message
        )

        conversation_store.save(
            state
        )

        return {
            "session_id":
                session_id,

            "intent":
                "general",

            "status":
                "needs_input",

            "message":
                assistant_message,

            "state": {
                "active_intent":
                    state.get(
                        "active_intent"
                    ),

                "collected_fields":
                    sorted(
                        state[
                            "slots"
                        ].keys()
                    ),
            },
        }


    # -----------------------------------
    # Extract text slots
    # -----------------------------------

    extracted_slots = (
        extract_basic_slots(
            message
        )
    )

    state[
        "slots"
    ].update(
        extracted_slots
    )


    # Explicit API context wins over
    # text-parsed values.
    if context:

        state[
            "slots"
        ].update(
            context
        )


    # -----------------------------------
    # Check required inputs
    # -----------------------------------

    missing_fields = (
        get_missing_fields(
            intent,
            state[
                "slots"
            ]
        )
    )


    if missing_fields:

        assistant_message = (
            build_missing_fields_message(
                intent=
                    intent,

                missing_fields=
                    missing_fields,

                collected_fields=
                    list(
                        state[
                            "slots"
                        ].keys()
                    ),
            )
        )

        _append_history(
            state,
            "assistant",
            assistant_message
        )

        conversation_store.save(
            state
        )

        return {
            "session_id":
                session_id,

            "intent":
                intent,

            "status":
                "needs_input",

            "missing_fields":
                missing_fields,

            "collected_fields":
                sorted(
                    state[
                        "slots"
                    ].keys()
                ),

            "message":
                assistant_message,
        }


    # -----------------------------------
    # All required information exists.
    # Call the registered business tool.
    # -----------------------------------

    tool_result = (
        call_workflow_tool(
            intent=
                intent,

            slots=
                state[
                    "slots"
                ],
        )
    )


    assistant_message = (
        build_completed_message(
            intent=
                intent,

            tool_result=
                tool_result,
        )
    )


    _append_history(
        state,
        "assistant",
        assistant_message
    )


    # Workflow completed.
    completed_intent = intent

    state[
        "active_intent"
    ] = None

    state[
        "slots"
    ] = {}


    conversation_store.save(
        state
    )


    return {
        "session_id":
            session_id,

        "intent":
            completed_intent,

        "status":
            "completed",

        "message":
            assistant_message,

        "tool_result":
            tool_result,
    }


def get_session_state(
    session_id: str
):
    return conversation_store.get(
        session_id
    )


def clear_session_state(
    session_id: str
):
    deleted = (
        conversation_store.clear(
            session_id
        )
    )

    return {
        "session_id":
            session_id,

        "cleared":
            deleted,
    }
