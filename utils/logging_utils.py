from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any, Mapping

from utils.env_flags import mas_debug


def _ts() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def log_event(agent: str, event: str, payload: Mapping[str, Any] | None = None) -> None:
    """Append a single JSON log line to stderr for observability.

    Args:
        agent: Logical agent name, e.g. ``"AvailabilityAgent"``.
        event: Short event label, e.g. ``"tool_call"``, ``"output"``.
        payload: Optional structured details (must be JSON-serializable).
    """
    if not mas_debug():
        return

    record: dict[str, Any] = {"ts": _ts(), "agent": agent, "event": event}
    if payload is not None:
        record["payload"] = dict(payload)
    sys.stderr.write(json.dumps(record, default=str) + "\n")
