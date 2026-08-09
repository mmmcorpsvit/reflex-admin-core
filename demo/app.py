"""
This is a small conceptual integration example for Reflex.
To run the UI, install Reflex and adapt per Reflex docs.

The file demonstrates how the renderer would be used, but is not a
fully runnable Reflex application in this POC.
"""
from reflex_admin.admin import admin_site
from reflex_admin.reflex.renderer import render_list_page
from demo.models import User
from reflex_admin.core.resource import Resource
from reflex_admin.pydantic.schemas import UserCreate, UserUpdate

# Define and register resource
class UserAdmin(Resource):
    model = User
    list_display = ["id", "email", "name", "active", "created_at"]
    search_fields = ["email", "name"]
    create_schema = UserCreate
    update_schema = UserUpdate

admin_site.register(UserAdmin())

# The Reflex app would call the renderer with a live session and query results.
# See docs and REFLEX README for instructions to "wire" a Reflex State to call
# Resource.list(...) and render the returned items using render_list_page.
