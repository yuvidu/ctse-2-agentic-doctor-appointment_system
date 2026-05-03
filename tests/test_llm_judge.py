"""LLM-as-judge smoke test (Ollama mocked — no daemon required)."""

from __future__ import annotations

from unittest.mock import patch

from agents.intent_agent import intent_agent
from tests.llm_judge import judge_output


def test_llm_judge_valid_case() -> None:
    state = {"user_input": "Book dentist tomorrow"}

    fake_parse = {
        "message": {
            "content": '{"specialization":"Dentistry","date":"2026-05-10","time_preference":"morning"}'
        }
    }
    fake_judge = {"message": {"content": "valid"}}

    with patch("tools.intent_tools.llm_parsing_tool.ollama.chat", return_value=fake_parse), patch(
        "tests.llm_judge.ollama.chat", return_value=fake_judge
    ):
        result = intent_agent(state)
        evaluation = judge_output(result)

    evaluation_clean = evaluation.lower().strip()
    assert evaluation_clean.startswith("valid") or evaluation_clean.startswith("invalid")
