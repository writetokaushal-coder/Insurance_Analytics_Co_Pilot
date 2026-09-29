import json
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from src.llm.config import get_llm_config
from src.llm.prompts import INSURANCE_COPILOT_SYSTEM_PROMPT
from src.llm.tools import INSURANCE_TOOLS
from src.repositories.conversation_repository import add_message, ensure_session, get_recent_messages
from src.repositories.audit_repository import log_tool_call

TOOL_MAP = {tool.name: tool for tool in INSURANCE_TOOLS}

def _history_to_messages(history):
    messages = []
    for item in history:
        role = item.get("ROLE")
        content = item.get("MESSAGE_TEXT", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages

def _json_text(value):
    return json.dumps(value, default=str, ensure_ascii=False)

def run_insurance_copilot(session_id: str, message: str):
    config = get_llm_config()
    ensure_session(session_id)
    history = get_recent_messages(session_id=session_id, limit=12)

    llm = ChatOllama(
        model=config["model_name"],
        base_url=config["base_url"],
        temperature=0.1,
        num_ctx=8192,
    )
    llm_with_tools = llm.bind_tools(INSURANCE_TOOLS)

    messages = [SystemMessage(content=INSURANCE_COPILOT_SYSTEM_PROMPT)]
    messages.extend(_history_to_messages(history))
    messages.append(HumanMessage(content=message))

    for _ in range(6):
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)
        tool_calls = getattr(ai_message, "tool_calls", None)

        if not tool_calls:
            final_text = ai_message.content if isinstance(ai_message.content, str) else str(ai_message.content)
            add_message(session_id=session_id, role="user", message_text=message)
            add_message(session_id=session_id, role="assistant", message_text=final_text)
            return {
                "session_id": session_id,
                "provider": "ollama",
                "model": config["model_name"],
                "status": "completed",
                "message": final_text,
            }

        for call in tool_calls:
            tool_name = call.get("name")
            tool_args = call.get("args", {})
            tool_call_id = call.get("id")
            selected_tool = TOOL_MAP.get(tool_name)

            if selected_tool is None:
                tool_result = {"error": f"Unknown tool requested: {tool_name}"}
                log_tool_call(
                    session_id=session_id,
                    tool_name=tool_name or "UNKNOWN",
                    tool_args=tool_args,
                    tool_result=tool_result,
                    status="ERROR",
                    error_message=tool_result["error"],
                )
            else:
                try:
                    tool_result = selected_tool.invoke(tool_args)
                    log_tool_call(
                        session_id=session_id,
                        tool_name=tool_name,
                        tool_args=tool_args,
                        tool_result=tool_result,
                        status="SUCCESS",
                    )
                except Exception as error:
                    tool_result = {"error": str(error)}
                    log_tool_call(
                        session_id=session_id,
                        tool_name=tool_name,
                        tool_args=tool_args,
                        status="ERROR",
                        error_message=str(error),
                    )

            messages.append(ToolMessage(content=_json_text(tool_result), tool_call_id=tool_call_id))

    fallback = "I could not complete the workflow within the tool-call limit. Please provide a little more detail."
    add_message(session_id=session_id, role="user", message_text=message)
    add_message(session_id=session_id, role="assistant", message_text=fallback)
    return {
        "session_id": session_id,
        "provider": "ollama",
        "model": config["model_name"],
        "status": "incomplete",
        "message": fallback,
    }
