import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_config():
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider != "ollama":
        raise RuntimeError(
            "This free Stage-18 configuration expects LLM_PROVIDER=ollama."
        )

    return {
        "provider": provider,
        "model_name": os.getenv("OLLAMA_MODEL", "qwen3:4b"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    }
