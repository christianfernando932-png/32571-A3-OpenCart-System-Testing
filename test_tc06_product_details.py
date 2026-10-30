"""TC06 / F06 - Product Details

S1  Details page matches the listing and shows the core fields
S2  Special prices, quantity discounts, options, tabs and images
S3  Missing required options and invalid product IDs
"""
import re

import pytest
from playwright.sync_api import expect

from helpers import (
    assert_no_server_error,
    breadcrumb,
    listing_price,
    open_category,
    open_product,
    product_info,
    tab_names,
)


# ---------------- S1: details match the listing ----------------

PRODUCTS_FROM_DESKTOPS = [
    pytest.param(
        "iPhone",
        {
            "Brand": "Apple",
            "Product Code": "product 11",
            "Availability": "In Stock",
            "price": "$123.20",
            "ex_tax": "$101.00",
        },
        ["Description", "Reviews (0)"],
        6,
        id="iPhone-in-stock",
    ),
    pytest.param(
        "MacBook",
        {
            "Brand": "Apple",
            "Product Code": "Product 16",
            "Reward Points": "600",
            "Availability": "Out Of Stock",
            "price": "$602.00",
            "ex_tax": "$500.00",
        },
        ["Description", "Specification", "Reviews (0)"],
        5,
        id="MacBook-out-of-stock",
    ),
]


@pytest.mark.parametrize("name,expected,tabs,thumbs", PRODUCTS_FROM_DESKTOPS)
def test_tc06_s1_details_match_listing(page, name, expected, tabs, thumbs):
    open_category(page, "20")
    tile_price = listing_price(page, name)  # e.g. "$123.20 Ex Tax: $101.00"

    page.locator(".product-thumb h4 a", has_text=re.compile(rf"^{re.escape(name)}$")).click()
    expect(page.locator("#content h1")).to_have_text(name)
    expect(page).to_have_title(name)
    assert breadcrumb(page) == ["", "Desktops", name]

    info = product_info(page)
    for key, value in expected.items():
        assert info.get(key) == value, f"{key}: expected {value!r}, got {info.get(key)!r}"

    # same price and ex-tax price as on the category tile
    assert tile_price == f"{info['price']} Ex Tax: {info['ex_tax']}"

    assert tab_names(page) == tabs
    assert page.locator("#content .thumbnails li").count() == thumbs
    expect(page.locator("#input-quantity")).to_have_value("1")
    expect(page.locator("#button-cart")).to_be_visible()


# ---------------- S2: specials, discounts, options, tabs, images ----------------

def test_tc06_s2_special_price_discounts_options_and_tabs(page):
    open_product(page, 42)  # Apple Cinema 30"
    expect(page.locator("#content h1")).to_have_text('Apple Cinema 30"')

    info = product_info(page)
    # 1. special price: old price struck through, new price shown
    assert info["old_price"] == "$122.00"
    assert info["price"] == "$110.00"
    assert info["ex_tax"] == "$90.00"
    # 2. quantity discounts, cheapest at the highest quantity
    assert info["discounts"] == ["10 or more $107.60", "20 or more $94.40", "30 or more $81.20"]
    assert info["Reward Points"] == "100"
    expect(page.locator("#content .col-sm-4")).to_contain_text("Price in reward points: 400")
    # stock level is live, so only check it is a number
    assert re.fullmatch(r"\d+", info["Availability"]), info["Availability"]

    # 3. all nine option types are offered
    labels = [t.strip() for t in page.locator("#product .form-group label.control-label").all_inner_texts()]
    assert labels[:-1] == [
        "Radio", "Checkbox", "Text", "Select", "Textarea",
        "File", "Date", "Time", "Date & Time",
    ]
    assert labels[-1] == "Qty"

    # 4. tabs switch content
    page.locator("#content .nav-tabs a", has_text="Specification").click()
    expect(page.locator("#tab-specification")).to_be_visible()
    expect(page.locator("#tab-specification table")).to_be_visible()
    page.locator("#content .nav-tabs a", has_text="Reviews (0)").click()
    expect(page.locator("#tab-review")).to_be_visible()
    expect(page.locator("#input-name")).to_be_visible()
    page.locator("#content .nav-tabs a", has_text="Description").click()
    expect(page.locator("#tab-description")).to_be_visible()

    # 5. main image opens in a larger popup and closes again
    page.locator("#content .thumbnails a.thumbnail").first.click()
    expect(page.locator(".mfp-img")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator(".mfp-img")).to_have_count(0)

    # 6. a second product with a special price and one option
    open_product(page, 30)  # Canon EOS 5D
    info = product_info(page)
    assert (info["old_price"], info["price"], info["ex_tax"]) == ("$122.00", "$98.00", "$80.00")
    labels = [t.strip() for t in page.locator("#product .form-group label.control-label").all_inner_texts()]
    assert labels == ["Select", "Qty"]


# ---------------- S3: missing options and invalid IDs ----------------


def test_tc06_s3_required_options_block_add_to_cart(page):
    open_product(page, 42)  # Apple Cinema 30"

    errors = page.locator("#product .text-danger")

    # Step 1: Click Add to Cart with default values
    page.locator("#button-cart").click()
    expect(errors.first).to_be_visible()

    actual = sorted(t.strip() for t in errors.all_inner_texts())
    expected_five = sorted([
        "Radio required!",
        "Checkbox required!",
        "Select required!",
        "Textarea required!",
        "File required!",
    ])
    assert actual == expected_five
    expect(page.locator("#cart-total")).to_have_text(
        "0 item(s) - $0.00"
    )

    # Step 2: Clear the four pre-filled required fields
    for field in ["Text", "Date", "Time", "Date & Time"]:
        label = page.locator(
            "#product label.control-label"
        ).filter(has_text=re.compile(rf"^{re.escape(field)}$"))

        field_input = label.locator("xpath=..").locator("input").first
        field_input.fill("")
        expect(field_input).to_have_value("")

    # Step 3: Submit again with all nine options empty
    page.locator("#button-cart").click()

    expect(errors).to_have_count(9)
    actual = sorted(t.strip() for t in errors.all_inner_texts())
    expected_nine = sorted([
        "Radio required!",
        "Checkbox required!",
        "Text required!",
        "Select required!",
        "Textarea required!",
        "File required!",
        "Date required!",
        "Time required!",
        "Date & Time required!",
    ])
    assert actual == expected_nine

    # Step 4: Verify the shopping cart remains empty
    expect(page.locator("#cart-total")).to_have_text(
        "0 item(s) - $0.00"
    )



@pytest.mark.parametrize("product_id", ["99999", "-1", "abc"], ids=["unknown-id", "negative-id", "text-id"])
def test_tc06_s3_invalid_product_id(page, product_id):
    response = open_product(page, product_id)
    assert response.status == 404
    expect(page.locator("#content")).to_contain_text("Product not found!")
    expect(page.locator("#button-cart")).to_have_count(0)
    assert_no_server_error(page)
    page.locator("#content .buttons a.btn-primary", has_text="Continue").click()
    expect(page).to_have_title("Your Store")
