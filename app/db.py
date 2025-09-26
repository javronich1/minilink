from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./minilink.sqlite3"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session