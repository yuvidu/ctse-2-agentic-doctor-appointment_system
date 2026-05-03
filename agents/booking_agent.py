"""Booking Agent — transactional slot commit (local JSON DB)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.booking_tools.booking_manager import BookingManager

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_APPOINTMENTS_DB = _REPO_ROOT / "data" / "appointments.json"


def _availability_ready(state: dict[str, Any]) -> bool:
    """True when Availability finished the lookup (ok or empty). Not ready on tool/missing-input failures."""
    av = state.get("availability_status")
    if av in ("availability_ok", "availability_empty"):
        return True
    return state.get("status") in ("availability_ok", "availability_empty")


def booking_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Pick first free slot, collision-check, commit to ``data/appointments.json``.

    Does **not** overwrite top-level ``state["status"]`` (Intent stays ``complete`` for the UI).
    Writes ``state["booking"]`` with ``confirmed`` / ``no_slots_available`` / etc.
    """
    manager = BookingManager(db_path=str(_DEFAULT_APPOINTMENTS_DB))

    if not _availability_ready(state):
        detail = str(state.get("availability_status") or "availability_not_ready")
        state["booking"] = {"status": "skipped", "detail": detail}
        state["appointment"] = {}
        return state

    availability = state.get("availability") or {}
    slots: list[dict[str, Any]] = list(availability.get("available_slots") or [])

    if not slots:
        state["booking"] = {
            "status": "no_slots_available",
            "filters_applied": (availability.get("filters_applied") or {}),
        }
        return state

    collision_messages: list[str] = []
    last_commit_error: str | None = None

    for selected_slot in slots:
        doctor_id = str(selected_slot.get("doctor_id", "")).strip()
        start_time = str(selected_slot.get("start", "")).strip()
        if not doctor_id or not start_time:
            continue

        if not manager.is_slot_available(doctor_id, start_time):
            collision_messages.append(
                f"Slot {start_time} for doctor {doctor_id} is no longer available."
            )
            continue

        booking_details: dict[str, Any] = {
            "doctor_id": doctor_id,
            "start_time": start_time,
            "end_time": selected_slot.get("end"),
            "location": selected_slot.get("location"),
            "specialty": selected_slot.get("specialty"),
            "user_intent": state.get("user_input", ""),
        }

        try:
            confirmation = manager.finalize_booking(booking_details)
            state["booking"] = {"status": "confirmed", "appointment_id": confirmation.get("id")}
            state["appointment"] = confirmation
            return state
        except Exception as e:  # noqa: BLE001
            last_commit_error = str(e)
            continue

    if last_commit_error:
        state["booking"] = {"status": "booking_failed", "detail": last_commit_error}
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(
            {
                "code": "BOOKING_ERROR",
                "message": (
                    f"Transactional commit failed after trying {len(slots)} slot(s): {last_commit_error}"
                ),
                "agent": "BookingAgent",
            }
        )
        return state

    summary = (
        collision_messages[0]
        if len(collision_messages) == 1
        else "All candidate slots are already booked."
    )
    state["booking"] = {"status": "conflict_detected", "detail": summary}
    if "errors" not in state:
        state["errors"] = []
    state["errors"].append(
        {
            "code": "BOOKING_COLLISION",
            "message": summary,
            "agent": "BookingAgent",
        }
    )
    return state
