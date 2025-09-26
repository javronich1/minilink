from fastapi import FastAPI, Depends, HTTPException, status
from app.db import init_db, get_session
from sqlmodel import Session, select
from app.models import Link
from app.schemas import LinkCreate, LinkRead
from app.services import choose_code, sanitize_scheme

app = FastAPI(title="minilink")

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