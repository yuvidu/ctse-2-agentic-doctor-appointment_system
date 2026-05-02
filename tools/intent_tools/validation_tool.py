from __future__ import annotations

import os
from typing import Dict

import requests

# Override if your API is not on 8000 (e.g. Windows WinError 10013 on port 8000).
_SPECIALIZATIONS_URL = os.environ.get(
    "SPECIALIZATIONS_API_URL",
    "http://127.0.0.1:8000/specializations",
)

# Mirrors ``backend/main.py`` when the API is unreachable (pytest / offline).
_FALLBACK_SPECIALIZATIONS: list[str] = [
    "Cardiology",
    "Dermatology",
    "Dentistry",
    "Neurology",
    "Orthopedics",
    "Pediatrics",
    "General Medicine",
    "Gynecology",
    "Psychiatry",
    "Oncology",
    "Endocrinology",
    "Gastroenterology",
    "Pulmonology",
    "Rheumatology",
    "Urology",
    "Ophthalmology",
    "ENT (Ear, Nose, Throat)",
    "Nephrology",
    "Hematology",
    "Anesthesiology",
    "Radiology",
    "Pathology",
    "Surgery (General)",
    "Neurosurgery",
    "Cardiothoracic Surgery",
]

_cached: list[str] | None = None


def get_specializations() -> list[str]:
    """Fetch from local FastAPI backend; fall back to static list if offline."""
    try:
        response = requests.get(_SPECIALIZATIONS_URL, timeout=2)
        response.raise_for_status()
        data = response.json().get("data", [])
        if isinstance(data, list) and data:
            return [str(x) for x in data]
    except (requests.RequestException, ValueError, TypeError):
        pass
    return list(_FALLBACK_SPECIALIZATIONS)


def _valid_list() -> list[str]:
    global _cached
    if _cached is None:
        _cached = get_specializations()
    return _cached


def validate_input(data: Dict) -> Dict:
    errors: list[str] = []
    valid = _valid_list()

    if "specialization" in data:
        if data["specialization"] not in valid:
            errors.append("Invalid specialization")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }
