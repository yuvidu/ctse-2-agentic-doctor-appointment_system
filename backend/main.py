"""FastAPI: specializations API + web UI + Intent→Availability pipeline."""

from __future__ import annotations

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
    """Run Intent agent then Availability (Ollama + local tools)."""
    try:
        return run_system(body.user_input.strip())
    except Exception as exc:  # noqa: BLE001 — surface errors to UI
        raise HTTPException(status_code=500, detail=str(exc)) from exc


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
