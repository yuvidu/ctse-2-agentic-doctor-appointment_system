"""Ensure explicit YYYY-MM-DD in user text is not overwritten by a wrong SLM date."""

from __future__ import annotations

from tools.intent_tools import llm_parsing_tool as lp


def test_explicit_iso_date_in_user_text_overrides_parsed_date() -> None:
    data = {"specialization": "Cardiology", "date": "2026-05-03", "time_preference": "morning"}
    out = lp._apply_explicit_iso_date_from_user(
        "I need a cardiology appointment on 2026-05-02 in the morning.",
        data,
    )
    assert out["date"] == "2026-05-02"


def test_two_different_dates_in_text_no_override() -> None:
    data = {"specialization": "Cardiology", "date": "2026-05-03", "time_preference": "morning"}
    out = lp._apply_explicit_iso_date_from_user(
        "Compare 2026-05-02 vs 2026-05-10 for cardiology",
        data,
    )
    assert out["date"] == "2026-05-03"
