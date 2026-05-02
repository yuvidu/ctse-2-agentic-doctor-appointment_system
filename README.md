# Healthcare MAS (CTSE Assignment 2)

Local multi-agent scaffold: **Intent** (Ollama + tools) → **Availability** (schedule file tool + optional Ollama ranking) → Booking / Notification (your team).

## Quick start

```powershell
cd <this-repo-folder>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 1) Backend (specializations API + **web UI** + pipeline API)

From the repo root (pick a free port; **8010** avoids common Windows blocks on **8000**):

```powershell
$env:SPECIALIZATIONS_API_URL = "http://127.0.0.1:8010/specializations"
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

`SPECIALIZATIONS_API_URL` must match wherever this app serves `/specializations` (same host/port as uvicorn). If you use the default **8000** and it works, you can omit the env var.

Then open **http://127.0.0.1:8010/** (or your chosen port).

- If **`frontend/dist`** exists (after `npm run build` in `frontend/`), the server serves the **React production UI** (chat + pipeline checklist + animated background) from the same origin; it calls **`POST /api/pipeline`** and **`/specializations`** without extra CORS setup.
- If there is no build yet, it falls back to **`static/index.html`** (legacy demo).

JSON API: `POST /api/pipeline` with body `{"user_input":"..."}`.

### React frontend (dev + production)

```powershell
cd frontend
npm install
npm run dev
```

`npm run dev` runs Vite on **5173** and proxies `/api` and `/specializations` to **`http://127.0.0.1:8010`** by default (override with `VITE_DEV_API_PROXY` in `frontend/vite.config.ts`).

Production build (output `frontend/dist`, picked up by uvicorn automatically):

```powershell
cd frontend
npm run build
```

Optional: set **`VITE_API_BASE_URL`** at build time when the UI is hosted on a different origin than the API (see `frontend/.env.example`).

**Windows `WinError 10013` on port 8000:** another process may be using it, or the port sits in an excluded range. Use `--port 8010` (or `8765`, `8888`) and set `SPECIALIZATIONS_API_URL` as above. To inspect reserved ranges: `netsh interface ipv4 show excludedportrange protocol=tcp` (run as Administrator).

### 2) Ollama

Pull a **local** model (default in this repo: `llama3.2:3b`; assignment also mentions `llama3:8b`, `phi3`, `qwen`):

```powershell
ollama pull llama3.2:3b
```

If you see **403 subscription** errors, use a tag from `ollama list`, set `OLLAMA_MODEL` to match, and consider `OLLAMA_NO_CLOUD=1` (see [Ollama FAQ](https://docs.ollama.com/faq)).

### 3) Run pipeline (Intent + Availability)

```powershell
python main.py
```

### 4) Run Availability only

```powershell
python demo_availability.py
```

### 5) Tests

```powershell
python -m pytest tests -v
```

## Assignment alignment (SE4010 CTSE)

| Area | Status |
|------|--------|
| Multi-agent orchestration | CrewAI stubs + `main.py` sequential flow; **follow-up**: use a single Crew sequential process or LangGraph for all agents to avoid duplicate Intent work (Crew `kickoff` + separate `intent_agent` call). |
| Tools | Intent tools (LLM parse, validation API, etc.) + `fetch_doctor_availability` (file I/O). |
| State | `state_schema.State` for orchestrator dict; `schemas.state.GlobalState` for Availability slice; `integration/intent_to_availability_state.py` bridges Intent field names. |
| Observability | JSON logs on stderr from `utils/logging_utils.py` and Intent tools. |
| Ollama | Local only; optional `AVAILABILITY_USE_OLLAMA=1` for slot ranking. |

## Docs

- [docs/AVAILABILITY_AGENT.md](docs/AVAILABILITY_AGENT.md) — Availability build guide and checklist.
