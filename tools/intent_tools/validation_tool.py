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

# LLMs often return job titles or colloquial terms instead of the official specialty string.
_SPECIALTY_ALIASES: dict[str, str] = {
    "cardiologist": "Cardiology",
    "cardiologists": "Cardiology",
    "cardiac": "Cardiology",
    "heart doctor": "Cardiology",
    "heart specialist": "Cardiology",
    "dermatologist": "Dermatology",
    "dentist": "Dentistry",
    "dental": "Dentistry",
    "neurologist": "Neurology",
    "orthopedist": "Orthopedics",
    "orthopaedic": "Orthopedics",
    "orthopedic": "Orthopedics",
    "orthopaedics": "Orthopedics",
    "pediatrician": "Pediatrics",
    "paediatrician": "Pediatrics",
    "gp": "General Medicine",
    "general practitioner": "General Medicine",
    "internist": "General Medicine",
    "psychiatrist": "Psychiatry",
    "oncologist": "Oncology",
    "endocrinologist": "Endocrinology",
    "gastroenterologist": "Gastroenterology",
    "pulmonologist": "Pulmonology",
    "rheumatologist": "Rheumatology",
    "urologist": "Urology",
    "ophthalmologist": "Ophthalmology",
    "eye doctor": "Ophthalmology",
    "nephrologist": "Nephrology",
    "hematologist": "Hematology",
    "haematologist": "Hematology",
    "anesthesiologist": "Anesthesiology",
    "anaesthesiologist": "Anesthesiology",
    "radiologist": "Radiology",
    "pathologist": "Pathology",
    "neurosurgeon": "Neurosurgery",
    "cardiothoracic surgeon": "Cardiothoracic Surgery",
    "ent": "ENT (Ear, Nose, Throat)",
    "ear nose throat": "ENT (Ear, Nose, Throat)",
    "otolaryngologist": "ENT (Ear, Nose, Throat)",
}


def get_specializations() -> list[str]:
    """Fetch from local FastAPI backend; merge with fallback so a partial/wrong proxy never drops names."""
    api: list[str] = []
    try:
        response = requests.get(_SPECIALIZATIONS_URL, timeout=2)
        response.raise_for_status()
        data = response.json().get("data", [])
        if isinstance(data, list) and data:
            api = [str(x) for x in data]
    except (requests.RequestException, ValueError, TypeError):
        pass

    merged: dict[str, str] = {v.lower(): v for v in _FALLBACK_SPECIALIZATIONS}
    for s in api:
        merged[str(s).strip().lower()] = str(s).strip()
    return list(merged.values())


def _valid_list() -> list[str]:
    global _cached
    if _cached is None:
        _cached = get_specializations()
    return _cached


def _canonicalize_specialization(data: Dict) -> None:
    """Mutate ``data`` so ``specialization`` matches an allowed name (casing + common aliases)."""
    raw = data.get("specialization")
    if raw is None or (isinstance(raw, str) and not str(raw).strip()):
        return
    spec = str(raw).strip()
    valid = _valid_list()
    by_lower = {v.lower(): v for v in valid}
    sl = " ".join(spec.lower().split())

    alias_target = _SPECIALTY_ALIASES.get(sl)
    if alias_target:
        key = alias_target.lower()
        if key in by_lower:
            data["specialization"] = by_lower[key]
            return

    canon = by_lower.get(sl)
    if canon:
        data["specialization"] = canon


def validate_input(data: Dict) -> Dict:
    errors: list[str] = []
    valid = _valid_list()

    if "specialization" in data:
        _canonicalize_specialization(data)
        if data["specialization"] not in valid:
            errors.append("Invalid specialization")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }
