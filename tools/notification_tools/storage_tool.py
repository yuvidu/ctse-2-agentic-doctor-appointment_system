import json
import os
from tools.notification_tools.logging_tool import log_event

STORAGE_FILE = "appointments.json"

def save_appointment(appointment: dict, filepath: str = STORAGE_FILE) -> bool:
    """Saves the appointment details to a local JSON file to persist state.

    Args:
        appointment: The appointment data dictionary.
        filepath: The path to the JSON storage file.

    Returns:
        True if successful, False otherwise.
    """
    log_event("StorageTool", "save_attempt", {"appointment_id": appointment.get("appointment_id")})
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        data.append(appointment)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        log_event("StorageTool", "save_success", {"appointment_id": appointment.get("appointment_id")})
        return True
    except Exception as e:
        log_event("StorageTool", "save_error", {"error": str(e)})
        return False
