"""Shared booking/notification helpers and schedules path (used by LangGraph nodes + docs)."""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEDULES_PATH = _REPO_ROOT / "data" / "sample_schedules.json"


def booking_failure_notification_message(state: dict) -> str:
    """User-facing copy when Booking did not confirm (no mock SMS for a non-commit)."""
    bk = state.get("booking") or {}
    st = bk.get("status")
    detail = bk.get("detail")
    if st == "skipped" and detail == "availability_failed":
        return (
            "No appointment was saved: the schedule lookup failed "
            "(invalid date, bad request, or file error). Fix the request and try again."
        )
    if st == "skipped" and detail == "availability_missing_input":
        return "No appointment was saved: required fields were missing for availability search."
    if st == "skipped" and detail in ("availability_not_ready", None):
        return (
            "No appointment was saved: availability did not complete. "
            "Check intent fields and try again."
        )
    if st == "skipped":
        return f"No appointment was saved: booking was skipped ({detail!r})."
    if st == "no_slots_available":
        fa = bk.get("filters_applied") if isinstance(bk.get("filters_applied"), dict) else {}
        if fa:
            return (
                "No appointment was saved: no slots in `sample_schedules.json` match "
                f"specialty={fa.get('specialty')!r}, date={fa.get('preferred_date')!r}, "
                f"time window={fa.get('preferred_time_window')!r}. Try another day or window."
            )
        return "No appointment was saved: there were no bookable slots for this request."
    if st == "booking_failed":
        return "No appointment was saved: the booking could not be written. Check logs and try again."
    return (
        "No appointment was saved: that slot is no longer available. "
        "It may already exist in your local `data/appointments.json` from an earlier test—"
        "delete that file or remove the row to retry the same time."
    )


def normalize_appointment_for_notification(state: dict) -> None:
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
