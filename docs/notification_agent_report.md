**Notification & Summary Agent — Technical Report Snippet**

- **Agent Role:** Notification & Summary Agent — formats a user-friendly confirmation and sends a notification (SMS/email) when an appointment is booked.
- **Files:**
  - `tools/notification_tool.py` — typed tool with `format_message()` and `send_notification()` (injectable logger for testability).
  - `agents/notification_agent.py` — agent wrapper that reads `state['appointment']`, calls the tool, updates `state['notification']` and `state['status']`.
  - `agents/notification_prompt.txt` — system prompt, constraints, and example I/O for the agent description.
  - `tests/test_notification_agent.py` — unit tests for the tool (message formatting, successful send, logger exception path).
  - `tests/test_notification_agent_integration.py` — small integration test that runs the agent end-to-end with a sample `state`.

- **Tool API (signature):**

  ```python
  def send_notification(appointment: Appointment, channel: str = "sms", logger: Callable[[str,str,Any], None] = log_event) -> NotificationResult
  ```

  - `Appointment` is a TypedDict containing `appointment_id, user_name, user_contact, doctor, specialization, time_iso, channel`.
  - `NotificationResult` is a TypedDict: `status` (`sent`|`failed`), `channel`, `message`, `error`.

- **Testing & Evaluation:**
  - Unit tests validate deterministic behavior and edge cases (logger failure). Run via `scripts/run_notification_tests.py`.
  - Integration test (`tests/test_notification_agent_integration.py`) checks that `state` is updated and notification status is `sent`.

- **Observability / Logs:**
  - Agent uses `tests/logging_tool.log_event()` to write structured logs to `logs.txt` (JSON-like entries). Include these logs as proof of LLMOps/AgentOps.

- **How to run demo locally:**

  ```powershell
  C:/Users/HP/AppData/Local/Programs/Python/Python313/python.exe scripts/demo_notification_flow.py
  ```

- **What to include in the final report:**
  - The agent's system prompt (`agents/notification_prompt.txt`) and example I/O.
  - The tool source (`tools/notification_tool.py`) showing type hints and docstrings.
  - Test outputs and sample `logs.txt` entries demonstrating observability.
