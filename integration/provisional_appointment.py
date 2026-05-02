"""Build a preview ``appointment`` dict when Booking has not run yet."""

from __future__ import annotations

import hashlib
from typing import Any


def _inner_intent(state: dict[str, Any]) -> dict[str, Any]:
    block = state.get("intent") or {}
    inner = block.get("intent")
    if isinstance(inner, dict):
        return inner
    return {}


def build_provisional_appointment(state: dict[str, Any]) -> dict[str, Any]:
    """Return ``appointment`` payload for Notification without a Booking agent.

    If ``state['appointment']`` already has ``appointment_id``, returns a shallow copy.
    Otherwise derives doctor/time from availability (structured slots or flattened strings)
    and intent fields from the Intent repo response shape.
    """
    existing = state.get("appointment")
    if isinstance(existing, dict) and existing.get("appointment_id"):
        return dict(existing)

    inner = _inner_intent(state)
    spec = str(inner.get("specialization") or inner.get("specialty") or "General Medicine").strip()
    date_hint = str(inner.get("date") or "").strip()

    avail = state.get("availability") or {}
    slots = avail.get("available_slots") or []
    doctor_id = ""
    time_iso = ""
    if slots and isinstance(slots[0], dict):
        s0 = slots[0]
        doctor_id = str(s0.get("doctor_id", "")).strip()
        time_iso = str(s0.get("start", "")).strip()

    if not doctor_id:
        doctor_id = str(state.get("doctor") or "").strip()

    if not time_iso:
        lines = state.get("available_slots") or []
        if lines and isinstance(lines[0], str):
            segs = [x.strip() for x in lines[0].split("|")]
            if segs:
                doctor_id = doctor_id or segs[0]
            if len(segs) >= 2:
                start_part = segs[1].split("–")[0].strip()
                if start_part:
                    time_iso = start_part

    if not time_iso and len(date_hint) >= 10 and date_hint[4] == "-" and date_hint[7] == "-":
        time_iso = f"{date_hint[:10]}T09:00:00"
    if not time_iso:
        time_iso = "2099-01-01T09:00:00"
    if not doctor_id:
        doctor_id = "pending-assignment"

    h = hashlib.sha256(
        (str(state.get("user_input", "")) + date_hint + spec).encode(),
        usedforsecurity=False,
    ).hexdigest()[:10]
    return {
        "appointment_id": f"PREVIEW-{h}",
        "user_name": "Guest",
        "user_contact": "n/a",
        "doctor": doctor_id,
        "specialization": spec,
        "time_iso": time_iso,
        "channel": "sms",
    }
