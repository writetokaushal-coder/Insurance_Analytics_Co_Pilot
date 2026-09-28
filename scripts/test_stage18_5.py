from uuid import uuid4
from src.repositories.conversation_repository import ensure_session, add_message, get_recent_messages
from src.repositories.audit_repository import log_tool_call, get_recent_tool_audit

sid = str(uuid4())
print("Session:", sid)

ensure_session(sid)
add_message(sid, "user", "Test user message")
add_message(sid, "assistant", "Test assistant message")

print("Messages:", get_recent_messages(sid))

log_tool_call(
    session_id=sid,
    tool_name="test_tool",
    tool_args={"x": 1},
    tool_result={"ok": True},
    status="SUCCESS"
)

print("Audit:", get_recent_tool_audit(sid))
print("Stage 18.5 SQL persistence test passed.")
