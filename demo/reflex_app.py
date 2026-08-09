"""
Minimal Reflex app entrypoint for the demo.

This file aims to be compatible with the Reflex API commonly used in recent releases.
It creates an `app` object and registers the users page at the root route `/`.

If your installed Reflex version uses slightly different APIs, this file attempts the
most common invocation patterns (rx.App(state=...), app.add_page(...), app.compile()).
If you see runtime errors when starting Reflex, tell me the exact reflex version and
the traceback and I will adapt this file to that concrete API.

The UI is intentionally small and focuses on registering the page. The UsersState
methods perform server-side queries via the Resource layer; those are unchanged.

Run the Reflex app using your Reflex CLI command (typically `reflex run`).
"""
from typing import List, Dict, Any

try:
    import reflex as rx
except Exception:
    rx = None

from demo.db import get_session
from demo.serializers import serialize_user
from reflex_admin.admin import admin_site
from reflex_admin.core.resource import Resource
from demo.ui_helpers import format_range

# Find the registered User resource
UserResource: Resource | None = None
for r in admin_site.get_resources().values():
    if getattr(r.model, "__name__", "") == "User":
        UserResource = r
        break

# Import demo.admin to ensure registration if not already found
if UserResource is None:
    import demo.admin as _
    for r in admin_site.get_resources().values():
        if getattr(r.model, "__name__", "") == "User":
            UserResource = r
            break

if rx is None:
    # Reflex is not installed. This module is still importable for static checks, but
    # attempting to start the UI will raise a clear error.
    if __name__ == "__main__":
        print("Reflex is not installed. Install it with `pip install reflex` to run the demo UI.")
    raise RuntimeError("Reflex is not installed")


class UsersState(rx.State):
    # Serializable UI state only
    search: str = ""
    page: int = 1
    page_size: int = 20
    sort_field: str = ""
    sort_desc: bool = False

    loading: bool = False
    error: str = ""

    total: int = 0
    items: List[Dict[str, Any]] = []
    selected: Dict[str, Any] | None = None

    # Server-side helper
    @classmethod
    def _fetch(cls, search: str, page: int, page_size: int, sort_field: str, sort_desc: bool):
        resource: Resource = UserResource
        with get_session() as session:
            res = resource.list(
                session=session,
                search=search,
                sort_field=sort_field or None,
                sort_desc=bool(sort_desc),
                page=page,
                page_size=page_size,
                filters=[],
            )
            items = [serialize_user(i) for i in res["items"]]
            return {"items": items, "total": res["total"], "page": res["page"], "page_size": res["page_size"]}

    # Derived reactive vars for pagination display
    @rx.var
    def page_label(self) -> str:
        return f"Page {self.page}"

    @rx.var
    def prev_disabled(self) -> bool:
        return self.page <= 1

    @rx.var
    def next_disabled(self) -> bool:
        return (self.page * self.page_size) >= self.total

    @rx.var
    def range_label(self) -> str:
        return format_range(self.total, self.page, self.page_size)

    # Actions
    def load(self):
        self.loading = True
        self.error = ""
        try:
            result = UsersState._fetch(self.search, self.page, self.page_size, self.sort_field, self.sort_desc)
            self.items = result["items"]
            self.total = result["total"]
            self.page = result["page"]
            self.page_size = result["page_size"]
        except Exception:
            self.error = "Unable to load users"
        finally:
            self.loading = False

    def search_action(self, val: str = None):
        if val is not None:
            self.search = val
        self.page = 1
        self.load()

    def set_page(self, page: int):
        self.page = max(1, page)
        self.load()

    def next_page(self):
        max_page = max(1, (self.total + self.page_size - 1) // self.page_size)
        if self.page < max_page:
            self.page += 1
            self.load()

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.load()

    def set_sort(self, field: str):
        if self.sort_field == field:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_field = field
            self.sort_desc = False
        self.load()

    def refresh(self):
        self.load()

    def view(self, _id: int):
        try:
            with get_session() as session:
                obj = UserResource.get(session, _id)
                if obj is None:
                    self.error = "Not found"
                    return
                self.selected = serialize_user(obj)
        except Exception:
            self.error = "Unable to load user"


# Basic UI builders using Reflex components
# Keep UI simple and driven by UsersState

def users_page() -> rx.Component:
    header = rx.box(rx.heading("Reflex Admin - Users"))

    # Use the Reflex lifecycle hook to trigger initial load when the page mounts.
    # Prefer common hooks in order: use_effect, use_effect_once, on_mount.
    if hasattr(rx, "use_effect"):
        rx.use_effect(UsersState.load)
    elif hasattr(rx, "use_effect_once"):
        rx.use_effect_once(UsersState.load)
    elif hasattr(rx, "on_mount"):
        rx.on_mount(UsersState.load)

    # For this task render a simple table of email, name, active, created_at from UsersState.items
    # Keep search input and Search button as previously implemented
    search_input = rx.input(value=UsersState.search, on_change=UsersState.set_state("search"), placeholder="Search users...")
    search_btn = rx.button("Search", on_click=UsersState.search_action)

    # Table header
    header_row = rx.hstack(
        rx.box(rx.strong("Email")),
        rx.box(rx.strong("Name")),
        rx.box(rx.strong("Active")),
        rx.box(rx.strong("Created At")),
    )

    # Table body (reactive iteration using rx.foreach)
    if UsersState.loading:
        rows_component = rx.text("Loading...")
    elif UsersState.error:
        rows_component = rx.box(rx.text(UsersState.error), rx.button("Retry", on_click=UsersState.load))
    elif not UsersState.items:
        rows_component = rx.text("No users found.")
    else:
        def user_row(item):
            # Use item.get(...) fallback to avoid KeyError and support plain dicts/objects
            email = item.get("email") if isinstance(item, dict) else getattr(item, "email", None)
            name = item.get("name") if isinstance(item, dict) else getattr(item, "name", None)
            active = item.get("active") if isinstance(item, dict) else getattr(item, "active", False)
            created = item.get("created_at") if isinstance(item, dict) else getattr(item, "created_at", None)
            return rx.hstack(
                rx.text(email or "-"),
                rx.text(name or "-"),
                rx.text("✓" if active else ""),
                rx.text(created or "-"),
            )

        # Use rx.foreach to render rows reactively from UsersState.items
        rows_component = rx.foreach(UsersState.items, user_row)

    # Pagination controls: Previous | Page N | Next (reactive via @rx.var on UsersState)
    prev_btn = rx.button("Previous", on_click=UsersState.prev_page, disabled=UsersState.prev_disabled())
    page_text = rx.text(UsersState.page_label())
    next_btn = rx.button("Next", on_click=UsersState.next_page, disabled=UsersState.next_disabled())

    pagination_row = rx.hstack(prev_btn, page_text, next_btn)

    range_text = rx.text(UsersState.range_label())

    # Build a table (header + rows)
    table = rx.vstack(header_row, rows_component)

    # New body: hide pagination while loading
    body = rx.vstack(
        rx.cond(
            UsersState.loading,
            rx.text("Loading..."),
            rx.vstack(
                rx.cond(
                    UsersState.error,
                    rx.text(UsersState.error),
                    rx.cond(
                        UsersState.total == 0,
                        rx.text("No users found."),
                        table,
                    ),
                ),
                pagination_row,
                rx.box(UsersState.range_label()),
            ),
        ),
    )

    return rx.vstack(header, rx.hstack(search_input, search_btn), body)


# Create the Reflex App and register the page. Attempt common API patterns.
app = None
try:
    # Typical recent API: rx.App(state=UsersState)
    app = rx.App(state=UsersState)
    try:
        app.add_page(users_page, route="/")
    except TypeError:
        # Some versions use add_page(func) without route kw
        app.add_page(users_page)
except Exception:
    # Fallback: try older pattern
    try:
        app = rx.App()
        try:
            app.add_page(users_page, route="/")
        except Exception:
            app.add_page(users_page)
    except Exception:
        # If app creation fails, re-raise with helpful message
        raise

# Try to compile the app if API supports it (no-op on some versions)
try:
    if hasattr(app, "compile"):
        app.compile()
except Exception:
    # Not fatal; the Reflex CLI may handle compilation/run
    pass

# Expose app for Reflex CLI discovery
__all__ = ["app", "UsersState", "users_page"]
