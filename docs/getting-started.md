# Getting started (short)

1. Install dependencies:
   - `poetry install` or `pip install -r requirements.txt`

2. Seed (SQLite):
   - `python -m demo.seed --sqlite`

3. Run tests:
   - `pytest -q`

4. Run Reflex UI (optional):
   - Install reflex: `poetry add -E ui`
   - Follow Reflex docs to run the app; demo/app.py contains a reference.
