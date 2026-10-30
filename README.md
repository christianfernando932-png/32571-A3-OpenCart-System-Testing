# TC04–TC06: Product Search, Category Navigation, Product Details

Automated tests for https://opencart.abstracta.us/ using pytest + Playwright.

## Setup (once)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Run

```bash
pytest                          # all 30, headless, writes report.html
pytest --headed --slowmo 500    # watch it in a browser window
pytest -k tc05                  # one test case only
```

Expected result: **28 passed, 2 xfailed**. The 2 xfailed rows are defect D01 (wrong "no results" message), confirmed and documented in `TEST_CASES.md`.

## Files

| File | What it is |
|---|---|
| `test_tc04_product_search.py` | TC04, 3 scenarios |
| `test_tc05_category_navigation.py` | TC05, 3 scenarios |
| `test_tc06_product_details.py` | TC06, 3 scenarios |
| `helpers.py` | Shared selectors and page readers |
| `conftest.py` | Viewport, timeouts, a screenshot per test |
| `TEST_CASES.md` | Steps and expected results as tables |
| `report.html` | Full run, 31 Oct 2026: 28 passed, 2 xfailed |
| `*.png` | One screenshot per test run (30) |
