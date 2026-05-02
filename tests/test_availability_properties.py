"""Property-based evaluation for Availability Agent."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from agents.availability_agent import availability_agent
from schemas.state import GlobalState
from tools.availability_tools.schedule_availability import fetch_doctor_availability


def _schedules_file() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "sample_schedules.json"


@settings(max_examples=80, deadline=None)
@given(
    junk=st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=1,
        max_size=48,
    )
)
def test_property_malformed_doctor_id_never_succeeds_status(junk: str) -> None:
    assume(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", junk) is None)
    state: GlobalState = {
        "intent": {"doctor_id": junk, "preferred_date": "2026-05-02"},
    }
    out = availability_agent(state, schedules_path=_schedules_file())
    assert out["status"] in ("availability_failed", "availability_missing_input")


@settings(max_examples=60, deadline=None)
@given(
    window=st.sampled_from(["morning", "afternoon", "any"]),
    specialty=st.sampled_from(["cardiology", "dermatology", "CARDIOLOGY"]),
)
def test_property_specialty_window_never_crash(window: str, specialty: str) -> None:
    state: GlobalState = {
        "intent": {
            "specialty": specialty,
            "preferred_date": "2026-05-02",
            "preferred_time_window": window,
        }
    }
    out = availability_agent(state, schedules_path=_schedules_file())
    assert out["status"] in (
        "availability_ok",
        "availability_empty",
        "availability_missing_input",
        "availability_failed",
    )
    if out["status"] == "availability_ok":
        assert out["availability"]["total_count"] >= 1


@settings(max_examples=40, deadline=None)
@given(note=st.text(min_size=1, max_size=120))
def test_property_specialty_free_text_does_not_escape_tool(note: str) -> None:
    state: GlobalState = {
        "intent": {"specialty": note, "preferred_date": "2026-05-02"},
    }
    out = availability_agent(state, schedules_path=_schedules_file())
    assert out["status"] in (
        "availability_ok",
        "availability_empty",
        "availability_failed",
        "availability_missing_input",
    )


def test_property_tool_invalid_date_raises() -> None:
    with pytest.raises(ValueError):
        fetch_doctor_availability(
            schedules_path=_schedules_file(),
            specialty="cardiology",
            preferred_date="not-a-date",
        )
