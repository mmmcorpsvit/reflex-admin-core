from demo.models import User
from reflex_admin.core.resource import Resource
from reflex_admin.pydantic.schemas import UserCreate, UserUpdate

def test_crud(session):
    # create
    resource = Resource(model=User, create_schema=UserCreate, update_schema=UserUpdate)
    payload = {"email": "a@test.com", "name": "Alpha", "active": True}
    obj = resource.create(session, payload)
    assert obj.id is not None
    # list
    res = resource.list(session=session, search="a@test.com", page=1, page_size=10)
    assert res["total"] >= 1
    # update
    updated = resource.update(session, obj.id, {"email": "b@test.com", "name": "Beta", "active": False})
    assert updated.email == "b@test.com"
    # get
    got = resource.get(session, obj.id)
    assert got.email == "b@test.com"
    # delete
    ok = resource.delete(session, obj.id)
    assert ok is True
