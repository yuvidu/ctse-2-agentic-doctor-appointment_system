from tools.intent_tools.llm_parsing_tool import llm_parse_input
from tools.intent_tools.missing_tool import detect_missing_fields
from tools.intent_tools.response_tool import build_response
from tools.intent_tools.validation_tool import validate_input
from utils.env_flags import mas_debug


def intent_agent(state: dict) -> dict:
    if mas_debug():
        print("\n[Agent] Parsing input using Ollama...")

    user_input = state["user_input"]

    parsed = llm_parse_input(user_input)
    if mas_debug():
        print("[Parsed]:", parsed)

    missing = detect_missing_fields(parsed)
    if mas_debug():
        print("[Missing]:", missing)

    validation = validate_input(parsed)
    if mas_debug():
        print("[Validation Errors]:", validation["errors"])

    response = build_response(
        missing,
        validation["errors"],
        parsed
    )

    state["intent"] = response
    state["status"] = response.get("status", "")

    return response