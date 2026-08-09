from reflex_admin.core.resource import Resource
from demo.models import User
from reflex_admin.pydantic.schemas import UserCreate, UserUpdate

class UserAdmin(Resource):
    model = User
    list_display = ["email", "name", "active", "created_at"]
    search_fields = ["email", "name"]
    create_schema = UserCreate
    update_schema = UserUpdate


# simple registration
from reflex_admin.admin import admin_site
admin_site.register(UserAdmin())
