"""TC05 / F05 - Category Navigation

S1  Top menu and breadcrumbs (dropdowns, "Show All", subcategories, links back)
S2  Category counts match what the shopper can reach (left column, Refine Search)
S3  Empty and invalid categories
"""
import re

import pytest
from playwright.sync_api import expect

from helpers import (
    EMPTY_CATEGORY_MSG,
    assert_no_server_error,
    breadcrumb,
    content_messages,
    left_menu_count,
    open_category,
    open_home,
    result_names,
    showing_text,
    top_menu_item,
    total_from_showing,
)


# ---------------- S1: top menu and breadcrumbs ----------------

def test_tc05_s1_top_menu_and_breadcrumbs(page):
    open_home(page)

    # 1. all 8 top-level categories are in the menu
    menu = [t.strip() for t in page.locator("#menu .navbar-nav > li > a").all_inner_texts()]
    assert menu == [
        "Desktops", "Laptops & Notebooks", "Components", "Tablets",
        "Software", "Phones & PDAs", "Cameras", "MP3 Players",
    ]

    # 2. hover Desktops -> dropdown -> "Show All Desktops"
    desktops = top_menu_item(page, "Desktops")
    desktops.hover()
    expect(desktops.locator(".dropdown-menu")).to_be_visible()
    desktops.locator("a.see-all", has_text="Show All Desktops").click()
    expect(page).to_have_title("Desktops")
    expect(page.locator("#content h2").first).to_have_text("Desktops")
    assert breadcrumb(page) == ["", "Desktops"]
    assert len(result_names(page)) == 12
    assert showing_text(page) == "Showing 1 to 12 of 12 (1 Pages)"

    # 3. hover Desktops -> "Mac (1)" subcategory
    desktops = top_menu_item(page, "Desktops")
    desktops.hover()
    desktops.locator(".dropdown-menu a", has_text="Mac (1)").click()
    expect(page.locator("#content h2").first).to_have_text("Mac")
    assert breadcrumb(page) == ["", "Desktops", "Mac"]
    assert result_names(page) == ["iMac"]

    # 4. breadcrumb "Desktops" goes back up one level
    page.locator(".breadcrumb a", has_text="Desktops").click()
    expect(page.locator("#content h2").first).to_have_text("Desktops")

    # 5. category without a dropdown opens directly from the menu
    top_menu_item(page, "Tablets").locator(":scope > a").click()
    expect(page.locator("#content h2").first).to_have_text("Tablets")
    assert result_names(page) == ["Samsung Galaxy Tab 10.1"]

    # 6. home icon in the breadcrumb returns to the home page
    page.locator(".breadcrumb li").first.locator("a").click()
    expect(page).to_have_title("Your Store")


# ---------------- S2: counts match reachable products ----------------

TOP_CATEGORIES = [
    # (menu name, path, count shown next to the name)
    ("Desktops", "20", 13),
    ("Laptops & Notebooks", "18", 5),
    ("Components", "25", 2),
    ("Tablets", "57", 1),
    ("Software", "17", 0),
    ("Phones & PDAs", "24", 3),
    ("Cameras", "33", 2),
    ("MP3 Players", "34", 4),
]


def _refine_links(page):
    links = page.locator("#content h3", has_text="Refine Search").locator("xpath=following-sibling::*[1]//a")
    return [(a.inner_text().strip(), a.get_attribute("href")) for a in links.all()]


@pytest.mark.parametrize("name,path,count", TOP_CATEGORIES, ids=[c[0] for c in TOP_CATEGORIES])
def test_tc05_s2_category_counts_match_products(page, name, path, count):
    open_category(page, path)

    # the left column highlights this category with its count
    shown_name, shown_count = left_menu_count(page)
    assert shown_name == name
    assert shown_count == count

    reachable = set(result_names(page))
    assert total_from_showing(page) == len(result_names(page))

    # every subcategory under "Refine Search": its count matches its own list
    for label, href in _refine_links(page):
        m = re.match(r"(.+?)\s*\((\d+)\)$", label)
        assert m, f"unexpected subcategory label {label!r}"
        page.goto(href)
        sub_names = result_names(page)
        assert len(sub_names) == int(m.group(2)), f"{label}: {len(sub_names)} listed"
        assert total_from_showing(page) == len(sub_names)
        reachable |= set(sub_names)

    # the parent's count = distinct products in the parent and its subcategories
    # (e.g. Desktops 13 = 12 listed + iMac, which is only under Desktops > Mac)
    assert len(reachable) == count, f"{name}: count {count}, reachable {sorted(reachable)}"
    assert_no_server_error(page)


# ---------------- S3: empty and invalid categories ----------------

@pytest.mark.parametrize("path,heading", [("17", "Software"), ("20_26", "PC")], ids=["Software", "Desktops-PC"])
def test_tc05_s3_empty_category(page, path, heading):
    open_category(page, path)
    expect(page.locator("#content h2").first).to_have_text(heading)
    assert result_names(page) == []
    assert showing_text(page) == ""
    page.locator("#content .buttons a.btn-primary", has_text="Continue").click()
    expect(page).to_have_title("Your Store")


@pytest.mark.xfail(
    strict=True,
    reason="D01: empty category shows 'Your shopping cart is empty!' "
    "instead of 'There are no products to list in this category.'",
)
def test_tc05_s3_empty_category_message(page):
    open_category(page, "17")
    assert EMPTY_CATEGORY_MSG in content_messages(page)


@pytest.mark.parametrize("path", ["99999", "abc", "20_99999"], ids=["unknown-id", "text-id", "unknown-subcategory"])
def test_tc05_s3_invalid_category(page, path):
    response = open_category(page, path)
    assert response.status == 404
    expect(page.locator("#content")).to_contain_text("Category not found!")
    assert result_names(page) == []
    assert_no_server_error(page)
    page.locator("#content .buttons a.btn-primary", has_text="Continue").click()
    expect(page).to_have_title("Your Store")
