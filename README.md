# Hyperdrive Crowdfunding — Prototype Full‑Stack

This is a **prototype** full‑stack scaffold for your Algorand crowdfunding dApp, centered on your provided PyTeal smart contract (included **unchanged**). It favors a **robust backend** with a simple frontend.

## What’s inside
- **contracts/** — your PyTeal contract as `crowdfunding.py` (unchanged) + a small `compile.py` helper.
- **backend/** — FastAPI + SQLAlchemy (Postgres via Docker) with a clean architecture:
  - Projects, Users, Contributions, Transactions tables
  - Cached on-chain state (goal, rate, deadline, etc.) for fast queries
  - Sync endpoints & service stubs to integrate with an Algorand indexer
- **frontend/** — Minimal Vite + React TypeScript UI to list projects and view details.

## Quick start (Docker)
Prereqs: Docker + Docker Compose

```bash
# 1) Copy env template and adjust as needed
cp backend/.env.example backend/.env

# 2) Launch stack
docker compose up --build
# API: http://localhost:8000/docs
# Frontend: http://localhost:5173
# Adminer (DB UI): http://localhost:8080  (System: PostgreSQL, Server: db, User/Pass in .env)
```

> Note: The backend includes **stubs** for Algorand Indexer/algod interaction. Wire those up to your preferred provider (AlgoNode, Dappflow, self-hosted indexer, etc.) and schedule the sync job (`services/sync.py`) via a worker/cron if desired.

## Local (no Docker)
You can also run the backend locally against SQLite for quick tests by setting `DB_URL=sqlite+aiosqlite:///./dev.db` in `backend/.env` and starting FastAPI with uvicorn. The included Docker setup uses Postgres by default.

## Contract compilation
From `contracts/`:
```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python compile.py
# Outputs: build/approval.teal and build/clear.teal
```

## API highlights
- `GET /projects` — list projects (+computed % funded)
- `POST /projects` — create project metadata (links on-chain `app_id`/`asa_id`)
- `GET /projects/{id}` — project detail (joins cached chain state + metadata)
- `POST /sync/app/{app_id}` — on-demand sync from indexer for one app
- `POST /webhooks/indexer` — webhook target if your indexer supports push

See full interactive docs at **/docs** when the API is running.

## Notes
- This is a scaffold: **no private keys** or signing occurs server-side.
- Frontend does **not** yet send transactions; it displays data from backend.
- You can bring in wallet-connect and full flows later (Pera/Defly/etc.).
