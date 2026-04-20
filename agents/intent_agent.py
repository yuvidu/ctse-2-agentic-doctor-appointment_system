from tools.intent_tools.llm_parsing_tool import llm_parse_input
from tools.intent_tools.missing_tool import detect_missing_fields
from tools.intent_tools.validation_tool import validate_input
from tools.intent_tools.response_tool import build_response


def intent_agent(user_input: str) -> dict:
    print("\n[Agent] Parsing input using Ollama...")

    parsed = llm_parse_input(user_input)
    print("[Parsed]:", parsed)

    missing = detect_missing_fields(parsed)
    print("[Missing]:", missing)

    validation = validate_input(parsed)
    print("[Validation Errors]:", validation["errors"])

    response = build_response(
        missing,
        validation["errors"],
        parsed
    )

    return response