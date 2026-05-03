"""Pick schedule dates on or after today (Asia/Colombo) so availability tests stay stable."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

_TZ = ZoneInfo("Asia/Colombo")


def preferred_date_on_or_after_today(schedules_path: Path, *, specialty: str, morning_only: bool = False) -> str:
    """Earliest date in *schedules_path* for *specialty* with at least one slot (optional morning-only)."""
    today = datetime.now(_TZ).date()
    raw = json.loads(schedules_path.read_text(encoding="utf-8"))
    spec_lower = specialty.lower().strip()
    best: datetime | None = None
    for doc in raw["doctors"]:
        if spec_lower not in str(doc.get("specialty", "")).lower():
            continue
        for slot in doc.get("slots", []):
            start = datetime.fromisoformat(str(slot["start"]))
            if start.tzinfo is None:
                start = start.replace(tzinfo=_TZ)
            else:
                start = start.astimezone(_TZ)
            if morning_only and not (5 <= start.hour < 12):
                continue
            d = start.date()
            if d < today:
                continue
            if best is None or start < best:
                best = start
    if best is None:
        pytest.skip(f"No {'morning ' if morning_only else ''}slot for {specialty!r} on or after today in schedules")
    return best.date().isoformat()
