# linkding

A self-hosted bookmark manager built with Django: SQLite by default, a REST API, server-rendered templates with a JavaScript frontend, background tasks with Huey, and import and export of bookmarks. Work arrives as factory tasks; `.factory/contract.json` defines the checks that decide pass or fail.

## Stack
Language: Python 3.13 · Framework: Django · Packaging: `pyproject.toml` with `uv` · Tests: pytest with pytest-django and xdist · Lint and format: ruff · Frontend: Node 20, npm

## Commands
- Install: `uv sync && npm ci && mkdir -p data`
- Lint: `uv run ruff check bookmarks`
- Format check: `uv run ruff format --check bookmarks` (fix with `uv run ruff format bookmarks`)
- Tests: `uv run pytest -n auto`

## Layout
- The Django app lives in `bookmarks/`: models in `models.py`, query building in `queries.py`, business logic in `services/`, REST API in `api/`, views in `views/`, templates in `templates/`, frontend code in `frontend/` and styles in `styles/`.
- Unit and integration tests live in `bookmarks/tests/` and follow the existing test helpers (`BookmarkFactoryMixin` and similar).
- Database changes need a migration in `bookmarks/migrations/`.
- Specs live in `specs/`.

## Rules
- Changes stay inside `bookmarks/**`, `docs/**`, `specs/**`, `pyproject.toml`, `uv.lock`, `package.json` and `package-lock.json`.
- Do not edit `pytest.ini`, any `conftest.py`, `bookmarks/tests_e2e/**`, `.factory/**`, `.github/**` or `AGENTS.md`.
- Follow the conventions of the existing code: API endpoints, serializers, permissions and responses behave like the neighboring ones.
- New dependencies need a clear reason in the spec; prefer what Django and the existing dependencies already provide.
- No secrets and no network access at runtime or in tests.
