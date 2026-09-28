from typing import (
    Optional,
    Dict,
    Any,
)

from uuid import uuid4

from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import (
    BaseModel,
    Field,
)

from src.agents.stateful_orchestrator import (
    run_stateful_orchestrator,
    get_session_state,
    clear_session_state,
)


router = APIRouter(
    tags=[
        "stateful-chat"
    ]
)


class StatefulChatRequest(
    BaseModel
):

    session_id: Optional[str] = None

    message: str = Field(
        min_length=1
    )

    # Optional structured fields collected
    # by a future GUI form or caller.
    context: Optional[
        Dict[
            str,
            Any
        ]
    ] = None


@router.post(
    "/chat/v2"
)
def stateful_chat(
    request: StatefulChatRequest
):

    session_id = (
        request.session_id
        or
        str(
            uuid4()
        )
    )


    try:

        return (
            run_stateful_orchestrator(
                session_id=
                    session_id,

                message=
                    request.message,

                context=
                    request.context,
            )
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to complete "
                "the conversation workflow."
            ),
        )


@router.get(
    "/chat/session/{session_id}"
)
def get_chat_session(
    session_id: str
):

    return get_session_state(
        session_id
    )


@router.delete(
    "/chat/session/{session_id}"
)
def clear_chat_session(
    session_id: str
):

    return clear_session_state(
        session_id
    )
