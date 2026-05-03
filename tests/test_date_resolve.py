"""Unit tests for deterministic date resolution (dateparser)."""

from __future__ import annotations

from datetime import datetime

from tools.intent_tools.date_resolve import (
    merge_dateparser_date,
    resolve_calendar_date_from_text,
    user_has_single_lock_iso,
)


def test_next_tuesday_from_sunday_may_2026() -> None:
    base = datetime(2026, 5, 3, 12, 0, 0)  # Sunday
    text = "I need a cardiology appointment next Tuesday morning, preferably with Dr. Smith."
    assert resolve_calendar_date_from_text(text, relative_base=base) == "2026-05-05"


def test_merge_overrides_past_sl_date_when_no_lock_iso() -> None:
    base = datetime(2026, 5, 3, 12, 0, 0)
    text = "Book dermatology next Friday afternoon."
    out = merge_dateparser_date(
        text,
        {"specialization": "Dermatology", "date": "2020-01-01", "time_preference": "afternoon"},
        relative_base=base,
    )
    assert out["date"] == "2026-05-08"


def test_single_explicit_iso_is_not_overridden() -> None:
    text = "Book cardiology on 2026-06-10 in the morning"
    assert user_has_single_lock_iso(text) is True
    merged = merge_dateparser_date(
        text,
        {"specialization": "Cardiology", "date": "2026-06-10", "time_preference": "morning"},
    )
    assert merged["date"] == "2026-06-10"


def test_resolve_tomorrow() -> None:
    base = datetime(2026, 5, 3, 8, 0, 0)
    assert resolve_calendar_date_from_text("tomorrow morning", relative_base=base) == "2026-05-04"
