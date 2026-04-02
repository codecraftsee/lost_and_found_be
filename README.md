# Lost & Found Platform - Backend API

A RESTful API for reporting and recovering lost personal belongings. Finders report items they discovered, owners report items they lost, and the system automatically matches them using category, location, date, and keyword similarity.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Local Development](#local-development)
  - [Docker](#docker)
- [Configuration](#configuration)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)
- [Linting & Type Checking](#linting--type-checking)
- [API Overview](#api-overview)
- [Project Structure](#project-structure)
- [License](#license)

## Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| Framework      | FastAPI (async)                     |
| Database       | PostgreSQL 16                       |
| ORM            | SQLAlchemy 2.0 (async) + asyncpg   |
| Migrations     | Alembic                            |
| Auth           | JWT (python-jose) + bcrypt (passlib)|
| Validation     | Pydantic v2 + pydantic-settings    |
| Server         | Uvicorn                            |
| Tests          | pytest + pytest-asyncio + httpx    |
| Linting        | Ruff                               |
| Type Checking  | mypy                               |

## Prerequisites

- **Python** >= 3.11
- **PostgreSQL** >= 16 (or use Docker)
- **pip** (or a compatible package manager)

## Getting Started

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd lnf-be
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your values (see [Configuration](#configuration)).

5. **Start PostgreSQL** (skip if using Docker)

   Ensure a PostgreSQL instance is running and the database exists:

   ```bash
   createdb lnf_db
   ```

6. **Run database migrations**

   ```bash
   alembic upgrade head
   ```

7. **Start the development server**

   ```bash
   uvicorn app.main:app --reload --app-dir src
   ```

   The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Docker

Run the entire stack (API + PostgreSQL) with a single command:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

To stop and remove containers:

```bash
docker-compose down
```

To also remove the database volume:

```bash
docker-compose down -v
```

## Configuration

Configuration is managed via environment variables (loaded from `.env`). See `.env.example` for all available options:

| Variable                     | Description                          | Default                                                  |
|------------------------------|--------------------------------------|----------------------------------------------------------|
| `DATABASE_URL`               | PostgreSQL async connection string   | `postgresql+asyncpg://postgres:postgres@localhost:5432/lnf_db` |
| `SECRET_KEY`                 | JWT signing key                      | `change-me-in-production`                                |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Access token TTL in minutes          | `30`                                                     |
| `REFRESH_TOKEN_EXPIRE_DAYS`  | Refresh token TTL in days            | `7`                                                      |
| `CORS_ORIGINS`               | Allowed CORS origins (JSON array)    | `["http://localhost:3000"]`                               |
| `RATE_LIMIT_PER_MINUTE`      | Max requests per minute per client   | `60`                                                     |
| `CLAIM_MAX_ATTEMPTS`         | Max claim attempts per item per user | `3`                                                      |
| `CLAIM_COOLDOWN_MINUTES`     | Cooldown after failed claim attempt  | `30`                                                     |

> **Important:** Always change `SECRET_KEY` in production to a strong, random value.

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description of changes"

# Downgrade one revision
alembic downgrade -1
```

## Running Tests

```bash
pytest
```

Tests use `pytest-asyncio` with auto mode. Test configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`.

## Linting & Type Checking

```bash
# Lint and auto-fix
ruff check --fix src tests

# Format
ruff format src tests

# Type check
mypy src
```

Ruff is configured in `pyproject.toml` targeting Python 3.11 with a 120-character line length.

## API Overview

All domain routes are prefixed with `/api/v1/`. Interactive documentation is auto-generated at `/docs` (Swagger UI) and `/redoc` (ReDoc).

| Module          | Prefix                    | Description                             |
|-----------------|---------------------------|-----------------------------------------|
| Health          | `/health`                 | Health check endpoint                   |
| Auth            | `/api/v1/auth`            | Registration, login, JWT, passwords     |
| Items           | `/api/v1/items`           | CRUD for lost and found item reports    |
| Search          | `/api/v1/search`          | Browse and filter with pagination       |
| Matching        | `/api/v1/matching`        | Automatic matching engine, suggestions  |
| Claims          | `/api/v1/claims`          | Claim submission, verification          |
| Notifications   | `/api/v1/notifications`   | In-app notification management          |

## Project Structure

```
lnf-be/
├── src/
│   └── app/
│       ├── main.py              # Application entrypoint & router registration
│       ├── config.py            # Settings (env-based via pydantic-settings)
│       ├── constants.py         # Application constants
│       ├── database.py          # Async SQLAlchemy engine & session
│       ├── dependencies.py      # FastAPI dependency injection
│       ├── exceptions.py        # Custom exception classes & handlers
│       ├── middleware/          # CORS and other middleware
│       ├── auth/               # Authentication & authorization
│       ├── items/              # Lost & found item reports
│       ├── search/             # Browse & search with filters
│       ├── matching/           # Automatic matching engine
│       ├── claims/             # Claim verification & fraud prevention
│       └── notifications/      # In-app notifications
├── migrations/                  # Alembic migration scripts
├── tests/                       # Test suite (mirrors src/app structure)
├── .env.example                 # Environment variable template
├── alembic.ini                  # Alembic configuration
├── docker-compose.yml           # Docker Compose (API + PostgreSQL)
├── Dockerfile                   # Multi-stage Docker build
└── pyproject.toml               # Project metadata, dependencies, tool config
```

Each domain module follows the pattern: `router.py` → `service.py` → `repository.py` + `models.py` + `schemas.py`.

## License

This project is proprietary. All rights reserved.
