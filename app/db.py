# app/db.py
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./minilink.sqlite3"  # or your current path
engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    # IMPORTANT: import models so SQLModel.metadata knows about User & Link
    from app import models  # <-- keep this import inside the function
    SQLModel.metadata.create_all(engine)