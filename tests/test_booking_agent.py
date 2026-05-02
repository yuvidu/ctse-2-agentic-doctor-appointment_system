"""Unit tests for the Booking Agent and Booking Manager."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agents.booking_agent import booking_agent
from tools.booking_tools.booking_manager import BookingManager


@pytest.fixture
def mock_state() -> dict:
    """Provides a baseline state for testing."""
    return {
        "user_input": "I need a dentist appointment",
        "availability_status": "availability_ok",
        "availability": {
            "available_slots": [
                {
                    "doctor_id": "DOC-001",
                    "start": "2024-06-01T10:00:00",
                    "end": "2024-06-01T11:00:00",
                    "location": "Main Clinic",
                    "specialty": "Dentistry",
                }
            ]
        },
        "errors": [],
    }


def test_booking_success(mock_state):
    """Success Case: Booking is saved, ID is generated, and state is updated."""
    with patch("agents.booking_agent.BookingManager") as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.is_slot_available.return_value = True
        mock_instance.finalize_booking.return_value = {
            "id": "APP-TEST1",
            "doctor_id": "DOC-001",
            "status": "confirmed",
        }

        updated_state = booking_agent(mock_state)

        assert updated_state["status"] == "confirmed"
        assert updated_state["appointment"]["id"] == "APP-TEST1"
        assert updated_state["appointment"]["status"] == "confirmed"


def test_booking_collision(mock_state):
    """Collision Case: If the checker finds a conflict, update state with error."""
    with patch("agents.booking_agent.BookingManager") as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.is_slot_available.return_value = False

        updated_state = booking_agent(mock_state)

        assert updated_state["status"] == "conflict_detected"
        assert any(e["code"] == "BOOKING_COLLISION" for e in updated_state["errors"])


def test_booking_no_slots(mock_state):
    """Validation Case: Handle state where available_slots is empty."""
    mock_state["availability"]["available_slots"] = []

    updated_state = booking_agent(mock_state)

    assert updated_state["status"] == "no_slots_available"


def test_booking_uses_availability_status_only_from_availability_agent():
    """Availability sets ``status`` (not ``availability_ok`` on a separate key)."""
    state = {
        "user_input": "Book cardiologist",
        "status": "availability_ok",
        "availability": {
            "available_slots": [
                {
                    "doctor_id": "DOC-002",
                    "start": "2024-06-02T14:00:00",
                    "end": "2024-06-02T15:00:00",
                    "location": "Clinic B",
                    "specialty": "Cardiology",
                }
            ]
        },
        "errors": [],
    }
    with patch("agents.booking_agent.BookingManager") as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.is_slot_available.return_value = True
        mock_instance.finalize_booking.return_value = {
            "id": "APP-AVAIL",
            "doctor_id": "DOC-002",
            "status": "confirmed",
        }

        updated = booking_agent(state)

        assert updated["status"] == "confirmed"
        assert updated["appointment"]["id"] == "APP-AVAIL"
        mock_instance.finalize_booking.assert_called_once()


def test_booking_retries_next_slot_on_collision(mock_state):
    """If the first ranked slot collides, try the next candidate."""
    mock_state["availability"]["available_slots"] = [
        {
            "doctor_id": "DOC-TAKEN",
            "start": "2024-06-01T10:00:00",
            "end": "2024-06-01T11:00:00",
            "location": "Main Clinic",
            "specialty": "Dentistry",
        },
        {
            "doctor_id": "DOC-FREE",
            "start": "2024-06-01T11:00:00",
            "end": "2024-06-01T12:00:00",
            "location": "Main Clinic",
            "specialty": "Dentistry",
        },
    ]
    with patch("agents.booking_agent.BookingManager") as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.is_slot_available.side_effect = [False, True]
        mock_instance.finalize_booking.return_value = {
            "id": "APP-SECOND",
            "doctor_id": "DOC-FREE",
            "start_time": "2024-06-01T11:00:00",
            "status": "confirmed",
        }

        updated_state = booking_agent(mock_state)

        assert updated_state["status"] == "confirmed"
        assert updated_state["appointment"]["id"] == "APP-SECOND"
        assert mock_instance.is_slot_available.call_count == 2
        second_call = mock_instance.finalize_booking.call_args[0][0]
        assert second_call["doctor_id"] == "DOC-FREE"


def test_booking_manager_db_ops(tmp_path):
    """Test BookingManager local file operations and ID generation."""
    test_db = tmp_path / "appointments.json"
    manager = BookingManager(db_path=str(test_db))

    details = {
        "doctor_id": "DOC-X",
        "start_time": "2024-07-01T09:00:00",
        "patient": "John Doe",
    }

    # Test availability
    assert manager.is_slot_available("DOC-X", "2024-07-01T09:00:00") is True

    # Test commit
    confirmation = manager.finalize_booking(details)
    assert confirmation["id"].startswith("APP-")
    assert confirmation["status"] == "confirmed"

    # Test collision after commit
    assert manager.is_slot_available("DOC-X", "2024-07-01T09:00:00") is False

    # Verify file content
    with open(test_db, "r") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["id"] == confirmation["id"]
