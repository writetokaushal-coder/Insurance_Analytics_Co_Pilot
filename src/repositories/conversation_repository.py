from sqlalchemy import text
from src.database import engine

def ensure_session(session_id: str):
    q = text("""
    IF NOT EXISTS (
        SELECT 1 FROM analytics.ai_chat_sessions
        WHERE SESSION_ID=:session_id
    )
    INSERT INTO analytics.ai_chat_sessions(SESSION_ID)
    VALUES(:session_id)
    """)
    with engine.begin() as c:
        c.execute(q, {"session_id": session_id})

def add_message(session_id: str, role: str, message_text: str):
    ensure_session(session_id)
    q = text("""
    INSERT INTO analytics.ai_chat_messages
    (SESSION_ID, ROLE, MESSAGE_TEXT)
    VALUES(:session_id,:role,:message_text);

    UPDATE analytics.ai_chat_sessions
    SET UPDATED_AT=SYSUTCDATETIME()
    WHERE SESSION_ID=:session_id;
    """)
    with engine.begin() as c:
        c.execute(q, {
            "session_id": session_id,
            "role": role,
            "message_text": message_text
        })

def get_recent_messages(session_id: str, limit: int = 12):
    ensure_session(session_id)
    limit = max(1, min(int(limit), 50))
    q = text(f"""
    SELECT ROLE, MESSAGE_TEXT, CREATED_AT
    FROM (
        SELECT TOP {limit}
            ROLE, MESSAGE_TEXT, CREATED_AT, MESSAGE_ID
        FROM analytics.ai_chat_messages
        WHERE SESSION_ID=:session_id
        ORDER BY MESSAGE_ID DESC
    ) x
    ORDER BY CREATED_AT ASC
    """)
    with engine.connect() as c:
        rows = c.execute(q, {"session_id": session_id}).mappings().all()
    return [dict(r) for r in rows]

def get_session(session_id: str):
    ensure_session(session_id)
    q = text("""
    SELECT SESSION_ID, CREATED_AT, UPDATED_AT, STATUS, LAST_INTENT
    FROM analytics.ai_chat_sessions
    WHERE SESSION_ID=:session_id
    """)
    with engine.connect() as c:
        row = c.execute(q, {"session_id": session_id}).mappings().first()
    return dict(row) if row else None
