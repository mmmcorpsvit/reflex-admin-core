"""
Minimal Reflex renderer shim.

This module intentionally keeps the core free of Reflex imports.
If Reflex is installed and the user wants to run a Reflex UI, this module
provides helper functions to convert semantic models into Reflex components.

The POC includes a very small renderer that demonstrates the idea but is
not a full production renderer. It imports Reflex at runtime only if available.
"""
from typing import Any, List, Optional

try:
    import reflex as rx  # optional dependency
except Exception:
    rx = None

def requires_reflex(func):
    def wrapper(*args, **kwargs):
        if rx is None:
            raise RuntimeError("Reflex is not installed. Install with `pip install reflex` to use the UI.")
        return func(*args, **kwargs)
    return wrapper

@requires_reflex
def render_list_page(resource, *, items: List[Any], total: int, page: int, page_size: int):
    """
    Returns a simple Reflex page definition (conceptual).
    The demo app (demo/app.py) shows how to integrate this with a Reflex app.
    """
    cols = resource.list_display or [f.name for f in resource.get_fields()]
    # This function returns a conceptual component tree — actual usage depends on Reflex app structure.
    return rx.box(
        rx.heading(resource.model.__name__),
        rx.text(f"Showing {len(items)} of {total}"),
        # The developer will map `cols` and `items` into rx components (table rows/cells)
    )
