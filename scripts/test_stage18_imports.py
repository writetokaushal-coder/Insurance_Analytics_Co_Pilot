def main():

    from src.llm.config import (
        get_openai_config
    )

    from src.llm.tools import (
        INSURANCE_TOOLS
    )

    from src.llm.copilot import (
        run_insurance_copilot
    )


    print(
        "Stage 18 imports loaded."
    )


    print(
        "Registered tools:"
    )


    for tool in INSURANCE_TOOLS:

        print(
            "-",
            tool.name
        )


    try:

        config = (
            get_openai_config()
        )

        print(
            "OPENAI_MODEL:",
            config[
                "model_name"
            ]
        )

        print(
            "OPENAI_API_KEY:"
            " configured"
        )

    except RuntimeError as error:

        print(
            "Configuration warning:",
            str(error)
        )


if __name__ == "__main__":

    main()
