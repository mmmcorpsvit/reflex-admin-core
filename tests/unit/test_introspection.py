from reflex_admin.sqlalchemy.introspection import inspect_model_fields, get_model_column_names
from demo.models import User, Post, Category


def test_introspection_simple():
    fields = inspect_model_fields(User)
    names = [f.name for f in fields]
    assert "email" in names
    assert "id" in names

    # find types
    email_field = next(f for f in fields if f.name == "email")
    assert email_field.type in ("string", "text")

    posts = inspect_model_fields(Post)
    pk = next(f for f in posts if f.name == "id")
    assert pk.primary_key


def test_get_column_names():
    cols = get_model_column_names(User)
    assert "email" in cols
    assert "id" in cols
