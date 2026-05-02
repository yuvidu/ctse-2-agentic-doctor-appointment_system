# Notification & Summary Agent — Technical notes (merged repo)

**Role:** After Intent + Availability (and later Booking), format a user-facing message, append a row to local JSON storage, and mock-send SMS/email. In this codebase, **Booking is not wired yet**: a **preview** `appointment` (`PREVIEW-…`) is built in [`integration/provisional_appointment.py`](../integration/provisional_appointment.py) when `state["appointment"]` is empty.

## Layout (single repository root)

| Piece | Path |
|--------|------|
| Agent | [`agents/notification_agent.py`](../agents/notification_agent.py) |
| System prompt | [`agents/notification_prompt.txt`](../agents/notification_prompt.txt) |
| Mock send tool | [`tools/notification_tools/notification_tool.py`](../tools/notification_tools/notification_tool.py) |
| JSON storage tool | [`tools/notification_tools/storage_tool.py`](../tools/notification_tools/storage_tool.py) — default file `data/notification_appointments.json` (gitignored) |
| Pipeline wiring | [`pipeline.py`](../pipeline.py) calls `notification_agent` after availability when Intent is `complete` |

## Tool API

`send_notification(appointment: Mapping[str, Any], message: str, channel: str = "sms", logger=...) -> NotificationResult`

- `NotificationResult`: `status` (`sent` \| `failed`), `channel`, `message`, `error`.
- Default `logger` is [`utils.logging_utils.log_event`](../utils/logging_utils.py) (stderr JSON when `MAS_DEBUG=1`).

## Pipeline contract

- Top-level **`state["status"]`** remains the **Intent** outcome (`complete` / `incomplete` / `error`). Notification writes **`state["notification"]`** only.
- Typed slice: [`schemas.state.NotificationPayload`](../schemas/state.py).

## Run tests

```powershell
python -m pytest tests/test_notification_tool.py tests/test_provisional_appointment.py tests/test_notification_integration.py tests/test_notification_judge.py -v
```

Or: `python scripts/run_notification_tests.py`

## Demo script

```powershell
python scripts/demo_notification_flow.py
```
