from reflex_admin.core.resource import Resource
from demo.models import User
from reflex_admin.sqlalchemy.introspection import inspect_model_fields

def test_inspect_fields():
    fields = inspect_model_fields(User)
    names = [f.name for f in fields]
    assert "email" in names
    assert "id" in names

def test_resource_default_fields():
    r = Resource(model=User, list_display=["email", "name"], search_fields=["email"])
    f = r.get_fields()
    assert any(fd.name == "email" for fd in f)
