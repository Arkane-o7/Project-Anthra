# ANTHRA MVP

![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-4169E1?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00)

ANTHRA is an early-stage “flight simulator” for marketing and product ideas: campaigns are evaluated against artificial personas before teams spend real-world budget. This repository contains the first backend foundation plus the architecture and delivery plan for the larger simulation platform.

## Current implementation

```mermaid
flowchart LR
    UI["React and Vite frontend"] --> API["FastAPI application"]
    API --> AUTH["Registration and JWT login"]
    AUTH --> ORM["SQLAlchemy models"]
    ORM --> PG[("PostgreSQL")]
    API --> MODELS["Campaign, persona, run, and result models"]
    MODELS --> PG
```

Implemented today:

- FastAPI application and authentication routes;
- bcrypt password hashing and JWT access tokens;
- SQLAlchemy models for users, campaigns, personas, simulation runs, and results;
- Alembic migration scaffolding;
- React/Vite frontend workspace;
- technical, development, and delivery planning documents.

The frontend is still the default Vite starter, and the persona-generation, simulation, analytics, queue, vector-database, and cloud layers described in `TECHNICAL_REPORT.md` are planned architecture rather than finished services.

## Backend setup

Requirements: Python 3.10+ and PostgreSQL.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@localhost/anthra_mvp
JWT_SECRET=replace-with-a-long-random-secret
```

Apply available migrations and start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

FastAPI exposes interactive API documentation at `http://localhost:8000/docs`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## API surface

| Endpoint | Purpose |
| --- | --- |
| `GET /` | Basic service response |
| `POST /auth/register` | Create a user account |
| `POST /auth/token` | Exchange credentials for a bearer token |

## Roadmap described in the repository

The design documents propose specialized persona, simulation, and analytics services; Qdrant-backed semantic persona search; asynchronous workers; fairness analysis; and AWS deployment. Treat these documents as design intent and validate them against the implementation as the MVP evolves.

## Security note

Always override the development `JWT_SECRET`, keep database credentials outside Git, and add authorization checks before exposing campaign or simulation data. The current code is a foundation, not a production-hardened authentication service.
