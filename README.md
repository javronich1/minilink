# 🧩 **minilink — Minimal URL Shortener (FastAPI + SQLite)**

A clean, modern, and minimal URL shortener built with **FastAPI**, **SQLModel**, and **Tailwind CSS**.  
Includes user authentication and individual analytics for each account.

---

## 🚀 Features

- 🔗 **Shorten URLs** easily from a simple web interface  
- 👤 **User authentication** (signup, login, logout)
- 🧮 **Per-user analytics** — each user sees **only their own links**
- 📊 Click analytics for every short link:
  - Click count (`click_count`)
  - Last access time (`last_accessed`)
- 🧠 Smart sorting on the analytics page (most-clicked first)
- ⚙️ Full REST API with CRUD operations (create links, read links, update click_counts, delete links)
- ❤️ Minimal, elegant UI built with Tailwind CSS
- 🩺 Health check endpoint for monitoring

---

## 💻 Quickstart (Local)

1. Create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Run the app
uvicorn app.main:app --reload

👉 Open http://localhost:8000 in your browser.

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
	1.	Go to http://localhost:8000/login
	2.	Log in with admin / 123 or create your own account
	3.	On the home page (/), enter a long URL and click Shorten
	4.	Click See my analytics to view all your short links and their stats
	5.	Test redirects and refresh analytics to see updated click counts

## 🧩 Tech Stack
	•	FastAPI — web framework
	•	SQLModel — ORM + SQLite database
	•	Jinja2 — templating engine
	•	Tailwind CSS — modern responsive styling
	•	Passlib (PBKDF2-SHA256) — secure password hashing
	•	SessionMiddleware — cookie-based authentication

⚠️ Disclaimer — Use of AI Assistance

This project was developed with the assistance of AI tools (ChatGPT by OpenAI) to streamline the development process.

AI was primarily used for:
	•	Generating boilerplate code and repetitive functions
	•	Designing HTML/CSS templates and improving UI styling
	•	Providing guidance on best practices and debugging support

All critical logic, reasoning, data modeling, and architectural decisions — including database design, authentication flow, and feature implementation — were conceptualized, coded, and refined by a human developer.

The AI served as a productivity enhancer, not a replacement for human creativity or understanding.

💡 This project demonstrates the powerful synergy between human intelligence and AI assistance in modern software development.

Created by Gonzalo Fernandez de Cordoba
Built as a learning and portfolio project — minimal yet powerful.