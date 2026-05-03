# Simple setup — run the project

Use **two terminals**: **Terminal A** = API (Python), **Terminal B** = UI (**Vite**, default).

All paths below assume you are in the **project root** (the folder that contains `simple-readme.md`, `backend/`, `frontend/`, and `requirements.txt`).

---

## One time only (first machine / fresh clone)

**1. Python packages**

```powershell
cd "C:\Users\ASUS TUF\Desktop\CTSE 2\New folder"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**2. Frontend packages**

```powershell
cd "C:\Users\ASUS TUF\Desktop\CTSE 2\New folder\frontend"
npm install
```

**3. Ollama (local LLM)**

Install [Ollama](https://ollama.com), then:

```powershell
ollama pull llama3.2:3b
```

Leave Ollama running in the background (usual on Windows after install).

---

## Every run — Terminal A (API on port **8010**)

Always set `SPECIALIZATIONS_API_URL` so intent validation hits **your** API (same port as uvicorn).

### A) Normal (quiet logs)

```powershell
cd "C:\Users\ASUS TUF\Desktop\CTSE 2\New folder"
.\.venv\Scripts\Activate.ps1
$env:SPECIALIZATIONS_API_URL = "http://127.0.0.1:8010/specializations"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
or


Set-Location "c:\Users\ASUS TUF\Documents\GitHub\ctse-2-agentic-doctor-appointment_system"
$env:SPECIALIZATIONS_API_URL = "http://127.0.0.1:8010/specializations"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

### B) MAS debug (prints + JSON lines on stderr for tracing)

Same as **A**, but add:

```powershell
$env:MAS_DEBUG = "1"
```

Full block:

```powershell
cd "C:\Users\ASUS TUF\Desktop\CTSE 2\New folder"
.\.venv\Scripts\Activate.ps1
$env:SPECIALIZATIONS_API_URL = "http://127.0.0.1:8010/specializations"
$env:MAS_DEBUG = "1"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

### C) MAS debug + **Ollama slot ranking** (availability re-orders slots)

Same as **B**, plus:

```powershell
$env:AVAILABILITY_USE_OLLAMA = "1"
$env:OLLAMA_MODEL = "llama3.2:3b"
$env:OLLAMA_HOST = "http://127.0.0.1:11434"
```

Full block:

```powershell
cd "C:\Users\ASUS TUF\Desktop\CTSE 2\New folder"
.\.venv\Scripts\Activate.ps1
$env:SPECIALIZATIONS_API_URL = "http://127.0.0.1:8010/specializations"
$env:MAS_DEBUG = "1"
$env:AVAILABILITY_USE_OLLAMA = "1"
$env:OLLAMA_MODEL = "llama3.2:3b"
$env:OLLAMA_HOST = "http://127.0.0.1:11434"
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

---

## Every run — Terminal B (**Vite** frontend — default UI)

**Default:** dev server on **http://127.0.0.1:5173/** (proxies `/api` to **8010**).

```powershell
cd "C:\Users\ASUS TUF\Desktop\CTSE 2\New folder\frontend"
npm run dev
```

Open in the browser: **http://127.0.0.1:5173/**

If your API is **not** on `8010`, create `frontend/.env.development`:

```env
VITE_DEV_API_PROXY=http://127.0.0.1:YOUR_PORT
```

Then run `npm run dev` again.

---

## Quick checks

| What | URL |
|------|-----|
| UI (Vite) | http://127.0.0.1:5173/ |
| API health | http://127.0.0.1:8010/api/health |

---

## Optional: one server only (no Vite)

Build the UI once, then only run **Terminal A**; open **http://127.0.0.1:8010/**

```powershell
cd "C:\Users\ASUS TUF\Desktop\CTSE 2\New folder\frontend"
npm run build
```

Restart uvicorn after `frontend/dist` exists.

---

## Tip for demos

Use a **real future date** in the chat text (must exist in `data/sample_schedules.json`), e.g. cardiology on **2026-05-05** morning, so availability does not fail on “date in the past.”
