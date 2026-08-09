# Reflex Admin POC

Minimal Proof-of-Concept admin framework: a semantic admin domain layer (Resources, Fields, Table, Filters, Forms) + SQLAlchemy adapter + optional Reflex renderer.

Goals:
- Keep the admin semantic model independent of Reflex.
- Demonstrate server-side search, sort, pagination, CRUD.
- Provide demo models (User, Post, Category) and seeding.
- Tests (unit + integration).

Quick start (SQLite fallback):

1. Install dependencies (poetry recommended)
   - poetry install

2. Seed demo DB (SQLite by default)
   - python -m demo.seed --sqlite

3. Run tests
   - pytest -q

Reflex UI (optional)
- Install reflex in extras: `poetry install -E ui`
- Start the Reflex app per reflex docs (demo/app.py includes an example).

For full Postgres local dev:
- `docker-compose up -d`
- seed: `python -m demo.seed --postgres "postgresql://reflex_admin:reflex_admin@localhost:5432/reflex_admin"`
