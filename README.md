# TimeScope

**TimeScope** is an employee monitoring and time tracking system with a FastAPI backend, Streamlit web UI, and a macOS desktop client for system monitoring and screenshot capture.

## Overview

- **Backend & Web UI** (`timeScope/`) — REST API (employees, projects, time tracking, screenshots) plus a Streamlit admin and user dashboard.
- **Desktop Client** (`tkinter_app/`) — macOS Tkinter app that tracks time, captures screenshots, and monitors app/website usage while syncing with the backend.

## Architecture

```
TimeScope/
├── timeScope/          # Backend API + Streamlit Web UI
│   ├── app/            # FastAPI app, models, schemas, API routes
│   ├── streamlit_app.py
│   ├── run_ui.py       # Start API + Streamlit together
│   └── setup.py        # One-command DB + admin setup
│
└── tkinter_app/        # macOS desktop client
    ├── main.py         # Entry point
    └── src/            # API client, auth, system monitor, UI
```

## Quick Start

### 1. Backend & Web UI (timeScope)

From the repo root:

```bash
cd timeScope
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env        # Edit .env if needed
python setup.py            # DB + migrations + first admin user
python run_ui.py           # API on :8000, Streamlit on :8501
```

- **API**: http://localhost:8000 — Docs: http://localhost:8000/docs  
- **Web UI**: http://localhost:8501  

### 2. macOS Desktop Client (tkinter_app)

Requires the backend running (or use offline mode):

```bash
cd tkinter_app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Or use the helper script: `./run.sh` (after `chmod +x run.sh`).

## Features

| Area | Backend (timeScope) | Desktop Client (tkinter_app) |
|------|---------------------|------------------------------|
| **Employees** | CRUD, auth, roles, status | Login, credential storage |
| **Projects** | CRUD, assign employees | View assigned projects/tasks |
| **Time tracking** | Start/stop, summaries, filters | Start/stop timer, sync with API |
| **Screenshots** | Upload, list, permissions | Capture & upload, macOS permissions |
| **Monitoring** | — | Apps, websites, idle detection |

## Requirements

- **Python**: 3.8+
- **Backend**: PostgreSQL (production) or SQLite (development)
- **Desktop client**: macOS 10.14+; optional backend for full sync

## Configuration

- **Backend**: Copy `timeScope/env.example` to `timeScope/.env` and set `DATABASE_URL`, `SECRET_KEY`, etc. See `timeScope/README.md` for full options.
- **Desktop**: Copy `tkinter_app/config.example.py` to `tkinter_app/config.py`. Set `API_BASE_URL` (e.g. `http://localhost:8000/api/v1`) and screenshot/monitoring options.

## Documentation

- **[timeScope README](timeScope/README.md)** — API endpoints, DB schema, env vars, migrations, deployment.
- **[tkinter_app README](tkinter_app/README.md)** — Desktop app setup, permissions, troubleshooting.

## License

See repository license (e.g. MIT for the API; tkinter_app may have separate terms).
