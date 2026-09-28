from typing import Optional

from uuid import uuid4

from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import (
    BaseModel,
    Field,
)

from src.llm.copilot import (
    run_insurance_copilot
)


router = APIRouter(
    tags=[
        "ai-copilot"
    ]
)


class AICopilotRequest(
    BaseModel
):

    session_id: Optional[str] = None

    message: str = Field(
        min_length=1
    )


@router.post(
    "/chat/ai"
)
def ai_copilot_chat(
    request: AICopilotRequest
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
            run_insurance_copilot(
                session_id=
                    session_id,

                message=
                    request.message,
            )
        )


    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to complete "
                "the AI Copilot request."
            ),
        )
