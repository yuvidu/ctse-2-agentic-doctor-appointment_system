"""Run the Availability Agent once. From repo root: ``python demo_availability.py``

Optional: ``set AVAILABILITY_USE_OLLAMA=1`` and ``OLLAMA_MODEL`` to a name from ``ollama list``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.availability_agent import availability_agent  # noqa: E402


def main() -> None:
    state = {
        "user_input": "Morning is better if possible.",
        "intent": {
            "specialty": "cardiology",
            "preferred_date": "2026-05-02",
            "preferred_time_window": "morning",
        },
    }
    out = availability_agent(state)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
