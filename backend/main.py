"""FastAPI: specializations API + web UI + Intent→Availability→Booking→Notification pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from pipeline import run_system  # noqa: E402

app = FastAPI(title="Healthcare MAS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SPECIALIZATIONS = [
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

_STATIC_INDEX = _REPO / "static" / "index.html"
_FRONTEND_DIST = _REPO / "frontend" / "dist"
_APPOINTMENTS_JSON = _REPO / "data" / "appointments.json"


def _read_appointments_list() -> list:
    if not _APPOINTMENTS_JSON.is_file():
        return []
    try:
        raw = json.loads(_APPOINTMENTS_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return raw if isinstance(raw, list) else []


def _write_appointments_list(rows: list) -> None:
    _APPOINTMENTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    _APPOINTMENTS_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")


class PipelineRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=4000)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/specializations")
def get_specializations() -> dict[str, list[str]]:
    return {"data": SPECIALIZATIONS}


@app.post("/api/pipeline")
def run_pipeline(body: PipelineRequest) -> dict:
    """Run Intent, Availability, Booking, then Notification (Ollama + local tools)."""
    try:
        return run_system(body.user_input.strip())
    except Exception as exc:  # noqa: BLE001 — surface errors to UI
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/appointments")
def list_appointments() -> dict:
    """Return confirmed rows from ``data/appointments.json`` (local demo DB)."""
    return {"appointments": _read_appointments_list()}


@app.delete("/api/appointments/{appt_id}")
def delete_appointment(appt_id: str) -> dict:
    """Remove one booking by its ``id`` (e.g. ``APP-A1B2C``)."""
    appt_id = appt_id.strip()
    if not appt_id:
        raise HTTPException(status_code=400, detail="Missing appointment id")
    rows = _read_appointments_list()
    new_rows = [r for r in rows if isinstance(r, dict) and str(r.get("id", "")) != appt_id]
    if len(new_rows) == len(rows):
        raise HTTPException(status_code=404, detail="Appointment not found")
    _write_appointments_list(new_rows)
    return {"ok": True, "deleted": appt_id}


@app.post("/api/appointments/clear")
def clear_appointments() -> dict:
    """Reset the local bookings file (demo / QA)."""
    _write_appointments_list([])
    return {"ok": True, "cleared": True}


def _serve_legacy_static() -> FileResponse:
    if not _STATIC_INDEX.is_file():
        raise HTTPException(status_code=404, detail="static/index.html missing")
    return FileResponse(_STATIC_INDEX, media_type="text/html")


if (_FRONTEND_DIST / "index.html").is_file():
    # Production UI: `npm run build` in `frontend/` (Vite + React). Served after API routes.
    app.mount(
        "/",
        StaticFiles(directory=str(_FRONTEND_DIST), html=True),
        name="frontend_spa",
    )
else:

    @app.get("/")
    def serve_ui() -> FileResponse:
        return _serve_legacy_static()
