from reflex_admin.core.resource import Resource
from demo.models import User
from reflex_admin.core.resource import Resource as R
from reflex_admin.core.resource import Resource


def test_resource_valid_config():
    class MyRes(Resource):
        model = User
        list_display = ["email", "name"]
        search_fields = ["email"]

    r = MyRes()
    assert r.model == User


def test_resource_invalid_list_display():
    try:
        class BadRes(Resource):
            model = User
            list_display = ["nope"]
        BadRes()
        assert False, "Should have raised"
    except ValueError as e:
        assert "Invalid list_display field" in str(e)
