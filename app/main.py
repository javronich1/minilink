from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from app.db import init_db, get_session
from sqlmodel import Session, select
from app.models import Link
from app.schemas import LinkCreate, LinkRead, LinkUpdate, StatsRead
from app.services import choose_code, sanitize_scheme
from datetime import datetime
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse

app = FastAPI(title="minilink")

import os
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, session: Session = Depends(get_session)):
    # basic scheme validation (avoid open redirects)
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
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

@app.get("/api/links", response_model=list[LinkRead])
def list_links(session: Session = Depends(get_session)):
    return session.exec(select(Link)).all()

@app.get("/api/links/{code}", response_model=LinkRead)
def read_link(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return link

@app.patch("/api/links/{code}", response_model=LinkRead)
def update_link(code: str, payload: LinkUpdate, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")

    # update original_url
    if payload.original_url is not None:
        if not sanitize_scheme(str(payload.original_url)):
            raise HTTPException(status_code=422, detail="Only http/https URLs are allowed")
        link.original_url = str(payload.original_url)

    # update expires_at
    if payload.expires_at is not None:
        link.expires_at = payload.expires_at

    # change short code (custom alias)
    if payload.custom_code and payload.custom_code != code:
        exists = session.exec(select(Link).where(Link.short_code == payload.custom_code)).first()
        if exists:
            raise HTTPException(status_code=409, detail="Custom code already in use")
        link.short_code = payload.custom_code

    session.add(link)
    session.commit()
    session.refresh(link)
    return link

@app.delete("/api/links/{code}", status_code=204)
def delete_link(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(link)
    session.commit()
    # 204 No Content → return nothing

@app.get("/r/{code}")
def redirect(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")

    # handle expiry if set
    if link.expires_at and link.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link expired")

    # analytics
    link.click_count += 1
    link.last_accessed = datetime.utcnow()
    session.add(link)
    session.commit()

    # 307 preserves method (POST/GET), good for redirects
    return RedirectResponse(url=link.original_url, status_code=307)

@app.get("/api/links/{code}/stats", response_model=StatsRead)
def link_stats(code: str, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return {"click_count": link.click_count, "last_accessed": link.last_accessed}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create", response_class=HTMLResponse)
def create_form(
    request: Request,
    original_url: str = Form(...),
    session: Session = Depends(get_session),
):
    # Reuse the same validation logic
    if not sanitize_scheme(original_url):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Only http/https URLs are allowed"},
            status_code=422,
        )
    # Choose a random code (no custom alias in the form to keep it simple)
    code = choose_code(None)
    # Ensure unique; regenerate if collision (rare, but safe)
    while session.exec(select(Link).where(Link.short_code == code)).first():
        code = choose_code(None)

    link = Link(short_code=code, original_url=original_url)
    session.add(link)
    session.commit()
    session.refresh(link)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "short_code": code},
        status_code=201,
    )

@app.get("/links", response_class=HTMLResponse)
def list_links_ui(request: Request, session: Session = Depends(get_session)):
    links = session.exec(
        select(Link).order_by(Link.click_count.desc(), Link.last_accessed.desc())
    ).all()
    return templates.TemplateResponse("list.html", {"request": request, "links": links})

