from fastapi import APIRouter, HTTPException
from src.repositories.conversation_repository import get_session, get_recent_messages
from src.repositories.audit_repository import get_recent_tool_audit

router = APIRouter(tags=["ai-admin"])

@router.get("/ai/session/{session_id}")
def inspect_ai_session(session_id: str):
    try:
        return {
            "session": get_session(session_id),
            "messages": get_recent_messages(session_id, 50)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/audit/{session_id}")
def inspect_ai_audit(session_id: str):
    try:
        return {
            "session_id": session_id,
            "tool_calls": get_recent_tool_audit(session_id, 100)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
