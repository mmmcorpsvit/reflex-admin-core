[Pull Request]
Title: Add reactive users table, pagination, sorting, and retry

This PR implements a minimal UI for the Reflex admin demo:

- demo/reflex_app.py
  - Adds a reactive Users page and UsersState with server-driven list loading
  - Renders UsersState.items reactively using rx.foreach
  - Adds pagination controls (Previous / Page N / Next) with reactive enabled/disabled states
  - Hides pagination while loading and shows a Loading indicator
  - Restores a Retry button in the error state
  - Adds column sorting via UsersState.sort_by and clickable Email/Name headers

- tests/unit/test_search_forwarding.py
  - Adds a unit test to ensure the search parameter is forwarded to Resource.list

Notes:
- The UI wiring uses common Reflex APIs (rx.App, rx.State, rx.foreach, rx.var, rx.cond).
- The code avoids introducing new abstractions or changing the Resource / DB layers.
- If your installed Reflex version uses different lifecycle or iteration APIs, I can adjust the small parts that rely on rx.foreach or rx.var. Please run the app locally and provide the reflex version and any traceback if adjustments are needed.

How to test locally:
1. Syntax check: python -m compileall .
2. Unit tests: pytest -q
3. Seed DB (sqlite) and run demo: python -m demo.seed --sqlite && reflex run

If this looks good I can open a PR from reflex-admin/poc into main. Otherwise tell me what to change.
