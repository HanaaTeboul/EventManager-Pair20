from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DB_DIR = "/app/data" if os.path.isdir("/app/data") else os.getcwd()
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'events.db')}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()