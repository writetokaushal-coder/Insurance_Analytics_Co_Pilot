from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.agents.orchestrator import run_orchestrator


router = APIRouter(
    tags=["chat"]
)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1
    )

    policy_id: Optional[str] = None

    claim_data: Optional[
        Dict[str, Any]
    ] = None

    applicant_data: Optional[
        Dict[str, Any]
    ] = None


@router.post("/chat")
def chat(request: ChatRequest):
    try:
        return run_orchestrator(
            message=request.message,
            policy_id=request.policy_id,
            claim_data=request.claim_data,
            applicant_data=request.applicant_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the conversation.",
        )
