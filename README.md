# RigoLoterias

Canonical modular platform for lottery and pool analysis.

## Current game status

| Game | Status |
|---|---|
| TRIS | Available |
| Melate | Available |
| Melate Retro | Available |
| Chispazo | Available |
| Gana Gato | Available |
| Progol | Available |
| Progol Media Semana | Available |
| Protouch | Available |

PLATFORM CORE SCOPE COMPLETE — 8 GAMES

## Architecture

- `backend/app`: FastAPI API, domain contracts, game registry and SQLAlchemy models.
- `backend/migrations`: Alembic migrations for the new canonical database only.
- `frontend/src`: React/TypeScript SPA with shared layout and game routes.
- `docs`: architecture, engine, rules and migration decisions.

Source projects are read-only references and are not dependencies of this repository.

## Backend

Requires Python 3.12.

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

The API is served at `http://127.0.0.1:8000/api/v1`; OpenAPI is available at `/docs`.
Set `DATABASE_URL` to use PostgreSQL in production. The default is a new local SQLite file
inside `backend/`; existing project databases are never referenced.

## Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Set `VITE_API_BASE_URL` to change the centralized API origin.

## Tests and quality

```bash
cd backend
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/black --check .
.venv/bin/mypy app tests

cd ../frontend
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Migrations

Run migrations from `backend/`. The Phase A baseline creates only the canonical schema:

```bash
alembic upgrade head
alembic downgrade base
```

Never aim `DATABASE_URL` at a source project's database.
