from sqlmodel import SQLModel, create_engine, Session

# sqlite database URL
DATABASE_URL = "sqlite:///./minilink.sqlite3"  

# create the database engine to manage connections to db
engine = create_engine(DATABASE_URL, echo=False)

# dependency to get a session, used in FastAPI endpoints, yields sqlmodel session
def get_session():
    with Session(engine) as session:
        yield session

# function to initialize the database (create tables)
def init_db():
    from app import models
    SQLModel.metadata.create_all(engine)