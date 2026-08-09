"""
Minimal Reflex app for Users vertical slice.

This file expects Reflex to be installed. It is written against a common modern Reflex/Pynecone-like API where
- `rx` is imported as `import reflex as rx`
- Pages are functions returning component trees
- rx.State subclasses are used for server-driven state with methods as actions

If the installed Reflex version differs, you may need to adjust the State/action APIs accordingly.

Run instructions (example):
1. Install Reflex (recommended in a venv):
   pip install "reflex"
2. Create or seed the demo DB (SQLite default):
   python -m demo.seed --sqlite
3. Start Reflex app (may vary by Reflex version):
   reflex run

Or run this module directly for a simple check (does not start Reflex server):
   python -m demo.reflex_app

"""
try:
    import reflex as rx
except Exception:
    rx = None

from typing import List, Dict, Any
from demo.db import get_session, DATABASE_URL
from demo.serializers import serialize_user
from reflex_admin.admin import admin_site
from reflex_admin.core.resource import Resource

# pick the registered User resource
# admin_site holds registered resources by model tablename; find the User resource
UserResource = None
for r in admin_site.get_resources().values():
    if r.model.__name__ == "User":
        UserResource = r
        break

if UserResource is None:
    # fallback: import demo admin to ensure registration
    import demo.admin as _
    for r in admin_site.get_resources().values():
        if r.model.__name__ == "User":
            UserResource = r
            break

if rx is None:
    # Reflex is not installed; provide a helpful message when run as script
    if __name__ == "__main__":
        print("Reflex is not installed. Install it with `pip install reflex` to run the demo UI.")
    raise RuntimeError("Reflex is not installed")


class UsersState(rx.State):
    # UI state (serializable primitives only)
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

    @rx.var
    def columns(self) -> List[str]:
        # derive columns from resource metadata
        cols = list(UserResource.list_display) if getattr(UserResource, "list_display", None) else [f.name for f in UserResource.get_fields()]
        return list(cols)

    @classmethod
    def _fetch(cls, search: str, page: int, page_size: int, sort_field: str, sort_desc: bool):
        # server-side data fetch
        resource: Resource = UserResource
        with get_session() as session:
            try:
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
            except Exception as e:
                raise

    def load(self):
        # UI action to load data; calls server-side helper
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
        # triggered by search box (on enter or search button)
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
        # fetch single object and open detail
        try:
            with get_session() as session:
                obj = UserResource.get(session, _id)
                if obj is None:
                    self.error = "Not found"
                    return
                self.selected = serialize_user(obj)
        except Exception:
            self.error = "Unable to load user"


# UI rendering functions

def header():
    return rx.box(
        rx.heading("Reflex Admin - Users"),
    )


def search_row():
    return rx.hstack(
        rx.input(value=UsersState.search, on_change=UsersState.set_state("search"), placeholder="Search users..."),
        rx.button("Search", on_click=UsersState.search_action),
        rx.button("Refresh", on_click=UsersState.refresh),
    )


def table_header():
    cols = UsersState.columns()
    header_cells = []
    for c in cols:
        # clicking header toggles sort
        header_cells.append(rx.button(c, on_click=lambda _c=c: UsersState.set_sort(_c)))
    header_cells.append(rx.box("Actions"))
    return rx.hstack(*header_cells)


def table_rows():
    if UsersState.loading:
        return rx.text("Loading...")
    if UsersState.error:
        return rx.box(rx.text(UsersState.error), rx.button("Retry", on_click=UsersState.load))
    if not UsersState.items:
        return rx.text("No users found.")

    rows = []
    cols = UsersState.columns()
    for item in UsersState.items:
        cells = []
        for c in cols:
            v = item.get(c)
            # format boolean/date
            if isinstance(v, bool):
                cells.append(rx.text("✓" if v else ""))
            else:
                cells.append(rx.text(v if v is not None else "-"))
        # actions
        cells.append(rx.button("View", on_click=lambda _id=item["id"]: UsersState.view(_id)))
        rows.append(rx.hstack(*cells))
    return rx.vstack(*rows)


def pagination_row():
    return rx.hstack(
        rx.button("Previous", on_click=UsersState.prev_page),
        rx.text(lambda: f"Page {UsersState.page}"),
        rx.button("Next", on_click=UsersState.next_page),
    )


def users_page():
    return rx.vstack(
        header(),
        search_row(),
        table_header(),
        table_rows(),
        pagination_row(),
        rx.box(rx.text(lambda: f"Showing {(UsersState.page-1)*UsersState.page_size+1}–{min(UsersState.page*UsersState.page_size, UsersState.total)} of {UsersState.total}")),
    )

# Register page if Reflex app discovery expects it
if __name__ == "__main__":
    print("This module defines a Reflex State and pages. Start the Reflex app per Reflex docs (e.g. `reflex run`).")
