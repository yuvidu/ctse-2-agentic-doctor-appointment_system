from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from schemas.state import AvailabilitySlot

_DEFAULT_TZ = ZoneInfo("Asia/Colombo")


@dataclass(frozen=True)
class AvailabilityQuery:
    """Normalized inputs for schedule lookup."""

    specialty: str | None
    doctor_id: str | None
    day: date
    time_window: str


def _safe_id(value: str) -> str:
    """Return *value* if it matches a strict id pattern, else raise ValueError."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value):
        msg = "doctor_id must be alphanumeric (plus _ or -), length 1-64"
        raise ValueError(msg)
    return value


def _parse_day(value: str, tz: ZoneInfo) -> date:
    try:
        d = date.fromisoformat(value)
    except ValueError as exc:
        msg = "preferred_date must be YYYY-MM-DD"
        raise ValueError(msg) from exc
    today = datetime.now(tz).date()
    if d < today:
        msg = "preferred_date cannot be in the past"
        raise ValueError(msg)
    return d


def _slot_on_day(slot_start_iso: str, day: date, tz: ZoneInfo) -> bool:
    start = datetime.fromisoformat(slot_start_iso).astimezone(tz)
    return start.date() == day


def _in_time_window(slot_start_iso: str, window: str, tz: ZoneInfo) -> bool:
    w = (window or "any").lower().strip()
    if w == "any":
        return True
    start = datetime.fromisoformat(slot_start_iso).astimezone(tz).time()
    morning = (time(5, 0), time(12, 0))
    afternoon = (time(12, 0), time(18, 0))
    if w == "morning":
        return morning[0] <= start < morning[1]
    if w == "afternoon":
        return afternoon[0] <= start < afternoon[1]
    msg = "preferred_time_window must be one of: morning, afternoon, any"
    raise ValueError(msg)


def fetch_doctor_availability(
    *,
    schedules_path: str | Path,
    specialty: str | None = None,
    doctor_id: str | None = None,
    preferred_date: str,
    preferred_time_window: str = "any",
    tz: ZoneInfo | None = None,
) -> list[AvailabilitySlot]:
    """Load doctor schedules from a JSON file and return available slots.

    This is a **custom tool**: it performs real file I/O (no LLM). Use it from
    the Availability Agent after upstream intent fields are validated.

    Args:
        schedules_path: Path to JSON file shaped like ``data/sample_schedules.json``.
        specialty: Optional medical specialty filter (case-insensitive substring match).
        doctor_id: Optional doctor identifier; if set, must pass :func:`_safe_id`.
        preferred_date: ISO calendar date ``YYYY-MM-DD`` for which slots are returned.
        preferred_time_window: ``morning``, ``afternoon``, or ``any``.
        tz: Timezone used for "today" checks and window filtering.

    Returns:
        A list of slot dictionaries suitable for ``GlobalState["availability"]``.

    Raises:
        FileNotFoundError: If *schedules_path* does not exist.
        ValueError: For invalid ids, dates, or time windows.
        KeyError: If the JSON document is missing required top-level keys.
    """
    zone = tz or _DEFAULT_TZ
    path = Path(schedules_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    doctors = raw["doctors"]
    day = _parse_day(preferred_date, zone)
    spec = specialty.strip().lower() if specialty else None
    doc_id = _safe_id(doctor_id) if doctor_id else None

    results: list[AvailabilitySlot] = []
    for doc in doctors:
        if doc_id and doc["doctor_id"] != doc_id:
            continue
        if spec and spec not in str(doc.get("specialty", "")).lower():
            continue
        for slot in doc.get("slots", []):
            start_iso = str(slot["start"])
            if not _slot_on_day(start_iso, day, zone):
                continue
            if not _in_time_window(start_iso, preferred_time_window, zone):
                continue
            results.append(
                {
                    "doctor_id": str(doc["doctor_id"]),
                    "start": start_iso,
                    "end": str(slot["end"]),
                    "location": str(doc.get("location", "")),
                    "specialty": str(doc.get("specialty", "")),
                }
            )
    results.sort(key=lambda s: s["start"])
    return results


def seed_demo_file_if_missing(path: Path) -> None:
    """Write a minimal demo JSON file if *path* does not exist (optional helper for local runs)."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    demo = {
        "doctors": [
            {
                "doctor_id": "D001",
                "name": "Dr. Silva",
                "specialty": "cardiology",
                "location": "Clinic A",
                "slots": [
                    {
                        "start": (datetime.now(_DEFAULT_TZ) + timedelta(days=1))
                        .replace(hour=10, minute=0, second=0, microsecond=0)
                        .isoformat(),
                        "end": (datetime.now(_DEFAULT_TZ) + timedelta(days=1))
                        .replace(hour=10, minute=30, second=0, microsecond=0)
                        .isoformat(),
                    }
                ],
            }
        ]
    }
    path.write_text(json.dumps(demo, indent=2), encoding="utf-8")
