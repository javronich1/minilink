# MiniLink – DevOps, Testing, and Deployment Report

## 1. Introduction
This report summarizes the improvements made to the MiniLink URL shortener in Assignment 2.  

Earlier versions were deployed on Render during development, but the final deployment uses Azure Web App for Containers as required by the assignment.

The focus of this iteration was upgrading the project from a simple local application to a fully tested, containerized, monitored, and automatically deployed production-style service. 

This includes:
- Significant refactoring for code quality
- Automated testing with ≥70% coverage (achieved 81%)
- A complete CI/CD pipeline using GitHub Actions
- Docker containerization and registry publishing
- Cloud deployment using Azure Web App for Containers
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

Command used: python -m pytest --cov=app --cov-report=xml --cov-report=html

---

## 4. CI/CD Pipeline (GitHub Actions + Docker + GHCR + Azure)
A full CI/CD workflow was built in `.github/workflows/ci.yml`.

A full CI/CD workflow was built in .github/workflows/ci.yml.

4.1 CI Steps

The CI pipeline runs automatically on every push to main:
	1.	Checkout repository
	2.	Set up Python
	3.	Install dependencies
	4.	Run tests
	5.	Enforce ≥70% coverage threshold
	6.	Build Docker image
	7.	Run a smoke test: launch the container and call /health

If any step fails, the pipeline stops.

4.2 Docker & GHCR

After tests pass, the pipeline builds and publishes the container image to:

ghcr.io/javronich1/minilink:latest

This is done using:
	•	docker/login-action
	•	docker/build-push-action

Authentication is handled securely through GITHUB_TOKEN.

4.3 Deployment to Azure

The pipeline includes an azure-setup job that:
	1.	Logs into Azure using the Service Principal credentials provided for the assignment
	2.	Ensures the resource group exists (BCSAI2025-DEVOPS-STUDENTS-B)
	3.	Updates the Azure Web App for Containers to pull the newest image from GHCR

The Azure Web App is configured with:
	•	Web App name: minilink-javronich1
	•	Runtime: Docker container
	•	Registry source: GHCR
	•	Environment variables (SESSION_SECRET, COOKIE_SECRET, ENV=production)

This satisfies the assignment’s requirements:
	•	Containerized application
	•	Automated deployment pipeline
	•	Only deployed from main
	•	Uses Azure resources via Service Principal

4.4 Summary of Deployment Flow
	1.	Push to main
	2.	GitHub Actions:
	•	run tests
	•	check coverage
	•	build + smoke test Docker
	•	push image to GHCR
	3.	Azure Web App pulls the updated image and restarts automatically

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
- Azure Web App for Containers was used for deployment. While simple to configure with Docker and suitable for this assignment, a more scalable production setup might require additional Azure services (App Service Plan upgrades, managed databases, IaC, etc.).
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
