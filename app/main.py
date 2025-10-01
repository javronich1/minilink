# app/main.py
from datetime import datetime
import os
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import init_db, get_session
from app.models import Link, User
from app.schemas import LinkCreate, LinkRead, LinkUpdate, StatsRead
from app.services import choose_code, sanitize_scheme
from app.auth import hash_password, verify_password

from starlette.middleware.sessions import SessionMiddleware

# -------------------------------
# Lifespan (startup/shutdown)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # DB setup
    yield
    # no cleanup needed for now

# -------------------------------
# App + Middleware
# -------------------------------
app = FastAPI(title="minilink", lifespan=lifespan)

# Secure session
app.add_middleware(SessionMiddleware, secret_key="change-me-please-very-secret")

# Jinja
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# -------------------------------
# Helper functions
# -------------------------------
def get_current_user(request: Request, session: Session) -> Optional[User]:
    uid = request.session.get("user_id")
    if not uid:
        return None
    return session.get(User, uid)

# -------------------------------
# Health check function
# -------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------
# API: CREATE LINK
# -------------------------------
@app.post("/api/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(
    payload: LinkCreate,
    request: Request,
    session: Session = Depends(get_session),
):
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    if not sanitize_scheme(str(payload.original_url)):
        raise HTTPException(status_code=422, detail="Only http/https URLs are allowed")

    code = choose_code(payload.custom_code)
    exists = session.exec(select(Link).where(Link.short_code == code)).first()
    if exists:
        raise HTTPException(status_code=409, detail="Custom code already in use")

    link = Link(
        short_code=code,
        original_url=str(payload.original_url),
        expires_at=payload.expires_at,
        label=payload.label,
        user_id=user.id,
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

# -------------------------------
# API: LIST LINKS
# -------------------------------
@app.get("/api/links", response_model=list[LinkRead])
def list_links(request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return session.exec(select(Link).where(Link.user_id == user.id)).all()

# -------------------------------
# API: READ LINK
# -------------------------------
@app.get("/api/links/{code}", response_model=LinkRead)
def read_link(code: str, request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    link = session.exec(
        select(Link).where(Link.short_code == code, Link.user_id == user.id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return link

# -------------------------------
# API: UPDATE LINK
# -------------------------------
@app.patch("/api/links/{code}", response_model=LinkRead)
def update_link(
    code: str,
    payload: LinkUpdate,
    request: Request,
    session: Session = Depends(get_session),
):
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    link = session.exec(
        select(Link).where(Link.short_code == code, Link.user_id == user.id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")

    if payload.original_url is not None:
        if not sanitize_scheme(str(payload.original_url)):
            raise HTTPException(status_code=422, detail="Only http/https URLs are allowed")
        link.original_url = str(payload.original_url)

    if payload.expires_at is not None:
        link.expires_at = payload.expires_at

    if payload.label is not None:
        link.label = payload.label

    if payload.custom_code and payload.custom_code != code:
        exists = session.exec(select(Link).where(Link.short_code == payload.custom_code)).first()
        if exists:
            raise HTTPException(status_code=409, detail="Custom code already in use")
        link.short_code = payload.custom_code

    session.add(link)
    session.commit()
    session.refresh(link)
    return link

# -------------------------------
# API: DELETE LINK
# -------------------------------
@app.delete("/api/links/{code}", status_code=204)
def delete_link(
    code: str,
    request: Request,
    session: Session = Depends(get_session),
):
    user = get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    link = session.exec(
        select(Link).where(Link.short_code == code, Link.user_id == user.id)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")

    session.delete(link)
    session.commit()

# -------------------------------
# Redirect + analytics
# -------------------------------
@app.get("/r/{code}")
def redirect(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")

    if link.expires_at and link.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link expired")

    link.click_count += 1
    link.last_accessed = datetime.utcnow()
    session.add(link)
    session.commit()

    return RedirectResponse(url=link.original_url, status_code=307)

# -------------------------------
# API: Stats
# -------------------------------
@app.get("/api/links/{code}/stats", response_model=StatsRead)
def link_stats(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return {"click_count": link.click_count, "last_accessed": link.last_accessed}

# -------------------------------
# AUTH (signup / login / logout)
# -------------------------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "signup_error": "Username already taken"},
            status_code=400,
        )

    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)

@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "login_error": "Invalid credentials"},
            status_code=400,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# -------------------------------
# UI: Home (form)
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.post("/create", response_class=HTMLResponse)
def create_form(
    request: Request,
    original_url: str = Form(...),
    label: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    user = get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if not sanitize_scheme(original_url):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Only http/https URLs are allowed", "user": user},
            status_code=422,
        )

    code = choose_code(None)
    while session.exec(select(Link).where(Link.short_code == code)).first():
        code = choose_code(None)

    link = Link(short_code=code, original_url=original_url, label=label, user_id=user.id)
    session.add(link)
    session.commit()
    session.refresh(link)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "short_code": code, "user": user},
        status_code=201,
    )

# -------------------------------
# UI: Analytics page
# -------------------------------
@app.get("/links", response_class=HTMLResponse)
def list_links_ui(request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    links = session.exec(
        select(Link)
        .where(Link.user_id == user.id)
        .order_by(Link.click_count.desc(), Link.last_accessed.desc())
    ).all()

    return templates.TemplateResponse("list.html", {"request": request, "links": links, "user": user})