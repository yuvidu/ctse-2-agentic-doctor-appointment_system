from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.logging_utils import log_event


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_storage_path() -> Path:
    return _repo_root() / "data" / "notification_appointments.json"


def save_appointment(
    appointment: dict[str, Any],
    filepath: str | Path | None = None,
) -> bool:
    """Append appointment dict to a JSON array file under ``data/``."""
    path = Path(filepath) if filepath else _default_storage_path()
    log_event("StorageTool", "save_attempt", {"appointment_id": appointment.get("appointment_id")})
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            with path.open(encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        if not isinstance(data, list):
            data = []
        data.append(appointment)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        log_event("StorageTool", "save_success", {"appointment_id": appointment.get("appointment_id")})
        return True
    except OSError as e:
        log_event("StorageTool", "save_error", {"error": str(e)})
        return False
