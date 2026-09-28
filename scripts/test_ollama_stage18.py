from langchain_ollama import ChatOllama
from src.llm.config import get_llm_config


def main():
    config = get_llm_config()

    print("Provider:", config["provider"])
    print("Model:", config["model_name"])
    print("Base URL:", config["base_url"])

    llm = ChatOllama(
        model=config["model_name"],
        base_url=config["base_url"],
        temperature=0.1,
    )

    response = llm.invoke(
        "Reply only with: Ollama working"
    )

    print(
        "Response:",
        response.content
    )


if __name__ == "__main__":
    main()
