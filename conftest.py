import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 900}}


@pytest.fixture(autouse=True)
def _page_defaults(page):
    page.set_default_timeout(15_000)
    yield


@pytest.fixture
def dialogs(page):
    """Records any JavaScript alert/confirm the page opens (used for the XSS check)."""
    seen = []

    def _on_dialog(d):
        seen.append(d.message)
        d.dismiss()

    page.on("dialog", _on_dialog)
    return seen


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        page = item.funcargs.get("page")
        if page is not None:
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            name = "".join(c if c.isalnum() or c in "-_" else "_" for c in item.name)
            try:
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{name}.png"), full_page=True)
            except Exception:
                pass
