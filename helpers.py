"""Shared helpers for TC04-TC06 on https://opencart.abstracta.us/

Selectors and expected values were checked against the live site on 31 Oct 2026.
"""
import re

from playwright.sync_api import Page, expect

BASE = "https://opencart.abstracta.us/"
HOME = BASE + "index.php?route=common/home"

# Text that would only appear if the server leaked an error to the page.
SERVER_ERROR_PATTERNS = [
    "SQL syntax",
    "mysqli",
    "Fatal error",
    "Warning:",
    "Notice:",
    "Stack trace",
]

# OpenCart's own wording for these pages (default English language file).
NO_SEARCH_RESULTS_MSG = "There is no product that matches the search criteria."
EMPTY_CATEGORY_MSG = "There are no products to list in this category."


# ---------- navigation ----------

def open_home(page: Page) -> None:
    page.goto(HOME)
    expect(page).to_have_title("Your Store")


def open_search(page: Page, query: str = "") -> None:
    page.goto(BASE + "index.php?route=product/search&search=" + query)


def open_category(page: Page, path: str):
    return page.goto(BASE + f"index.php?route=product/category&path={path}")


def open_product(page: Page, product_id):
    return page.goto(BASE + f"index.php?route=product/product&product_id={product_id}")


def header_search(page: Page, text: str, press_enter: bool = False) -> None:
    """Type into the header search box and submit with the button or Enter."""
    box = page.locator("#search input[name='search']")
    box.fill(text)
    with page.expect_navigation():
        if press_enter:
            box.press("Enter")
        else:
            page.locator("#search button").click()


def top_menu_item(page: Page, name: str):
    return page.locator("#menu .navbar-nav > li").filter(
        has=page.locator(":scope > a", has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
    )


# ---------- reading pages ----------

def result_names(page: Page) -> list[str]:
    return [t.strip() for t in page.locator(".product-thumb h4 a").all_inner_texts()]


def showing_text(page: Page) -> str:
    loc = page.locator("#content .text-right", has_text="Showing")
    return loc.inner_text().strip() if loc.count() else ""


def total_from_showing(page: Page) -> int:
    """'Showing 1 to 12 of 12 (1 Pages)' -> 12; no products -> 0."""
    m = re.search(r"of (\d+)", showing_text(page))
    return int(m.group(1)) if m else 0


def content_messages(page: Page) -> list[str]:
    """Paragraphs that sit directly in #content (where OpenCart puts its notices)."""
    return [t.strip() for t in page.locator("#content > p").all_inner_texts()]


def left_menu_count(page: Page) -> tuple[str, int]:
    """Active entry in the left category list, e.g. ('Desktops', 13)."""
    text = page.locator(".list-group a.active").first.inner_text().strip()
    m = re.match(r"(.+?)\s*\((\d+)\)$", text)
    assert m, f"unexpected left-menu text: {text!r}"
    return m.group(1), int(m.group(2))


def breadcrumb(page: Page) -> list[str]:
    """Breadcrumb texts; the first item is the home icon (empty text)."""
    return [t.strip() for t in page.locator(".breadcrumb li").all_inner_texts()]


def listing_price(page: Page, name: str) -> str:
    tile = page.locator(".product-thumb").filter(
        has=page.locator("h4 a", has_text=re.compile(rf"^{re.escape(name)}$"))
    )
    return " ".join(tile.locator(".price").inner_text().split())


def product_info(page: Page) -> dict:
    """Read the right-hand column of a product page into a dict.

    Labelled rows ('Product Code: Product 16') become keys; the brand row reads
    'Brands Apple'. Prices are read separately.
    """
    info = {}
    col = page.locator("#content .col-sm-4").first
    for li in col.locator("ul.list-unstyled").first.locator("li").all_inner_texts():
        li = " ".join(li.split())
        if li.startswith("Brands "):
            info["Brand"] = li[len("Brands "):]
        elif ":" in li:
            k, v = li.split(":", 1)
            info[k.strip()] = v.strip()
    info["price"] = col.locator("ul.list-unstyled h2").first.inner_text().strip()
    old = col.locator("ul.list-unstyled li span[style*='line-through']")
    info["old_price"] = old.first.inner_text().strip() if old.count() else None
    ex = col.locator("ul.list-unstyled li", has_text="Ex Tax:")
    info["ex_tax"] = ex.first.inner_text().split(":", 1)[1].strip() if ex.count() else None
    info["discounts"] = [
        " ".join(t.split())
        for t in col.locator("ul.list-unstyled li", has_text="or more").all_inner_texts()
    ]
    return info


def tab_names(page: Page) -> list[str]:
    return [t.strip() for t in page.locator("#content .nav-tabs a").all_inner_texts()]


# ---------- checks ----------

def assert_no_server_error(page: Page) -> None:
    body = page.locator("body").inner_text()
    for pattern in SERVER_ERROR_PATTERNS:
        assert pattern not in body, f"server error text {pattern!r} shown on page"


def assert_names_contain(names: list[str], keyword: str) -> None:
    for n in names:
        assert keyword.lower() in n.lower(), f"{n!r} does not contain {keyword!r}"
