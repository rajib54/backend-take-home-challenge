
# URL Shortener & Analytics API

This FastAPI-based microservice provides URL shortening, redirection, and analytics functionality. 

---

## Features

### URL Shortening
- `POST /shorten`  
  Accepts a long URL and returns a shortened slug and full short URL.
- Idempotent: posting the same long URL returns the same slug. This is done so we can map one long url to a slug.

### Redirection
- `GET /{slug}`  
  Redirects (HTTP 307) to the original long URL.
- Logs a visit with timestamp.
- Uses Redis for fast slug resolution.

### Analytics
- `GET /stats` – Returns the top N visited links.  
- `GET /stats/{slug}` – Returns visit count and latest visit time for one slug.
- Cached in Redis to reduce DB load.

---

## Tech Stack

| Layer      | Tool                    |
|------------|-------------------------|
| Web        | FastAPI                 |
| ORM        | SQLAlchemy              |
| DB         | PostgreSQL              |
| Caching    | Redis                   |
| Migrations | Alembic                 |
| Testing    | Pytest                  |
| Container  | Docker + Compose        |

---

## Project Structure

```
app/
├── main.py              # FastAPI entrypoint
├── routes/              # API routers
├── services/            # Business logic (slugging, stats)
├── handler/             # DB access layer
├── models/              # SQLAlchemy models
├── schemas/             # Response objects to api
├── utils/cache.py       # Redis wrapper
├── tests/               # Unit + integration tests
```

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/rajib54/backend-take-home-challenge
cd backend-take-home-challenge
```

### 2. Run with Docker

```bash
docker-compose up --build
```
- This will apply migrations from alembic/versions folder. For any model changes we can generate migrations and it will be added in that folder
- FastAPI: [http://localhost:8000](http://localhost:8000)

---

## Run Tests

```bash
docker-compose run web pytest
```

- Includes both unit and integration tests.

---

## Design Decisions

- **Slug Generation**: Base62 encoded unique integer; deterministic for duplicate URLs. I used a table `slug_sequence` which has one row (sequence number). 
When slug needs to be generated I take that number and generate slug. This number ensures slug are not totally random and doesn't get duplicated.
For concurency purpose I lock that table after release the lock after slug-long_url mapping is added into DB. For distributed system we can improve this by assigning a range of sequnce for each machine.
- **Visit Logging**: One DB insert per redirect.
- **Caching**:
  - `slug:{slug}` – Cached for 1 day
  - `report:top_n` – Cached for 1 hour and auto-invalidated
- **Layered Architecture**: Handlers (DB), Services (business), Routes (API) separation
- **Async SQLAlchemy**: To be able to handle more requests

---

## Requirements Checklist

| Requirement                    | Status |
|-------------------------------|--------|
| FastAPI service                | ✅     |
| URL shortening (`/shorten`)   | ✅     |
| Redirection (`/{slug}`)       | ✅     |
| Visit tracking                 | ✅     |
| Stats (`/stats`, `/stats/{}`) | ✅     |
| Relational DB (Postgres)      | ✅     |
| Redis caching                 | ✅     |
| Dockerized setup              | ✅     |
| Unit & integration tests      | ✅     |
| Structured codebase           | ✅     |
| README with full instructions | ✅     |

---

## Notes

- The project uses `.env` and `.env.test` to manage configs.
- Make sure ports `5432`, `6379`, `8000`, and `8089` are free on your host machine.

---
