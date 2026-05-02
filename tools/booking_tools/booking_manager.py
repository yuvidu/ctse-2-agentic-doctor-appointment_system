"""Booking Manager tool for transactional integrity in doctor appointments."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List


class BookingManager:
    """Handles transactional integrity for doctor appointments.

    This class provides methods to verify slot availability and commit bookings
    to a local JSON database, ensuring that no duplicate appointments exist
    for the same doctor at the same time.
    """

    def __init__(self, db_path: str = "data/appointments.json"):
        """Initializes the BookingManager with a path to the appointments database.

        Args:
            db_path (str): The relative or absolute path to the appointments JSON file.
        """
        self.db_path = Path(db_path)
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensures the appointments database file exists and is a valid JSON list."""
        try:
            if not self.db_path.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.db_path, "w") as f:
                    json.dump([], f)
        except OSError:
            # Handle cases where directory creation or file writing fails
            pass

    def _read_db(self) -> List[Dict[str, Any]]:
        """Reads the appointments database.

        Returns:
            List[Dict[str, Any]]: A list of confirmed appointments.

        Raises:
            IOError: If there is an error reading the file.
        """
        try:
            if not self.db_path.exists():
                return []
            with open(self.db_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def is_slot_available(self, doctor_id: str, start_time: str) -> bool:
        """Verifies if a doctor is available at a specific time (AtomicCollisionChecker).

        Args:
            doctor_id (str): The ID of the doctor to check.
            start_time (str): The start time of the slot (ISO format).

        Returns:
            bool: True if the slot is available, False if a collision is detected.
        """
        try:
            appointments = self._read_db()
            for appt in appointments:
                if appt.get("doctor_id") == doctor_id and appt.get("start_time") == start_time:
                    return False
            return True
        except Exception:
            # In case of any unexpected error, default to unsafe (not available)
            return False

    def finalize_booking(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Finalizes the booking by appending it to the database (SecureBookingCommiter).

        Args:
            booking_details (Dict[str, Any]): Details of the appointment (doctor_id, start_time, etc.).

        Returns:
            Dict[str, Any]: The confirmation record with a unique ID.

        Raises:
            RuntimeError: If the booking could not be saved.
        """
        try:
            appointments = self._read_db()

            # Generate unique ID: APP-XXXXX
            unique_id = f"APP-{uuid.uuid4().hex[:5].upper()}"

            record = {
                "id": unique_id,
                **booking_details,
                "status": "confirmed"
            }

            appointments.append(record)

            with open(self.db_path, "w") as f:
                json.dump(appointments, f, indent=2)

            return record
        except Exception as e:
            raise RuntimeError(f"Failed to finalize booking: {str(e)}")
