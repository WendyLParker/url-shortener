# URL Shortener

A high-performance URL shortening service built with **Python + FastAPI**.

### Features
- Generate a short URL for any long URL
- Instant redirect from short URL → original URL
- Click analytics (click count tracking)
- Designed for high traffic and low latency (Redis caching)
- Fully containerized with Docker

### Tech Stack
- **FastAPI** – Modern, high-performance async Python framework
- **PostgreSQL** – Primary database
- **Redis** – Caching layer for ultra-fast redirects
- **Docker + Docker Compose** – Reproducible environment
- **SQLAlchemy + Alembic** – ORM and migrations

### Why this stack?
When evaluating options for a high-traffic, low-latency URL shortener, three strong candidates stood out:

1. **Go + Gin/Fiber** — Excellent for high-concurrency, read-heavy services.
2. **Node.js + Fastify** — The most popular real-world choice; ships very quickly.
3. **Python + FastAPI** — Fully capable (especially with Redis) and offers outstanding developer experience.

I chose **Python + FastAPI** because I am actively interviewing and focused on landing a stable role. It currently offers the broadest job market opportunities, strengthens my portfolio with a modern in-demand skill set, and complements recent AI-related learning.

### API Endpoints
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/shorten`                | Create a short URL                 |
| GET    | `/{short_url}`            | Redirect to the original URL       |
| GET    | `/analytics/{short_url}`  | Get click analytics                |

### Project Structure

```
url-shortener/
├── app/
│   ├── main.py              # FastAPI app instance, lifespan, root route
│   ├── core/
│   │   └── config.py        # pydantic-settings configuration
│   ├── db/
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   ├── session.py       # Async engine / session factory
│   │   └── redis.py         # Redis client
│   ├── models/               # SQLAlchemy ORM models (empty for now)
│   ├── schemas/               # Pydantic schemas
│   └── api/
│       ├── deps.py          # Shared FastAPI dependencies
│       └── v1/
│           ├── router.py    # Aggregates all v1 routers
│           └── endpoints/
│               └── health.py
├── alembic/                  # Async-aware Alembic migration environment
├── tests/
├── docker/entrypoint.sh      # Runs migrations, then starts uvicorn
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

### Getting Started

```bash
# Clone the repository
git clone https://github.com/WendyLParker/url-shortener.git
cd url-shortener

# Create your local environment file
cp .env.example .env

# Start the full stack (API + Postgres + Redis)
docker compose up --build
```

API docs will be available at: http://localhost:8000/docs
Health check: http://localhost:8000/api/v1/health

### Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Point POSTGRES_HOST / REDIS_HOST at localhost in your .env, then:
alembic upgrade head
uvicorn app.main:app --reload
```

### Database Migrations

```bash
# Autogenerate a migration after adding/changing models in app/models/
alembic revision --autogenerate -m "add short_urls table"

# Apply migrations
alembic upgrade head
```

