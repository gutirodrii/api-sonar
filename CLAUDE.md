# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server (hot reload)
uvicorn main:app --reload

# Run with production settings (matches Docker)
uvicorn main:app --host 0.0.0.0 --port 3000

# Run database migrations manually
python migrate.py

# Seed database with dummy pulseras and users
python seed.py
```

## Environment

Create a `.env` file with:
```
DATABASE_URL=postgresql://user:password@host/dbname
```

Without it, falls back to `sqlite:///./database.db` (see `database.py`).

In production, the app connects to a Neon PostgreSQL instance via `DATABASE_URL` injected as a Docker env var.

## Architecture

All application code lives in the root directory (no package structure):

- **`main.py`** — FastAPI app, all route handlers, and Pydantic request models. Tables are auto-created on startup via `SQLModel.metadata.create_all(engine)`.
- **`models.py`** — SQLModel table definitions: `User`, `Throw`, `FirstThrow`, `Screen`, `Pulsera`.
- **`database.py`** — Engine creation and `get_session()` dependency. Handles both SQLite (dev) and PostgreSQL (prod).
- **`migrate.py`** — One-off raw SQL migrations (run manually, not auto-applied on startup).
- **`seed.py`** — Creates 10 dummy pulseras and users for testing.

## Data Model

- **`Pulsera`** — Wristband/badge registry. Must exist before a user can be created.
- **`User`** — Auto-incremented integer PK. Created by providing a valid `pulsera_id`. `pulsera_id` is unique (one user per pulsera). `group_id` is auto-assigned alternating 1/2 based on the last created user. `state` is 0, 1, or 2 (enforced in app logic).
- **`Screen`** — 1:1 with `User` (same `user_id` PK, integer). Created automatically alongside the user.
- **`Throw`** — Dice roll records, FK to `User.id` (integer).
- **`FirstThrow`** — Shares the same PK as the corresponding `Throw`. Linked back from `User.first_throw_id` when `claim-first` is called.

## User Creation Flow

`POST /users/` accepts `{ pulsera_id, thrower? }`:
1. Validates `pulsera_id` exists in the `pulsera` table.
2. Rejects if `pulsera_id` is already linked to a user.
3. Assigns `group_id` alternating 1→2→1→2 based on the last user's `group_id`.
4. Creates `User` (auto-incremented `id`) and its associated `Screen`.

## Deployment

CI/CD via `.github/workflows/deploy.yml`: pushes to `main`/`master`/`production` build and push a Docker image to GitHub Container Registry (`ghcr.io`), then SSH into the server to pull and restart the container on port 80 (mapped to internal 3000). Container name is `tuapi`.

Required GitHub secrets: `DATABASE_URL`, `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY`.

CORS is currently restricted to `http://localhost:5173` (Vite dev server) — update `origins` in `main.py` for production frontend domains.

## Schema Changes

When modifying models, `SQLModel.metadata.create_all(engine)` only creates missing tables — it does not ALTER existing ones. Use `migrate.py` with raw `ALTER TABLE` statements for additive column changes on existing databases.
