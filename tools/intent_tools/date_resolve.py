"""Deterministic calendar resolution for natural-language dates (on top of SLM JSON)."""

from __future__ import annotations

import re
from datetime import datetime

import dateparser
import dateparser.search as dp_search


def user_has_single_lock_iso(user_input: str) -> bool:
    """True when the user typed exactly one YYYY-MM-DD — that value must not be overridden."""
    found = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", user_input)
    unique = list(dict.fromkeys(found))
    return len(unique) == 1


def resolve_calendar_date_from_text(
    user_input: str,
    *,
    relative_base: datetime | None = None,
) -> str | None:
    """Parse the first calendar date from free text; prefer future; return YYYY-MM-DD or None."""
    text = (user_input or "").strip()
    if not text:
        return None
    base = relative_base or datetime.now()
    today = base.date()
    settings = {
        "RELATIVE_BASE": base,
        "PREFER_DATES_FROM": "future",
        "PREFER_DAY_OF_MONTH": "first",
    }
    # ``parse`` often fails on long sentences; ``search_dates`` finds embedded phrases ("next Tuesday").
    found = dp_search.search_dates(text, settings=settings) or []
    for _, dt in found:
        if dt is None:
            continue
        resolved = dt.date()
        if resolved >= today:
            return resolved.isoformat()

    dt = dateparser.parse(text, settings=settings)
    if dt is None:
        return None
    resolved = dt.date()
    if resolved < today:
        return None
    return resolved.isoformat()


def merge_dateparser_date(
    user_input: str,
    data: dict,
    *,
    relative_base: datetime | None = None,
) -> dict:
    """When the user did not lock a single ISO date, prefer dateparser over SLM ``date`` if it finds one."""
    if user_has_single_lock_iso(user_input):
        return data
    iso = resolve_calendar_date_from_text(user_input, relative_base=relative_base)
    if not iso:
        return data
    out = dict(data)
    out["date"] = iso
    return out
