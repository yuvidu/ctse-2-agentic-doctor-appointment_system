# Healthcare MAS (CTSE Assignment 2)

Local multi-agent scaffold: **Intent** (Ollama + tools) → **Availability** (schedule file tool + optional Ollama ranking) → **Booking** (collision check + local `data/appointments.json`) → **Notification** (mock SMS/email + `data/notification_appointments.json`).

Repository layout: this folder is the **project root** (Python backend, `frontend/`, `data/`, `tests/`, `static/`). Use this tree only; see [`docs/NOTIFICATION_SINGLE_REPO.md`](docs/NOTIFICATION_SINGLE_REPO.md) if you previously used separate sibling folders (`Notification/`, `booking agent/`, etc.).

---

for local repo : 
cd "c:\Users\ASUS TUF\Desktop\CTSE 2\New folder"
$env:SPECIALIZATIONS_API_URL = "http://127.0.0.1:8010/specializations"
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010

## Prerequisites

| Tool | Notes |
|------|--------|
| **Python** | 3.11+ recommended (3.13 works with current deps). |
| **Git** | For version control and GitHub. |
| **Node.js** | 18+ (for the React frontend: `npm` / Vite). |
| **Ollama** | Local LLM runtime ([https://ollama.com](https://ollama.com)). |

Optional: **PowerShell** on Windows (commands below use PowerShell). On macOS/Linux, use the equivalent `bash`/`zsh` commands where noted.

---

## Full installation

### 1. Get the code

**Clone from GitHub** (after you have created the remote repository — see [GitHub initialization](#github-initialization)):

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

Or open an existing copy of this project and `cd` into its root (the directory that contains this `README.md`).

### 2. Python virtual environment and dependencies

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `Activate.ps1` is blocked by policy:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

(or run `python -m pip install -r requirements.txt` using the venv’s `python` path without activating).

### 3. Ollama (local models)

Install Ollama from the official site, then pull the model used by this repo:

```powershell
ollama pull llama3.2:3b
```

Ensure Ollama is **running** (`ollama serve` is usually automatic after install). Default API: `http://127.0.0.1:11434`.

If you see **403 subscription** errors, use a tag from `ollama list`, align `OLLAMA_MODEL` with your Crew/parsing config, and consider `OLLAMA_NO_CLOUD=1` (see [Ollama FAQ](https://docs.ollama.com/faq)).

### 4. React frontend dependencies

From the **repository root**:

```powershell
cd frontend
npm install
cd ..
```

### 5. Environment variables (summary)

| Variable | When to set | Purpose |
|----------|-------------|---------|
| `SPECIALIZATIONS_API_URL` | Recommended if not using default port **8000** | Intent validation calls `GET …/specializations` (must match your uvicorn URL). Example: `http://127.0.0.1:8010/specializations` |
| `VITE_DEV_API_PROXY` | `npm run dev` only, if API not on **8010** | Vite proxy target for `/api` and `/specializations`. See `frontend/.env.example`. |
| `VITE_API_BASE_URL` | Production build only if UI and API differ | Absolute API origin (no trailing slash). Usually **unset** when FastAPI serves `frontend/dist`. |
| `CREWAI_VERBOSE` | Optional | `1` / `true` — verbose CrewAI Rich logs. |
| `MAS_DEBUG` | Optional | `1` — extra intent / availability print and `logs.txt` from parsing logger. |

Create **`frontend/.env.development`** locally (do not commit secrets) if you need a custom proxy, e.g.:

```env
VITE_DEV_API_PROXY=http://127.0.0.1:8010
```

**Debugging / log noise**

- **CrewAI:** set `CREWAI_VERBOSE=1` before starting Python to show Rich crew/task panels (off by default). Restart after changing.
- **Pipeline prints:** set `MAS_DEBUG=1` for `[Agent]`, `[LOG]`, and structured stderr lines from tools (off by default).

---

## Run the application

### Backend (FastAPI + pipeline)

Use a free port (**8010** avoids common Windows issues on **8000**):

**Windows:**

```powershell
.\.venv\Scripts\Activate.ps1
$env:SPECIALIZATIONS_API_URL = "http://127.0.0.1:8010/specializations"
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

**macOS / Linux:**

```bash
source .venv/bin/activate
export SPECIALIZATIONS_API_URL="http://127.0.0.1:8010/specializations"
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

Then open **http://127.0.0.1:8010/**

- If **`frontend/dist`** exists (`npm run build` in `frontend/`), you get the **React** UI (same-origin `/api/pipeline`).
- Otherwise the server serves **`static/index.html`** (legacy demo).

**API:** `POST /api/pipeline` (`{"user_input":"..."}`) · `GET /api/health` · `GET /specializations` · `GET /api/appointments` (local `data/appointments.json`) · `DELETE /api/appointments/{id}` · `POST /api/appointments/clear` (demo reset)

**Pipeline stages (`run_system` / `POST /api/pipeline`):** when Intent returns `status: complete`, the server runs **Availability**, then **Booking** (commits first free slot to `data/appointments.json`, gitignored), then **Notification** (normalizes the booking row for mock send + appends to `data/notification_appointments.json`). If Booking does not run or does not confirm, Notification may still build a **preview** `appointment` (`PREVIEW-…`) from intent + slots. Top-level `status` stays the **Intent** outcome (`complete` / `incomplete` / `error`); booking outcome is in `booking.status` (`confirmed`, `no_slots_available`, etc.).

**Windows `WinError 10013` on port 8000:** use `--port 8010` and set `SPECIALIZATIONS_API_URL` to match. Check excluded ranges: `netsh interface ipv4 show excludedportrange protocol=tcp` (Administrator).

### React frontend (development)

With the backend running (default proxy → `8010`):

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173/** (Vite default). If the API runs on another port, set `VITE_DEV_API_PROXY` before `npm run dev` (see `frontend/.env.example`).

### React frontend (production build served by FastAPI)

```powershell
cd frontend
npm run build
cd ..
```

Restart uvicorn. The app will serve **`frontend/dist`** from `/` when `frontend/dist/index.html` exists.

### Other entrypoints

```powershell
python main.py              # CLI pipeline demo
python demo_availability.py # Availability-only demo
python -m pytest tests -v   # Tests
```

---

## GitHub initialization

These steps assume the **project root** is the folder containing `README.md`, `.gitignore`, `requirements.txt`, and `backend/`.

### 1. Initialize Git (first time only)

```powershell
cd <path-to-project-root>
git init
git branch -M main
```

### 2. Ensure `.gitignore` is present

This repo includes a root [`.gitignore`](.gitignore) (Python venv, caches, `frontend/node_modules`, local `.env` files, `logs.txt`, etc.). Verify it exists before the first commit.

### 3. First commit

```powershell
git add .
git status
git commit -m "Initial commit: Healthcare MAS scaffold"
```

### 4. Create a repository on GitHub

1. Log in to [GitHub](https://github.com).
2. **New repository** → choose a name (e.g. `healthcare-mas-ctse`) → **Create repository** (no README/license if you already have them locally).

### 5. Add remote and push

Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repository name.

**HTTPS:**

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**SSH** (if you use SSH keys):

```powershell
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

If GitHub’s default branch is `master` and you use `main`:

```powershell
git branch -M main
git push -u origin main
```

### 6. Later updates

```powershell
git add .
git commit -m "Describe your change"
git push
```

---

## Sample API prompt

```json
{"user_input": "I need a cardiologist in Colombo on 2026-05-02 in the morning."}
```

Use dates that exist in `data/sample_schedules.json` for predictable availability results.

---

## Assignment alignment (SE4010 CTSE)

| Area | Status |
|------|--------|
| Multi-agent orchestration | **LangGraph** (`orchestration/mas_workflow.py`): Intent → Availability → **Booking** → **Notification** with conditional routing; `pipeline.run_system` invokes the compiled graph. CrewAI agent stubs in `agents/crew_ai/` are legacy/reference only (runtime orchestration is LangGraph). |
| Tools | Intent tools + `fetch_doctor_availability` + **notification mock send** + **JSON storage** under `data/`. |
| State | `state_schema.State` for orchestrator dict; `schemas.state.GlobalState` for Availability slice; `integration/intent_to_availability_state.py` bridges Intent field names. |
| Observability | JSON logs on stderr from `utils/logging_utils.py` and Intent tools (gated by `MAS_DEBUG`). |
| Ollama | Local only; optional `AVAILABILITY_USE_OLLAMA=1` for slot ranking. |

---

## Docs

- [docs/AVAILABILITY_AGENT.md](docs/AVAILABILITY_AGENT.md) — Availability build guide and checklist.
