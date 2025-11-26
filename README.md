# 🧩 **minilink — Minimal URL Shortener (FastAPI + SQLite + DevOps)**

A clean, modern, and production-ready URL shortener built with **FastAPI**, **SQLModel**, **Tailwind CSS**, full **CI/CD**, **Docker**, **Azure Web App**, and **Prometheus monitoring**.

This version includes:
	•	Automated tests (81% coverage)
	•	CI pipeline (tests, coverage gate, Docker build, GHCR publish)
	•	Azure Web App for Containers deployment
	•	Health checks & Prometheus metrics
	•	Clean, SOLID-friendly backend structure

---

## 🚀 Features

### 🔗 Core Application
	•	Shorten URLs from a simple web interface
	•	Per-user link ownership and full authentication
	•	Click analytics (click_count, last_accessed)
	•	Smart sorting on analytics page (most-clicked first)
	•	Full REST API
	•	Minimal responsive UI using Tailwind

### 🛠️ DevOps Enhancements
	•	Automated tests using pytest
	•	Coverage gate (pipeline fails below 70%)
	•	GitHub Actions CI/CD
	•	Run tests & coverage
	•	Build Docker image
	•	Push image to GHCR
	•	Deploy to Azure Web App when CI passes
	•	Production-ready Dockerfile
	•	Health check endpoint: /health
	•	Prometheus metrics at /metrics
	•	Optional local Prometheus configuration

---

## 💻 Quickstart (Local)

### 1. Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

### 2. Install dependencies
pip install -r requirements.txt

### 3. Run the app
uvicorn app.main:app --reload

👉 Open http://localhost:8000 in your browser.

# run tests + coverage
python -m pytest --cov=app --cov-report=term-missing --cov-report=html

View full HTML coverage at:
htmlcov/index.html

## 🐳 Docker (Local)

Build the Docker image:
docker build -t minilink:latest .

Run the container:
docker run -p 8000:8000 minilink:latest

## 🚦 GitHub Actions CI/CD

CI/CD is fully automated on main:

✔ Runs on every push to main:
	•	Installs dependencies
	•	Runs tests + coverage
	•	Enforces ≥70% coverage
	•	Builds Docker image
	•	Publishes image to GitHub Container Registry (GHCR)
	•   Trigger Azure Web App deployment

✔ CD (deployment)

Render auto-deploys only when main CI passes.

Docker image is published as:
ghcr.io/javronich1/minilink:latest

## ☁️ Cloud Deployment (Azure Web App for Containers)

The live application runs at:

👉 https://minilink-javronich1-container-h7chfcf6dvdrfgbg.westeurope-01.azurewebsites.net/

Deployment details:
	•	Platform: Azure Web App for Containers
	•	Source: Docker image from GHCR
	•	Runtime: Python + FastAPI inside a custom Docker container
	•	Auto-deploy: Enabled via GitHub Actions (only on main branch)
	•	Azure Resource Group: BCSAI2025-DEVOPS-STUDENTS-B
	•	Service Plan: Provided in course (Linux plan)
	•	Environment variables:
	•	COOKIE_SECRET
	•	SESSION_SECRET
	•	ENV=production

This satisfies the DevOps requirement to deploy using Docker + Azure + CI/CD automation.

## 📈 Monitoring & Health

### Health Check

GET /health
→ {"status": "ok"}

### Prometheus Metrics

GET /metrics

Exports:
	•	minilink_requests_total
	•	minilink_request_latency_seconds
	•	Python GC metrics
	•	Error counters

Optional Prometheus Local Config

monitoring/prometheus.yml:

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "minilink"
    static_configs:
      - targets: ["host.docker.internal:8000"]

## 🧭 API Overview

Endpoints:

POST /api/links
→ Create a new short link

GET /api/links
→ List all links (only for the logged-in user)

GET /api/links/{code}
→ Retrieve details for a specific short link

PATCH /api/links/{code}
→ Update an existing link

DELETE /api/links/{code}
→ Delete a link

GET /r/{code}
→ Redirect to the original URL (increments click count)

GET /api/links/{code}/stats
→ Retrieve analytics for a single link

GET /health
→ Health check endpoint

GET /metrics — Prometheus metrics

## 🌐 Web Interface

/ — Home Page
Create a short link. Only accessible after login.

/links — Analytics Page
See all your URLs, click counts, and last access times.
Click the “🔄 Refresh” button after testing redirects to update stats.

/login — Login / Signup Page
Sign up for a new account or log in to an existing one.

## 👤 Authentication System
	•	Users must sign up or log in before creating or viewing links.
	•	Each user’s links are private and stored separately.
	•	When logged in, your username appears on the top bar.
	•	To view all your URLs and stats, click “See my analytics” on the homepage.

## 🔑 Default Account

When the app is first run, a default account is automatically available:
Username: admin
Password: 123

## 🧾 Example Workflow
	1.	Open /login
	2.	Log in or create an account
	3.	Shorten a URL on /
	4.	View analytics at /links
	5.	Try /r/<code> redirections
	6.	Refresh analytics to update stats

## 🧩 Tech Stack
	•	FastAPI — web framework
	•	SQLModel — ORM + SQLite database
	•	Jinja2 — templating engine
	•	Tailwind CSS — modern responsive styling
	•	Passlib (PBKDF2-SHA256) — secure password hashing
	•	SessionMiddleware — cookie-based authentication
	•	Docker
	•	GitHub Actions
	•	Prometheus
	•	Azure Web App for Containers

⚠️ Disclaimer — Use of AI Assistance

This project was developed with the assistance of AI tools (ChatGPT by OpenAI) to streamline the development process.

AI was primarily used for:
	•	Generating boilerplate code and repetitive functions
	•	Designing HTML/CSS templates and improving UI styling
	•	Providing guidance on best practices and debugging support
    •	Repetitive tasks such as this README file
    •	Guidance for some better practices
    •	Smoke testing

All critical logic, reasoning, data modeling, and architectural decisions — including database design, authentication flow, and feature implementation — were conceptualized, coded, and refined by a human developer.

All architectural decisions, core logic, refactoring, DevOps setup (CI/CD, Docker, monitoring), and deployment work were performed intentionally and manually by the developer.

The AI served as a productivity enhancer, not a replacement for human creativity or understanding.

💡 This project demonstrates the powerful synergy between human intelligence and AI assistance in modern software development.

Created by Gonzalo Fernandez de Cordoba
Built as a learning and portfolio project — minimal yet powerful.