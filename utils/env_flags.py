"""Runtime toggles read from the process environment."""

from __future__ import annotations

import os


def mas_debug() -> bool:
    """Verbose prints and structured stderr logs. Off by default; set ``MAS_DEBUG=1``."""
    return os.environ.get("MAS_DEBUG", "").strip().lower() in ("1", "true", "yes")
