# Demo: how to run the Reflex UI (notes)

This demo requires Reflex to be installed in the environment. The code in demo/reflex_app.py
is written to be compatible with common Reflex APIs, but you may need to adapt it to the
installed Reflex version.

Quick start (example):

1. Install optional UI deps (Reflex)
   pip install "reflex"

2. Seed demo DB (SQLite)
   python -m demo.seed --sqlite

3. Start Reflex app (depends on Reflex version):
   reflex run

If your Reflex version requires a different startup flow, consult Reflex docs. The demo defines
UsersState and users_page() in demo/reflex_app.py — use your Reflex project's routing to expose
users_page as a route, or adapt demo/reflex_app.py to the Reflex project layout.
