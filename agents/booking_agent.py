"""Booking Agent implementation for the Transactional Integrity Lead role."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from tools.booking_tools.booking_manager import BookingManager

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_APPOINTMENTS_DB = _REPO_ROOT / "data" / "appointments.json"


def _availability_ready(state: Dict[str, Any]) -> bool:
    """True when Availability succeeded.

    ``availability_agent`` sets top-level ``status`` to ``availability_ok``.
    The pipeline may also copy that into ``availability_status`` on a merged dict.
    Accept either so booking runs when wired to raw Availability output.
    """
    if state.get("availability_status") == "availability_ok":
        return True
    return state.get("status") == "availability_ok"


def booking_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transactional Integrity Lead: Handles the final booking commitment.

    This agent receives the global state after the Availability Agent has
    found potential slots. It selects the best slot, performs an atomic
    collision check to prevent race conditions, and commits the booking.

    If the first choice is taken (collision), it retries with the next
    candidate slot in Availability order (e.g. Ollama-ranked list).

    Args:
        state (Dict[str, Any]): The global orchestration state.

    Returns:
        Dict[str, Any]: The updated global state with booking status and details.
    """
    manager = BookingManager(db_path=str(_DEFAULT_APPOINTMENTS_DB))

    if not _availability_ready(state):
        return state

    availability = state.get("availability") or {}
    slots: list[dict[str, Any]] = list(availability.get("available_slots") or [])

    if not slots:
        state["status"] = "no_slots_available"
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

        booking_details: Dict[str, Any] = {
            "doctor_id": doctor_id,
            "start_time": start_time,
            "end_time": selected_slot.get("end"),
            "location": selected_slot.get("location"),
            "specialty": selected_slot.get("specialty"),
            "user_intent": state.get("user_input", ""),
        }

        try:
            confirmation = manager.finalize_booking(booking_details)
            state["status"] = "confirmed"
            state["appointment"] = confirmation
            return state
        except Exception as e:  # noqa: BLE001 — surface as booking_failed after retries
            last_commit_error = str(e)
            continue

    if last_commit_error:
        state["status"] = "booking_failed"
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({
            "code": "BOOKING_ERROR",
            "message": f"Transactional commit failed after trying {len(slots)} slot(s): {last_commit_error}",
            "agent": "BookingAgent",
        })
        return state

    state["status"] = "conflict_detected"
    if "errors" not in state:
        state["errors"] = []
    summary = (
        collision_messages[0]
        if len(collision_messages) == 1
        else "All candidate slots are already booked."
    )
    state["errors"].append({
        "code": "BOOKING_COLLISION",
        "message": summary,
        "agent": "BookingAgent",
    })
    return state
