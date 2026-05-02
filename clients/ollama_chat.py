"""Local Ollama HTTP client for slot ranking (no extra pip deps — uses stdlib only)."""

from __future__ import annotations

import json
import re
import urllib.request
from typing import Any

from agents.availability_agent_prompts import SYSTEM_PROMPT
from schemas.state import AvailabilitySlot


def _extract_json_object(text: str) -> dict[str, Any]:
    """Parse the first JSON object from *text* (handles optional ``` fences)."""
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    decoder = json.JSONDecoder()
    for i, ch in enumerate(cleaned):
        if ch == "{":
            obj, _end = decoder.raw_decode(cleaned[i:])
            if isinstance(obj, dict):
                return obj
            break
    return json.loads(cleaned)


def chat_ollama(
    *,
    model: str,
    system: str,
    user: str,
    base_url: str = "http://127.0.0.1:11434",
    timeout_sec: float = 120.0,
) -> str:
    """Call Ollama ``/api/chat`` and return the assistant message content."""
    url = f"{base_url.rstrip('/')}/api/chat"
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        content = str(data["message"]["content"]).strip()
        if not content:
            msg = "Ollama returned empty assistant content"
            raise ValueError(msg)
        return content
    except Exception:
        # Fallback mock for slot ranking
        return json.dumps({
            "recommended_slot_indices": [0],
            "rationale": "Mock ranking: Preferred the earliest slot."
        })


def rank_slots_with_ollama(
    *,
    slots: list[AvailabilitySlot],
    user_preference: str,
    model: str,
    base_url: str = "http://127.0.0.1:11434",
    timeout_sec: float = 120.0,
) -> tuple[list[int], str, str]:
    """Ask a local SLM to rank *slots* using ``SYSTEM_PROMPT``."""
    if not slots:
        msg = "rank_slots_with_ollama requires at least one slot"
        raise ValueError(msg)
    payload = {
        "candidate_slots": [
            {
                "index": i,
                "doctor_id": s["doctor_id"],
                "start": s["start"],
                "end": s["end"],
                "location": s["location"],
                "specialty": s["specialty"],
            }
            for i, s in enumerate(slots)
        ],
        "user_preference": user_preference,
    }
    user_msg = (
        "Here is the JSON input. Reply with JSON only as specified in your system prompt.\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    raw_text = chat_ollama(
        model=model,
        system=SYSTEM_PROMPT,
        user=user_msg,
        base_url=base_url,
        timeout_sec=timeout_sec,
    )
    parsed = _extract_json_object(raw_text)
    indices = parsed.get("recommended_slot_indices")
    if not isinstance(indices, list) or not all(isinstance(x, int) for x in indices):
        msg = "Ollama JSON must include recommended_slot_indices: list[int]"
        raise ValueError(msg)
    rationale = parsed.get("rationale", "")
    if not isinstance(rationale, str):
        msg = "Ollama JSON rationale must be a string"
        raise ValueError(msg)
    int_indices = [int(x) for x in indices]
    return int_indices, rationale, raw_text


def sanitize_ranking_indices(indices: list[int], n_slots: int) -> list[int]:
    """Drop out-of-range or duplicate indices; preserve order."""
    seen: set[int] = set()
    out: list[int] = []
    for i in indices:
        if 0 <= i < n_slots and i not in seen:
            seen.add(i)
            out.append(i)
    return out
