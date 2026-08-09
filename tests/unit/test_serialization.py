from demo.models import User
from demo.serializers import serialize_user


def test_serialize_user():
    u = User(id=1, email="a@b.com", name="A", active=True)
    out = serialize_user(u)
    assert out["id"] == 1
    assert out["email"] == "a@b.com"
    assert out["name"] == "A"
    assert out["active"] is True
