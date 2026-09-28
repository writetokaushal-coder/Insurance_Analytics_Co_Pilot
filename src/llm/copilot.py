import json

from langchain_ollama import ChatOllama

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)

from src.agents.conversation_state import conversation_store
from src.llm.config import get_llm_config
from src.llm.prompts import INSURANCE_COPILOT_SYSTEM_PROMPT
from src.llm.tools import INSURANCE_TOOLS


TOOL_MAP = {
    tool.name: tool
    for tool in INSURANCE_TOOLS
}


def _history_to_messages(history: list):
    messages = []

    for item in history[-12:]:
        role = item.get("role")
        content = item.get("message", "")

        if role == "user":
            messages.append(
                HumanMessage(content=content)
            )

        elif role == "assistant":
            messages.append(
                AIMessage(content=content)
            )

    return messages


def _safe_json(value):
    return json.dumps(
        value,
        default=str,
        ensure_ascii=False,
    )


def run_insurance_copilot(
    session_id: str,
    message: str
):
    config = get_llm_config()

    llm = ChatOllama(
        model=config["model_name"],
        base_url=config["base_url"],
        temperature=0.1,
        num_ctx=8192,
    )

    llm_with_tools = llm.bind_tools(
        INSURANCE_TOOLS
    )

    state = conversation_store.get(
        session_id
    )

    messages = [
        SystemMessage(
            content=INSURANCE_COPILOT_SYSTEM_PROMPT
        )
    ]

    messages.extend(
        _history_to_messages(
            state.get("history", [])
        )
    )

    messages.append(
        HumanMessage(
            content=message
        )
    )

    for _ in range(6):
        ai_message = llm_with_tools.invoke(
            messages
        )

        messages.append(
            ai_message
        )

        tool_calls = getattr(
            ai_message,
            "tool_calls",
            None,
        )

        if not tool_calls:
            final_text = (
                ai_message.content
                if isinstance(
                    ai_message.content,
                    str
                )
                else str(
                    ai_message.content
                )
            )

            state["history"].append({
                "role": "user",
                "message": message,
            })

            state["history"].append({
                "role": "assistant",
                "message": final_text,
            })

            state["history"] = (
                state["history"][-20:]
            )

            conversation_store.save(
                state
            )

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

            selected_tool = TOOL_MAP.get(
                tool_name
            )

            if selected_tool is None:
                tool_result = {
                    "error": (
                        "Unknown tool requested: "
                        f"{tool_name}"
                    )
                }
            else:
                try:
                    tool_result = (
                        selected_tool.invoke(
                            tool_args
                        )
                    )
                except Exception as error:
                    tool_result = {
                        "error": str(error)
                    }

            messages.append(
                ToolMessage(
                    content=_safe_json(
                        tool_result
                    ),
                    tool_call_id=tool_call_id,
                )
            )

    fallback = (
        "I could not complete the workflow within the tool-call limit. "
        "Please provide a little more detail and try again."
    )

    state["history"].append({
        "role": "user",
        "message": message,
    })

    state["history"].append({
        "role": "assistant",
        "message": fallback,
    })

    state["history"] = (
        state["history"][-20:]
    )

    conversation_store.save(
        state
    )

    return {
        "session_id": session_id,
        "provider": "ollama",
        "model": config["model_name"],
        "status": "incomplete",
        "message": fallback,
    }
