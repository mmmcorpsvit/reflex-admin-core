from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///demo.db")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def get_session():
    """Yields a SQLAlchemy session. Caller is responsible for calling within a `with` block."""
    s = SessionLocal()
    try:
        yield s
n    finally:
        s.close()
