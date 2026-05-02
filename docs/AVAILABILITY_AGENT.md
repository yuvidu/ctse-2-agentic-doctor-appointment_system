# Availability Agent — Build Guide (CTSE Assignment 2)

This document is your **single checklist** for implementing the **Availability Agent**: role, shared state, tool (real-world I/O), orchestration handoff, logging, and tests. Code lives in this **repository root** (`agents/`, `tools/availability_tools/`, `schemas/`, etc.); follow the steps in order.

---

## 1. What you are responsible for

| Item | Requirement |
|------|-------------|
| **Agent** | One agent: reads global state, validates inputs, calls tools, writes availability results back into state. |
| **Tool** | At least one **custom Python tool** with **type hints** and **docstrings** that touches the real world: local DB, file, or free HTTP API. |
| **Tests** | Automated tests: **valid**, **missing required fields**, **invalid** inputs; assert structured state + errors. |
| **Observability** | Log **agent input summary**, **every tool call** (name + args + result summary), **agent output**. |

Your teammates own Intent → Booking → Notification. You **only** own the slice between “parsed intent exists” and “booking can run.”

---

## 2. Orchestration contract (how you plug in)

**Pattern:** sequential pipeline — state dict flows: Intent → **Availability** → Booking → Notification.

Your agent should be a **pure function** (recommended for LangGraph):

```text
new_state = availability_agent(state)
```

- **Do not** mutate the input dict in place unless your team agrees; prefer `state = {**state, ...updates}`.
- **Do** only add/update keys your agent owns (see §4).

Later, LangGraph will call your function as a **node**; CrewAI can wrap the same function in a task. The assignment expects a **framework** orchestrator — keep your logic framework-agnostic inside one module.

---

## 3. Tool choice (pick one primary)

| Option | Pros | Notes |
|--------|------|--------|
| **A. JSON / SQLite file** | Zero setup, runs anywhere | Good for demo; still “real world” file I/O. |
| **B. MongoDB (local)** | Matches many healthcare demos | Install Mongo locally; tool uses `pymongo`. |
| **C. Free public API** | “Real API” story | Must work offline or document fallback; assignment forbids **paid** cloud LLM APIs — HTTP APIs are OK if free. |

**This repo’s scaffold uses Option A** (`data/sample_schedules.json`) so you can run tests immediately. Swap the tool body for MongoDB when your group finalizes infra.

---

## 4. Shared state — keys you READ and WRITE

### Keys you typically READ (from Intent / upstream)

These names are **suggestions** — align with your group’s final schema, but keep the same *idea*:

- `user_input` — raw text (optional for you).
- `intent` — structured object: `specialty`, `doctor_id`, `preferred_date`, `preferred_time_window`, `location`, etc.
- `errors` — list of `{ "code", "message", "agent" }` (append only).
- `missing_fields` — list of strings (you may append).

### Keys you WRITE (Availability Agent owns)

- `availability` — your main payload:

```json
{
  "availability": {
    "queried_at": "2026-05-01T12:00:00+05:30",
    "source": "file",
    "filters_applied": {},
    "available_slots": [
      { "doctor_id": "D001", "start": "2026-05-02T10:00:00+05:30", "end": "2026-05-02T10:30:00+05:30", "location": "Clinic A" }
    ],
    "total_count": 1
  },
  "status": "availability_ok"
}
```

- `status` — short machine-readable phase: e.g. `availability_ok`, `availability_failed`, `availability_missing_input`.
- `errors` / `missing_fields` — when validation fails.

**Rule:** Booking Agent should be able to run only if `status == "availability_ok"` and `availability.available_slots` is non-empty (or your team defines `selected_slot` here).

---

## 5. Implementation steps (do in order)

### Step 1 — Environment

From the **repository root** (this folder):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2 — Read the scaffold

| File | Purpose |
|------|---------|
| `schemas/state.py` | TypedDict for Availability slice (adjust with team). |
| `tools/availability_tools/schedule_availability.py` | **Your tool**: load schedules, query availability. |
| `agents/availability_agent.py` | **Your agent**: validate → tool → merge results. |
| `utils/logging_utils.py` | Small logger for observability. |
| `data/sample_schedules.json` | Seed data for the tool. |
| `tests/test_availability_agent.py` | Your automated tests. |

### Step 3 — Define validation rules

Before any tool call, check:

1. **Required fields** for *your* tool (e.g. `specialty` OR `doctor_id`, and a `preferred_date` or range).
2. **Sanity checks**: date not in the past (use timezone-aware datetimes if possible).
3. If something is missing → set `missing_fields`, `status = "availability_missing_input"`, **do not** call the tool (or call with partial — team choice; documenting one approach is enough).

### Step 4 — Implement the tool

- Strict types on all public functions.
- Docstring: what it does, args, returns, raises.
- Errors: return a structured error or raise `ValueError` — **agent** catches and maps to `errors[]`.

### Step 5 — Implement the agent

- Log at start: subset of state (no PHI if this were real healthcare).
- Call tool once per request (or batch if you add pagination later).
- Normalize tool output into `availability.available_slots`.
- Log at end: count of slots, status.

### Step 6 — Tests

Run:

```powershell
pytest tests/test_availability_agent.py -v
```

Cases (minimum):

| Case | What to assert |
|------|----------------|
| Valid | `status == "availability_ok"`, slots non-empty, correct doctor/specialty. |
| Missing | `status` reflects missing input, `missing_fields` populated, no slots / tool not called. |
| Invalid | bad date / unknown doctor → `errors` or empty slots with `availability_failed`. |

### Step 7 — Group integration

1. Agree on **exact** `intent` shape with Intent agent owner.
2. Export `availability_agent` for the orchestrator:

```python
from agents.availability_agent import availability_agent
```

3. In LangGraph: add a node `availability` that returns partial state update.

### Step 8 — Report / video proof

- Screenshot or log excerpt showing **tool call + result**.
- Short paragraph: **prompt/constraints** if your agent uses an SLM for ranking slots (optional); if fully deterministic, say “deterministic policy agent with tool-backed retrieval.”

---

## 6. Ollama (optional ranking step)

After the **tool** returns real candidate slots, you can turn on a local SLM to **rank** them using the same `SYSTEM_PROMPT` in `availability_agent_prompts.py`. Tool output stays the source of truth; the model only permutes order and adds `ollama_ranking` metadata.

### Enable locally

1. Install [Ollama](https://ollama.com) and **pull a model that runs on your machine** (this repo defaults to `llama3.2:3b`; the CTSE brief also names e.g. `llama3:8b`, `phi3`, `qwen`). Example:

```powershell
ollama pull llama3.2:3b
```

2. From PowerShell in the project root:

```powershell
$env:AVAILABILITY_USE_OLLAMA = "1"
$env:OLLAMA_MODEL = "llama3.2:3b"   # must match a line from `ollama list` (local digest)
# optional: $env:OLLAMA_HOST = "http://127.0.0.1:11434"
python demo_availability.py
```

3. Prefer natural-language hints via `user_input` or `intent.slot_preference_notes`.

### If you see `403 Forbidden … requires a subscription`

That message means Ollama tried to use a **cloud / paid-tier** model (or your app is pointed at a registry tag that only exists on Ollama Cloud). Fix it by staying **local**:

1. Pick a model you have **pulled locally**: run `ollama list` and set `OLLAMA_MODEL` to that **exact name** (including tag, e.g. `llama3.2:3b`, `llama3.1:8b`).
2. Pull a known-open weights bundle, e.g. `ollama pull llama3.2:3b`, then use the same string in `OLLAMA_MODEL`.
3. Optional: force local-only behaviour so Ollama does not route you through cloud-only models — set `OLLAMA_NO_CLOUD=1` (then restart the Ollama app / service), or add `"disable_ollama_cloud": true` to `%USERPROFILE%\.ollama\server.json` per [Ollama’s FAQ](https://docs.ollama.com/faq).
4. Do **not** use assignment-banned paid APIs; local Ollama + a pulled OSS model is what the brief intends.

### When disabled (default)

If `AVAILABILITY_USE_OLLAMA` is unset or `0`, the agent behaves as before: tool-only, no network calls.

### Tests

`tests/test_availability_ollama.py` mocks Ollama so CI does not need a running server.

### Assignment note

The course requires a **local SLM via Ollama** for the project overall; not every agent must call it. This ranking step is optional, but turning it on for the demo is a clear way to show **tool-first truth + SLM reasoning** on your slice. Keep tool fetch deterministic; the model only reorders among returned slots. Logs include a short preview of the assistant reply (`ollama_output` event).

---

## 7. Rubric self-check (before you say “done”)

- [ ] 3–4 agents in full system (you only build one; group integrates).
- [ ] Your agent **does not** work in isolation: reads prior `intent`, writes `availability` for Booking.
- [ ] **Custom tool** with type hints + docstrings + real I/O.
- [ ] **Global state** handoff documented (this file + `schemas/state.py` + `state_schema.py`).
- [ ] **Logging** of inputs, tool calls, outputs.
- [ ] **Tests** automated, including security-ish checks (e.g. injection in `doctor_id` rejected or escaped — see tests).

---

## 8. MongoDB swap (when the team is ready)

Replace the body of `fetch_doctor_availability` with:

1. `MongoClient("mongodb://localhost:27017")`
2. Query collection `schedules` by `doctor_id` / `specialty` / date range.
3. Return the same **list[AvailableSlotDict]** shape so Booking does not break.

Keep function signature stable — that is how you avoid integration pain.

---

## 9. Quick reference — function you expose to orchestrator

```python
def availability_agent(state: GlobalState) -> GlobalState:
    ...
```

Return the **full** updated state dict (or LangGraph-style partial update if your team standardizes on that — **pick one** with the orchestrator owner).

---

## 10. Contact points with teammates

| Owner | You need from them | You give them |
|-------|-------------------|---------------|
| Intent | Stable `intent` fields and enums | `missing_fields` you require |
| Booking | Whether they need `selected_slot` vs first slot | `availability.available_slots` schema |
| Notification | N/A upstream | Final `status` values they may branch on |

---

**End of guide.** Run the code from this repository root (see layout below).

---

## 11a. Intent + Availability in one repo

Field names from the **Intent** agent differ from Availability’s internal keys:

| Intent repo (`build_response` / LLM) | Availability (`schemas.state`) |
|--------------------------------------|------------------------------|
| `specialization` | `specialty` |
| `date` | `preferred_date` |
| `time_preference` | `preferred_time_window` (normalized to morning/afternoon/any) |

Bridge: ``integration/intent_to_availability_state.py`` → ``global_state_from_intent_repo(state)``.

**Run Intent + Availability together** (needs Ollama + FastAPI backend for specialization validation — see ``tools/intent_tools/validation_tool.py``):

```powershell
Set-Location "<path-to-this-repo>"
python main.py
```

``main.py`` calls ``intent_agent``, then (on ``status == "complete"``) calls ``availability_agent`` and writes ``availability``, ``availability_status``, and string summaries into ``available_slots``.

---

## 11. Repository layout (Availability slice)

```text
./
  docs/
    AVAILABILITY_AGENT.md
  data/
    sample_schedules.json
  schemas/
    state.py
  utils/
    logging_utils.py
  clients/
    ollama_chat.py
  agents/
    availability_agent.py
    availability_agent_prompts.py
    intent_agent.py
  tools/
    availability_tools/
      schedule_availability.py
    intent_tools/
      ...
  integration/
    intent_to_availability_state.py
  tests/
    test_availability_agent.py
    test_availability_properties.py
    test_availability_ollama.py
    test_intent_to_availability_bridge.py
  pytest.ini
  requirements.txt
  main.py
  demo_availability.py
```

Run tests from repository root:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -v
```

---

## 12. Individual coursework checklist (what *you* submit)

Use this section as a literal tick-list against the PDF’s **Individual Requirements**.

### 1) Build an Agent (prompt + persona + constraints)

- [ ] Open `agents/availability_agent_prompts.py` and **personalize** the text if your clinic story differs (keep the medical “no advice” guardrails).
- [ ] Paste `PERSONA_DESCRIPTION`, `CONSTRAINTS`, and `SYSTEM_PROMPT` into your **technical report** under *Agent Design* (trim if needed for page limits).
- [ ] In the report, add **one diagram or bullet workflow**: inputs from Intent → your validation rules → tool call → keys written to `availability` / `status`.
- [ ] If your team adds an **Ollama** step for ranking slots, use `SYSTEM_PROMPT` as the system message and log the model JSON output (still tool-first for truth).

### 2) Build a Tool (type hints + docstrings)

- [ ] Your tool is `fetch_doctor_availability` in `tools/availability_tools/schedule_availability.py` — verify docstrings stay accurate after any MongoDB swap.
- [ ] Keep **strict typing** on public functions; extend with `TypedDict` if you add fields.

### 3) Testing / Evaluation (automated script)

- [ ] **Scenario tests:** `tests/test_availability_agent.py` (valid / missing / invalid / empty / corrupt JSON).
- [ ] **Property-based tests:** `tests/test_availability_properties.py` (Hypothesis) — cite in the report as *property-based evaluation*.
- [ ] Run and save output for proof of contribution:

```powershell
python -m pytest tests/test_availability_agent.py tests/test_availability_properties.py -v > availability_eval_log.txt
```

- [ ] (Optional) Add **LLM-as-judge** only if allowed by your team’s policy: local judge model via Ollama grading JSON outputs against a rubric — not required if Hypothesis + assertions already cover “secure + accurate” for your slice.

---

## 13. Going beyond “three pytest cases” (assignment wording)

The brief asks for an **automated evaluation script** that validates **accuracy and security**. This repo gives you **pytest** with multiple assertions. For a stronger submission, add one of:

- **Hypothesis** property-based tests on `doctor_id`, dates, and window strings, or
- A small **golden-file** suite: snapshot expected `availability` JSON for fixed inputs.

Document whichever approach you pick in the group’s technical report.
