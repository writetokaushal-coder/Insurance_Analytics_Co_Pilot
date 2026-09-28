import json
from sqlalchemy import text
from src.database import engine
from src.repositories.conversation_repository import ensure_session

def log_tool_call(
    session_id: str,
    tool_name: str,
    tool_args,
    tool_result=None,
    status: str="SUCCESS",
    error_message=None
):
    ensure_session(session_id)
    q = text("""
    INSERT INTO analytics.ai_tool_audit
    (SESSION_ID, TOOL_NAME, TOOL_ARGS_JSON, TOOL_RESULT_JSON, STATUS, ERROR_MESSAGE)
    VALUES
    (:session_id,:tool_name,:tool_args_json,:tool_result_json,:status,:error_message)
    """)
    with engine.begin() as c:
        c.execute(q, {
            "session_id": session_id,
            "tool_name": tool_name,
            "tool_args_json": json.dumps(tool_args, default=str),
            "tool_result_json": json.dumps(tool_result, default=str) if tool_result is not None else None,
            "status": status,
            "error_message": error_message
        })

def get_recent_tool_audit(session_id: str, limit: int=50):
    ensure_session(session_id)
    limit = max(1, min(int(limit), 200))
    q = text(f"""
    SELECT TOP {limit}
        AUDIT_ID, TOOL_NAME, TOOL_ARGS_JSON, TOOL_RESULT_JSON,
        STATUS, ERROR_MESSAGE, CREATED_AT
    FROM analytics.ai_tool_audit
    WHERE SESSION_ID=:session_id
    ORDER BY AUDIT_ID DESC
    """)
    with engine.connect() as c:
        rows = c.execute(q, {"session_id": session_id}).mappings().all()
    return [dict(r) for r in rows]
