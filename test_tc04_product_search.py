"""TC04 / F04 - Product Search

S1  Keyword search from the header (button and Enter, case, partial words)
S2  Advanced search criteria (descriptions, category, subcategories)
S3  No-match and invalid input (nonsense, SQL, script, very long, empty)
"""
import pytest
from playwright.sync_api import expect

from helpers import (
    NO_SEARCH_RESULTS_MSG,
    assert_names_contain,
    assert_no_server_error,
    content_messages,
    header_search,
    open_home,
    open_search,
    result_names,
    showing_text,
)

MAC_RESULTS = ["iMac", "MacBook", "MacBook Air", "MacBook Pro"]


def run_criteria_search(page):
    """Click the Search button under the criteria form and wait for the new page."""
    with page.expect_navigation():
        page.locator("#button-search").click()


# ---------------- S1: keyword search from the header ----------------

def test_tc04_s1_keyword_search_from_header(page):
    open_home(page)

    # 1. "mac" with the search button
    header_search(page, "mac")
    expect(page).to_have_title("Search - mac")
    expect(page.locator("#content h1")).to_have_text("Search - mac")
    assert result_names(page) == MAC_RESULTS
    assert showing_text(page) == "Showing 1 to 4 of 4 (1 Pages)"
    # the keyword is carried into the search-criteria box
    expect(page.locator("#input-search")).to_have_value("mac")

    # 2. "MAC" with Enter: search is not case-sensitive
    header_search(page, "MAC", press_enter=True)
    assert result_names(page) == MAC_RESULTS

    # 3. multi-word partial name narrows the list
    header_search(page, "Mac Bo")
    assert result_names(page) == ["MacBook", "MacBook Air", "MacBook Pro"]

    # 4. single exact product
    header_search(page, "iphone")
    assert result_names(page) == ["iPhone"]
    assert_names_contain(result_names(page), "iphone")

    # 5. a result opens the matching product page
    page.locator(".product-thumb h4 a", has_text="iPhone").click()
    expect(page.locator("#content h1")).to_have_text("iPhone")


# ---------------- S2: advanced search criteria ----------------

def test_tc04_s2_advanced_search_criteria(page):
    # 1. word that appears only in descriptions
    open_search(page, "stunning")
    assert result_names(page) == []

    page.locator("#description").check()
    run_criteria_search(page)
    assert result_names(page) == ["HP LP3065", "iMac"]
    expect(page.locator("#description")).to_be_checked()

    # 2. category filter: Desktops, without subcategories
    page.locator("#description").uncheck()
    page.locator("#input-search").fill("mac")
    page.locator("select[name='category_id']").select_option(label="Desktops")
    run_criteria_search(page)
    assert result_names(page) == ["MacBook", "MacBook Air"]

    # 3. same, with "Search in subcategories" (adds iMac from Desktops > Mac)
    page.locator("input[name='sub_category']").check()
    run_criteria_search(page)
    assert result_names(page) == ["iMac", "MacBook", "MacBook Air"]

    # 4. a different category: Laptops & Notebooks
    page.locator("select[name='category_id']").select_option(label="Laptops & Notebooks")
    run_criteria_search(page)
    assert result_names(page) == ["MacBook", "MacBook Air", "MacBook Pro"]
    assert_no_server_error(page)


# ---------------- S3: no-match and invalid input ----------------

INVALID_INPUTS = [
    pytest.param("zzqxnotreal", id="nonsense"),
    pytest.param("' OR 1=1--", id="sql-injection"),
    pytest.param("<script>alert(1)</script>", id="script-tag"),
    pytest.param("a" * 300, id="300-chars"),
    pytest.param("", id="empty"),
]


@pytest.mark.parametrize("keyword", INVALID_INPUTS)
def test_tc04_s3_no_match_and_invalid_input(page, dialogs, keyword):
    open_home(page)
    header_search(page, keyword)

    assert result_names(page) == [], "no product should be listed"
    assert showing_text(page) == ""
    assert_no_server_error(page)
    assert dialogs == [], f"page opened a JavaScript dialog: {dialogs}"
    if keyword:
        # the keyword is shown back as plain text, not run as HTML
        expect(page.locator("#content h1")).to_have_text(f"Search - {keyword}")


@pytest.mark.xfail(
    strict=True,
    reason="D01: no-result search shows 'Your shopping cart is empty!' "
    "instead of 'There is no product that matches the search criteria.'",
)
def test_tc04_s3_no_result_message(page):
    open_search(page, "zzqxnotreal")
    assert NO_SEARCH_RESULTS_MSG in content_messages(page)
