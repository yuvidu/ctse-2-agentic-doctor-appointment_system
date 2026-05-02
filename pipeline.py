"""Intent → Availability → Booking → Notification (importable by CLI, FastAPI, tests)."""

from __future__ import annotations

from pathlib import Path

from agents.availability_agent import availability_agent
from agents.booking_agent import booking_agent
from agents.intent_agent import intent_agent
from agents.notification_agent import notification_agent
from integration.intent_to_availability_state import global_state_from_intent_repo

_REPO_ROOT = Path(__file__).resolve().parent
_SCHEDULES = _REPO_ROOT / "data" / "sample_schedules.json"


def _booking_failure_notification_message(state: dict) -> str:
    """User-facing copy when Booking did not confirm (no mock SMS for a non-commit)."""
    bk = state.get("booking") or {}
    st = bk.get("status")
    if st == "no_slots_available":
        return "No appointment was saved: there were no bookable slots for this request."
    if st == "booking_failed":
        return "No appointment was saved: the booking could not be written. Check logs and try again."
    return (
        "No appointment was saved: that slot is no longer available. "
        "It may already exist in your local `data/appointments.json` from an earlier test—"
        "delete that file or remove the row to retry the same time."
    )


def _normalize_appointment_for_notification(state: dict) -> None:
    """Map BookingManager record (``id``, ``doctor_id``, …) to Notification ``AppointmentModel`` keys."""
    appt = state.get("appointment")
    if not isinstance(appt, dict) or appt.get("appointment_id"):
        return
    aid = appt.get("id")
    if not aid:
        return
    ib = state.get("intent") or {}
    inner = ib.get("intent") if isinstance(ib.get("intent"), dict) else ib
    if not isinstance(inner, dict):
        inner = {}
    user_name = str(inner.get("user_name") or inner.get("patient_name") or "Guest").strip() or "Guest"
    user_contact = str(inner.get("user_contact") or inner.get("phone") or "n/a").strip() or "n/a"
    state["appointment"] = {
        "appointment_id": str(aid),
        "user_name": user_name,
        "user_contact": user_contact,
        "doctor": str(appt.get("doctor_id") or appt.get("doctor") or ""),
        "specialization": str(
            appt.get("specialization") or appt.get("specialty") or "General Medicine"
        ),
        "time_iso": str(appt.get("start_time") or appt.get("time_iso") or ""),
        "channel": str(appt.get("channel") or "sms"),
    }


def run_system(user_input: str) -> dict:
    """Run Intent, Availability, Booking, then Notification when intent is complete."""
    state: dict = {
        "user_input": user_input,
        "intent": {},
        "doctor": "",
        "available_slots": [],
        "appointment": {},
        "status": "",
        "errors": [],
    }

    # Intent: ``intent_agent`` (Ollama + tools). Crew ``kickoff()`` was removed —
    # CrewAI 1.x still routed the crew runner through OpenAI and caused 500s offline.

    intent_response = intent_agent(state)
    state["intent"] = intent_response
    state["status"] = intent_response.get("status", "")
    if isinstance(intent_response.get("errors"), list):
        state["errors"] = intent_response["errors"]

    if intent_response.get("status") != "complete":
        return state

    mas_state = global_state_from_intent_repo(state)
    avail_out = availability_agent(mas_state, schedules_path=_SCHEDULES)

    state["availability"] = avail_out.get("availability")
    state["availability_status"] = avail_out.get("status")
    if avail_out.get("errors"):
        state["availability_errors"] = avail_out["errors"]
    if avail_out.get("missing_fields"):
        state["availability_missing_fields"] = avail_out["missing_fields"]

    slots = (avail_out.get("availability") or {}).get("available_slots") or []
    state["available_slots"] = [
        f"{s.get('doctor_id', '')} | {s.get('start', '')} – {s.get('end', '')} | {s.get('location', '')}"
        for s in slots
    ]
    if slots:
        state["doctor"] = str(slots[0].get("doctor_id", ""))

    state = booking_agent(state)
    _normalize_appointment_for_notification(state)

    bk = state.get("booking") or {}
    if bk.get("status") and bk.get("status") != "confirmed":
        state["notification"] = {
            "status": "skipped",
            "channel": None,
            "message": _booking_failure_notification_message(state),
            "error": None,
        }
        state["appointment"] = {}
        return state

    state = notification_agent(state)

    return state
