"""Availability Agent — tool-backed scheduling lookup."""

from __future__ import annotations

import json
import os
import urllib.error
from datetime import datetime
from pathlib import Path

from clients.ollama_chat import rank_slots_with_ollama, sanitize_ranking_indices
from schemas.state import AvailabilityPayload, ErrorEntry, GlobalState
from tools.availability_tools.schedule_availability import fetch_doctor_availability
from utils.logging_utils import log_event


def _repo_root() -> Path:
    """Repository root (directory containing ``data/``)."""
    return Path(__file__).resolve().parents[1]


def _default_schedules_path() -> Path:
    return _repo_root() / "data" / "sample_schedules.json"


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def availability_agent(
    state: GlobalState,
    *,
    schedules_path: str | Path | None = None,
) -> GlobalState:
    """Compute available appointment slots and merge into *state*."""
    out: GlobalState = dict(state)
    agent_name = "AvailabilityAgent"
    log_event(agent_name, "input", {"keys": sorted(out.keys())})

    intent = dict(out.get("intent") or {})
    missing: list[str] = list(out.get("missing_fields") or [])
    errors: list[ErrorEntry] = list(out.get("errors") or [])

    preferred_date = intent.get("preferred_date")
    specialty = intent.get("specialty")
    doctor_id = intent.get("doctor_id")
    time_window = intent.get("preferred_time_window") or "any"

    if not preferred_date:
        missing.append("intent.preferred_date")
    if not specialty and not doctor_id:
        missing.append("intent.specialty_or_doctor_id")

    if missing:
        out["missing_fields"] = sorted(set(missing))
        out["status"] = "availability_missing_input"
        log_event(agent_name, "output", {"status": out["status"], "missing": out["missing_fields"]})
        return out

    path = Path(schedules_path) if schedules_path else _default_schedules_path()
    log_event(
        agent_name,
        "tool_call",
        {
            "tool": "fetch_doctor_availability",
            "args": {
                "schedules_path": str(path),
                "specialty": specialty,
                "doctor_id": doctor_id,
                "preferred_date": preferred_date,
                "preferred_time_window": time_window,
            },
        },
    )

    try:
        slots = fetch_doctor_availability(
            schedules_path=path,
            specialty=specialty,
            doctor_id=doctor_id,
            preferred_date=str(preferred_date),
            preferred_time_window=str(time_window),
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        err: ErrorEntry = {
            "code": "AVAILABILITY_TOOL_ERROR",
            "message": str(exc),
            "agent": agent_name,
        }
        errors.append(err)
        out["errors"] = errors
        out["status"] = "availability_failed"
        log_event(agent_name, "tool_error", {"message": str(exc)})
        log_event(agent_name, "output", {"status": out["status"]})
        return out

    payload: AvailabilityPayload = {
        "queried_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": "file",
        "filters_applied": {
            "specialty": specialty,
            "doctor_id": doctor_id,
            "preferred_date": preferred_date,
            "preferred_time_window": time_window,
        },
        "available_slots": slots,
        "total_count": len(slots),
    }
    out["availability"] = payload

    if not slots:
        out["status"] = "availability_empty"
        log_event(agent_name, "output", {"status": out["status"], "total_count": 0})
        return out

    if _env_flag("AVAILABILITY_USE_OLLAMA"):
        pref = (out.get("user_input") or "").strip()
        if not pref:
            pref = str(intent.get("slot_preference_notes") or "").strip()
        if not pref:
            pref = (
                "Prefer the earliest reasonable appointment; if ties, keep tool order. "
                "Output valid JSON only."
            )
        model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b").strip() or "llama3.2:3b"
        base = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434"
        try:
            log_event(agent_name, "ollama_call", {"model": model, "n_slots": len(slots)})
            idx_raw, rationale, raw_assistant = rank_slots_with_ollama(
                slots=slots,
                user_preference=pref,
                model=model,
                base_url=base,
            )
            idx = sanitize_ranking_indices(list(idx_raw), len(slots))
            payload["ollama_ranking"] = {
                "recommended_slot_indices": idx,
                "rationale": rationale[:800],
                "model": model,
            }
            log_event(
                agent_name,
                "ollama_output",
                {
                    "indices": idx,
                    "rationale_preview": rationale[:160],
                    "assistant_preview": raw_assistant[:400],
                },
            )
            if idx:
                tail = [slots[j] for j in range(len(slots)) if j not in set(idx)]
                payload["available_slots"] = [slots[i] for i in idx] + tail
                payload["total_count"] = len(payload["available_slots"])
                out["availability"] = payload
        except (
            urllib.error.URLError,
            TimeoutError,
            ConnectionRefusedError,
            ValueError,
            KeyError,
            json.JSONDecodeError,
        ) as exc:
            log_event(agent_name, "ollama_skipped", {"reason": type(exc).__name__, "message": str(exc)[:300]})

    out["status"] = "availability_ok"
    log_event(
        agent_name,
        "output",
        {"status": out["status"], "total_count": len(out["availability"]["available_slots"])},
    )
    return out
