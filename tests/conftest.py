import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from demo.models import Base

@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:", echo=False)

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.rollback()
    s.close()
