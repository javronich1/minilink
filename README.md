# minilink — Minimal URL Shortener (FastAPI + SQLite)

## Features
- CRUD endpoints for links
- Redirect `/r/{code}` with 307 redirect
- Click analytics (click_count, last_accessed)
- Stats endpoint `/api/links/{code}/stats`
- Health check `/health`

## Quickstart (local)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Open http://localhost:8000/docs

API Overview
	•	POST /api/links → create
	•	GET /api/links → list
	•	GET /api/links/{code} → read
	•	PATCH /api/links/{code} → update
	•	DELETE /api/links/{code} → delete
	•	GET /r/{code} → redirect (increments analytics)
	•	GET /api/links/{code}/stats → stats
	•	GET /health → health check

## Minimal UI
- `/` — HTML form to create a short link
- `/links` — Analytics table (sorted by most-clicked, shows last access)