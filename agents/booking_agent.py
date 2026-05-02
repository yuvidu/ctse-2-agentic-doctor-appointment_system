"""Booking Agent implementation for the Transactional Integrity Lead role."""

from __future__ import annotations

from typing import Any, Dict

from tools.booking_tools.booking_manager import BookingManager


def booking_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transactional Integrity Lead: Handles the final booking commitment.

    This agent receives the global state after the Availability Agent has
    found potential slots. It selects the best slot, performs an atomic
    collision check to prevent race conditions, and commits the booking.

    Args:
        state (Dict[str, Any]): The global orchestration state.

    Returns:
        Dict[str, Any]: The updated global state with booking status and details.
    """
    manager = BookingManager()

    # Step 1: Verify availability status
    availability_status = state.get("availability_status")
    if availability_status != "availability_ok":
        # If availability wasn't successful, we cannot proceed with booking
        return state

    # Step 2: Retrieve candidate slots from the availability payload
    # Note: We use the raw dictionary data from 'availability' for precision.
    availability = state.get("availability", {})
    slots = availability.get("available_slots", [])

    if not slots:
        state["status"] = "no_slots_available"
        return state

    # Step 3: Reasoning Logic - Select the top-ranked or first available slot.
    # In a multi-agent system, the ranking is assumed to be handled by the
    # Availability Agent (e.g., via Ollama ranking).
    selected_slot = slots[0]
    doctor_id = str(selected_slot.get("doctor_id", ""))
    start_time = str(selected_slot.get("start", ""))

    # Step 4: Atomic Collision Check
    # Verify that the slot hasn't been taken in the "race condition" window.
    if not manager.is_slot_available(doctor_id, start_time):
        state["status"] = "conflict_detected"
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({
            "code": "BOOKING_COLLISION",
            "message": f"The slot starting at {start_time} for doctor {doctor_id} is no longer available.",
            "agent": "BookingAgent"
        })
        return state

    # Step 5: Secure Booking Committer
    # If clear, structure the final record and save it.
    try:
        booking_details = {
            "doctor_id": doctor_id,
            "start_time": start_time,
            "end_time": selected_slot.get("end"),
            "location": selected_slot.get("location"),
            "specialty": selected_slot.get("specialty"),
            "user_intent": state.get("user_input", "")
        }

        confirmation = manager.finalize_booking(booking_details)

        # Step 6: Update Global State
        # Set status to confirmed and populate the appointment object.
        state["status"] = "confirmed"
        state["appointment"] = confirmation

    except Exception as e:
        state["status"] = "booking_failed"
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({
            "code": "BOOKING_ERROR",
            "message": f"Transactional commit failed: {str(e)}",
            "agent": "BookingAgent"
        })

    return state
