# AzuraCast-py

A Python + React TypeScript rewrite of [AzuraCast](https://www.azuracast.com/), a free and open-source web radio management suite.

## Architecture

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.12, FastAPI, SQLAlchemy 2.0 async |
| Database | PostgreSQL 16 (asyncpg) |
| Cache | Redis 7 |
| Auth | JWT (access + refresh tokens), bcrypt |
| Frontend | React 18, TypeScript, Vite, Zustand, React Query |
| Containerization | Docker + Docker Compose |

## Project Structure

```
azuracast-py/
├── backend/          # FastAPI application
│   ├── src/
│   │   ├── core/     # Config, DB, Security, Logging
│   │   ├── modules/  # Feature modules (users, auth, stations)
│   │   └── api/      # API routes (v1)
│   ├── alembic/      # Database migrations
│   ├── tests/        # Pytest test suite
│   └── scripts/      # Seed scripts
└── frontend/         # React TypeScript SPA
    └── src/
        ├── api/      # Axios client
        ├── store/    # Zustand state management
        ├── pages/    # Route pages
        └── components/
```

## Quick Start (Docker Compose)

```bash
docker compose up -d
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Local Development

### Backend

```bash
cd backend
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python scripts/seed.py
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Default Credentials

After seeding: `admin@azuracast.local` / `admin123`

## Roadmap

### Phase 0 — Foundation ✅
- FastAPI skeleton, Docker Compose, CI/CD
- User auth (JWT), RBAC (roles + permissions)
- Station model + CRUD API

### Phase 1 — Core Radio Features
- Mount points and stream URLs
- Liquidsoap integration for live broadcasting
- AutoDJ playlist management

### Phase 2 — Media Management
- Media file upload and storage
- Metadata extraction (ID3 tags)
- Playlist scheduling

### Phase 3 — Advanced Features
- Live streaming (Icecast/SHOUTcast)
- Listener analytics and statistics
- Webhook notifications

### Phase 4 — Enterprise Features
- Multi-tenant support
- Advanced RBAC with fine-grained permissions
- Plugin system
