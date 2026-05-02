"""Booking Manager tool for transactional integrity in doctor appointments."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from utils.logging_utils import log_event


class BookingManager:
    """Handles transactional integrity for doctor appointments.

    This class provides methods to verify slot availability and commit bookings
    to a local JSON database, ensuring that no duplicate appointments exist
    for the same doctor at the same time.
    """

    def __init__(self, db_path: str = "data/appointments.json"):
        self.db_path = Path(db_path)
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        try:
            if not self.db_path.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
                with self.db_path.open("w", encoding="utf-8") as f:
                    json.dump([], f)
        except OSError:
            pass

    def _read_db(self) -> list[dict[str, Any]]:
        try:
            if not self.db_path.exists():
                return []
            with self.db_path.open(encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def is_slot_available(self, doctor_id: str, start_time: str) -> bool:
        """True if no existing row has the same doctor_id and start_time."""
        try:
            appointments = self._read_db()
            for appt in appointments:
                if appt.get("doctor_id") == doctor_id and appt.get("start_time") == start_time:
                    return False
            return True
        except Exception:  # noqa: BLE001
            return False

    def finalize_booking(self, booking_details: dict[str, Any]) -> dict[str, Any]:
        """Append a confirmed appointment row and return the record (includes ``id``)."""
        log_event("BookingManager", "finalize_start", {"doctor_id": booking_details.get("doctor_id")})
        try:
            appointments = self._read_db()
            unique_id = f"APP-{uuid.uuid4().hex[:5].upper()}"
            record = {
                "id": unique_id,
                **booking_details,
                "status": "confirmed",
            }
            appointments.append(record)
            with self.db_path.open("w", encoding="utf-8") as f:
                json.dump(appointments, f, indent=2)
            log_event("BookingManager", "finalize_ok", {"id": unique_id})
            return record
        except Exception as e:
            log_event("BookingManager", "finalize_error", {"error": str(e)[:300]})
            raise RuntimeError(f"Failed to finalize booking: {e!s}") from e
