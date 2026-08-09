from reflex_admin.sqlalchemy.queries import apply_search, apply_sort, apply_filters
from demo.models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from demo.models import Base
from reflex_admin.core.filters import FilterExpression

def setup_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    u1 = User(email="john@example.com", name="John")
    u2 = User(email="jane@sample.org", name="Jane")
    s.add_all([u1, u2])
    s.commit()
    return s

def test_search():
    s = setup_db()
    q = s.query(User)
    q = apply_search(q, User, "john", ["email", "name"])
    res = q.all()
    assert len(res) == 1
    assert res[0].email == "john@example.com"
    s.close()

def test_filter_and_sort():
    s = setup_db()
    q = s.query(User)
    q = apply_filters(q, User, [FilterExpression(field="email", operator="contains", value="example")])
    q = apply_sort(q, User, "name", sort_desc=False)
    res = q.all()
    assert len(res) == 1
    s.close()
