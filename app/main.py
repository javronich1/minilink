from datetime import datetime
import os
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from sqlmodel import Session, select

from app.db import init_db, get_session
from app.models import Link
from app.schemas import LinkCreate, LinkRead, LinkUpdate, StatsRead
from app.services import choose_code, sanitize_scheme

app = FastAPI(title="minilink")

# DB init (deprecated on_event is fine for this project; we can switch to lifespan later)
@app.on_event("startup")
def on_startup():
    init_db()

# Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# --- Health ---
@app.get("/health")
def health():
    return {"status": "ok"}

# --- API: CREATE ---
@app.post("/api/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, session: Session = Depends(get_session)):
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
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

# --- API: LIST ---
@app.get("/api/links", response_model=list[LinkRead])
def list_links(session: Session = Depends(get_session)):
    return session.exec(select(Link)).all()

# --- API: READ ---
@app.get("/api/links/{code}", response_model=LinkRead)
def read_link(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return link

# --- API: UPDATE ---
@app.patch("/api/links/{code}", response_model=LinkRead)
def update_link(code: str, payload: LinkUpdate, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
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

# --- API: DELETE ---
@app.delete("/api/links/{code}", status_code=204)
def delete_link(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(link)
    session.commit()

# --- Redirect + analytics ---
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

# --- Stats ---
@app.get("/api/links/{code}/stats", response_model=StatsRead)
def link_stats(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return {"click_count": link.click_count, "last_accessed": link.last_accessed}

# --- UI: Home ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create", response_class=HTMLResponse)
def create_form(
    request: Request,
    original_url: str = Form(...),
    label: Optional[str] = Form(None),   # Python 3.9 compatible
    session: Session = Depends(get_session),
):
    if not sanitize_scheme(original_url):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Only http/https URLs are allowed"},
            status_code=422,
        )
    code = choose_code(None)
    while session.exec(select(Link).where(Link.short_code == code)).first():
        code = choose_code(None)

    link = Link(short_code=code, original_url=original_url, label=label)
    session.add(link)
    session.commit()
    session.refresh(link)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "short_code": code},
        status_code=201,
    )

# --- UI: Analytics page (server-rendered first, sorted by clicks then last_accessed) ---
@app.get("/links", response_class=HTMLResponse)
def list_links_ui(request: Request, session: Session = Depends(get_session)):
    links = session.exec(
        select(Link).order_by(Link.click_count.desc(), Link.last_accessed.desc())
    ).all()
    return templates.TemplateResponse("list.html", {"request": request, "links": links})