# URL Shortener

A high-performance URL shortening service built with **Python + FastAPI**. Submit a long URL, get back a short code, and every visit to that short link is tracked and redirected to the original destination — with Redis caching so redirects stay fast under load.

### Features
- Generate a short code for any long URL (`POST /shorten`)
- Instant redirect from short code → original URL, with click tracking (`GET /{short_code}`)
- Click analytics: view count, original URL, and creation time (`GET /analytics/{short_code}`)
- Redis cache-aside pattern in front of Postgres for low-latency redirects
- Dependency health check (`GET /health`) for API, Postgres, and Redis
- Fully containerized with Docker Compose (API + Postgres + Redis)
- Async SQLAlchemy models with Alembic migrations

### Tech Stack
| Component | Choice | Why |
|---|---|---|
| Web framework | **FastAPI** | Async-native, automatic OpenAPI/Swagger docs, strong typing via Pydantic |
| Database | **PostgreSQL** | Reliable, relational store for short URLs and click counts |
| Cache | **Redis** | Sub-millisecond lookups for the hottest path — resolving a short code on redirect |
| ORM / migrations | **SQLAlchemy (async) + Alembic** | Type-safe queries and versioned, repeatable schema changes |
| Containerization | **Docker + Docker Compose** | One-command, reproducible local environment matching production topology |
| Config | **pydantic-settings** | Typed, validated environment configuration instead of loose `os.environ` calls |

**Why this stack?** When evaluating options for a high-traffic, low-latency URL shortener, three strong candidates stood out: Go (Gin/Fiber) for raw concurrency, Node.js (Fastify) for shipping speed, and Python (FastAPI) for developer experience. I chose **Python + FastAPI** because it's fully capable for this workload (especially paired with Redis), it's in high demand in the current job market, and it let me showcase modern async Python patterns end-to-end — from typed settings to async ORM sessions to cache-aside caching.

### Project Structure

```
url-shortener/
├── app/
│   ├── main.py                # FastAPI app instance, lifespan, root route
│   ├── core/
│   │   └── config.py          # pydantic-settings configuration
│   ├── db/
│   │   ├── base.py            # SQLAlchemy declarative base
│   │   ├── session.py         # Async engine / session factory
│   │   └── redis.py           # Redis client
│   ├── models/
│   │   └── url.py             # ShortURL ORM model
│   ├── schemas/
│   │   ├── health.py
│   │   └── url.py             # Shorten / analytics Pydantic schemas
│   ├── services/
│   │   └── url_shortener.py   # Short-code generation, cache-aside lookup, click tracking
│   └── api/
│       ├── deps.py            # Shared FastAPI dependencies
│       └── v1/
│           ├── router.py      # Aggregates all v1 routers
│           └── endpoints/
│               ├── health.py
│               ├── shorten.py
│               ├── analytics.py
│               └── redirect.py
├── alembic/                    # Async-aware Alembic migration environment
├── tests/
├── docker/entrypoint.sh        # Runs migrations, then starts uvicorn
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

### Getting Started (Docker)

```bash
# Clone the repository
git clone https://github.com/WendyLParker/url-shortener.git
cd url-shortener

# Create your local environment file
cp .env.example .env

# Start the full stack (API + Postgres + Redis)
docker compose up --build
```

- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

The API container runs `alembic upgrade head` on startup, so the database schema is always up to date before `uvicorn` starts.

### API Endpoints

| Method | Endpoint                          | Description                             |
|--------|------------------------------------|------------------------------------------|
| GET    | `/api/v1/health`                  | Health check for the API, Postgres, and Redis |
| POST   | `/api/v1/shorten`                 | Create a short URL for a long URL       |
| GET    | `/api/v1/{short_code}`            | Redirect to the original URL, tracking a click |
| GET    | `/api/v1/analytics/{short_code}`  | Get click analytics for a short code    |

```bash
# Create a short URL
curl -X POST http://localhost:8000/api/v1/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com/some/very/long/path"}'
# => {"short_code": "aZ3xQ1b", "short_url": "http://localhost:8000/api/v1/aZ3xQ1b", ...}

# Check analytics
curl http://localhost:8000/api/v1/analytics/aZ3xQ1b
```

#### Testing the redirect endpoint

`GET /api/v1/{short_code}` returns an HTTP 307 redirect. **Swagger UI's "Try it out" button will not show the redirect** — the browser's underlying `fetch` call follows redirects silently and Swagger just displays the final response, so it can look like the endpoint "did nothing" or returned the wrong thing. To actually observe the redirect, use one of these instead:

```bash
# See the 307 and its Location header
curl -i http://localhost:8000/api/v1/aZ3xQ1b

# Follow it all the way to the original URL
curl -iL http://localhost:8000/api/v1/aZ3xQ1b
```

Or simply paste `http://localhost:8000/api/v1/aZ3xQ1b` into a browser's address bar — the browser will follow the redirect and land on the original URL.

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
alembic revision --autogenerate -m "describe your change"

# Apply migrations
alembic upgrade head
```

### Running Tests

```bash
pytest
```

### License

MIT — see [LICENSE](LICENSE).
