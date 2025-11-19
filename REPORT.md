# MiniLink – DevOps, Testing, and Deployment Report

## 1. Introduction
This report summarizes the improvements made to the MiniLink URL shortener in Assignment 2.  
The focus of this iteration was upgrading the project from a simple local application to a fully tested, containerized, monitored, and automatically deployed production-style service.

This includes:
- Significant refactoring for code quality
- Automated testing with ≥70% coverage (achieved 81%)
- A complete CI/CD pipeline using GitHub Actions
- Docker containerization and registry publishing
- Cloud deployment using Render
- Health checks and Prometheus metrics
- Updated documentation

---

## 2. Code Quality & Refactoring
The codebase was reorganized to remove duplication, improve clarity, and follow the Single Responsibility Principle.

### Key Improvements
- Extracted password hashing and authentication helpers into **`app/auth.py`**.
- Moved short-code generation and URL validation into **`app/services.py`**.
- Centralized DB initialization and session logic in **`app/db.py`**.
- Clearly separated:
  - Models → `models.py`
  - Schemas → `schemas.py`
  - Routes → `main.py`
- `main.py` is now focused on routing and orchestration instead of business logic.
- Added helper `get_current_user()` to avoid repeated authentication code.

### Result
A cleaner, modular structure that is:
- easier to test,
- easier to maintain,
- and aligned with SOLID principles.

---

## 3. Testing & Coverage
Testing was performed using **pytest** and FastAPI’s **TestClient**, covering:

- `/health`
- CRUD operations for links
- Redirect behavior and analytics increment
- Expired link logic (410 Gone)
- Invalid or conflicting link creation
- Authentication-protected endpoints

### Coverage
- Achieved **81% line coverage**.
- Pipeline enforces a **minimum of 70%**.
- CI parses `coverage.xml` and fails the build if coverage is insufficient.

Command used: python -m pytest –cov=app –cov-report=xml –cov-report=html

---

## 4. CI/CD Pipeline (GitHub Actions + Docker + GHCR + Render)
A full CI/CD workflow was built in `.github/workflows/ci.yml`.

### CI Steps
1. Checkout repo  
2. Set up Python  
3. Install dependencies  
4. Run tests  
5. Enforce ≥70% coverage  
6. Build Docker image  
7. Smoke test container (`/health`)  

### Docker & GHCR
- CI builds the image and pushes it to:  
  **ghcr.io/javronich1/minilink:latest**
- Uses `docker/build-push-action`.
- Authentication handled via `GITHUB_TOKEN`.

### Deployment (CD)
- Render is configured to:
  - Pull from GitHub
  - Use Dockerfile directly
  - Auto-deploy **only when `main` changes**
  - Use environment variables (`SESSION_SECRET`, `ENV=production`)

This satisfies all CD requirements:
- Containerized app  
- Automated deployment pipeline  
- Main-branch-only triggers  

---

## 5. Monitoring & Health Checks
### Health Check
- `/health` returns a simple JSON:  
  `{ "status": "ok" }`
- Used by:
  - Local debugging
  - CI docker smoke tests
  - Potential uptime monitoring

### Prometheus Metrics
At `/metrics`, the app exposes:
- `minilink_requests_total`
- `minilink_request_latency_seconds`
- `minilink_request_errors_total`
- Default Python metrics (GC, info, etc.)

Middleware automatically tracks:
- Per-path request volume
- Latency histograms
- Server errors

### Optional Prometheus Config
A minimal Prometheus config is included in `monitoring/prometheus.yml`.

---

## 6. Reflection & Future Work
### Improvements over Assignment 1
- From a local script → to a **production-style service**
- From manual testing → to **automated tests + coverage**
- From ad-hoc execution → to **Docker + CI/CD**
- From no visibility → to **monitoring & metrics**

### Trade-offs
- Stayed on SQLite for simplicity (good for assignment; not ideal for scale).
- Render was chosen for minimal config; production apps might require AWS/GCP/Azure.
- Focus was DevOps-oriented rather than adding many new features.

### Future Enhancements
- Staging environment before production
- Alerting based on error rate
- Infrastructure as Code (Terraform)
- PostgreSQL for high-load use

---

## 7. AI Usage Disclosure
AI tools (ChatGPT) were used for:
- Structuring CI/CD pipelines
- Debugging YAML syntax
- Suggesting testing patterns
- Formatting this report and README

All code, pipeline logic, and architectural decisions were fully understood and validated manually.

---
