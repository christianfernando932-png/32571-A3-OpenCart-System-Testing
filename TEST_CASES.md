# Test Cases TC04–TC06

**System under test:** OpenCart demo store, https://opencart.abstracta.us/
**Tools:** Python, pytest, Playwright (Chromium)
**Expected values checked against the live site:** 31 Oct 2026

All three functions work for guests (no login), so they can run in parallel with account-related tests.

---

## TC04 – F04 Product Search

| Field | Detail |
|---|---|
| Test Case ID | TC04 |
| Function | F04 Product Search |
| Description | Check that the store search finds the right products by keyword, honours the advanced criteria, and handles no-match and malicious input safely. |
| Preconditions | Store reachable; browser on the home page; no login needed. |
| Automated in | `tests/test_tc04_product_search.py` |

### Scenario 1 – Keyword search from the header

| Step | Action / Input | Expected result |
|---|---|---|
| 1 | Type `mac` in the header search box, click the search button | Page "Search - mac" lists exactly iMac, MacBook, MacBook Air, MacBook Pro; "Showing 1 to 4 of 4 (1 Pages)"; `mac` is kept in the Search Criteria box |
| 2 | Type `MAC`, press Enter | Same 4 products (search is not case-sensitive; Enter works like the button) |
| 3 | Type `Mac Bo` | MacBook, MacBook Air, MacBook Pro only |
| 4 | Type `iphone` | iPhone only |
| 5 | Click the iPhone result | iPhone product page opens |

### Scenario 2 – Advanced search criteria

| Step | Action / Input | Expected result |
|---|---|---|
| 1 | Search `stunning` (names only) | No products (the word is only in descriptions) |
| 2 | Tick "Search in product descriptions", search again | HP LP3065 and iMac; box stays ticked |
| 3 | Untick descriptions; keyword `mac`, category Desktops | MacBook, MacBook Air |
| 4 | Tick "Search in subcategories" | iMac, MacBook, MacBook Air (iMac is under Desktops > Mac) |
| 5 | Change category to Laptops & Notebooks | MacBook, MacBook Air, MacBook Pro; no error text |

### Scenario 3 – No-match and invalid input

| Step | Input (header search) | Expected result |
|---|---|---|
| 1 | `zzqxnotreal` | No products, no "Showing" line, message "There is no product that matches the search criteria." |
| 2 | `' OR 1=1--` | No products; no SQL/PHP error text |
| 3 | `<script>alert(1)</script>` | No products; no JavaScript alert; keyword shown as plain text in the heading |
| 4 | 300 × `a` | No products; no error |
| 5 | empty | No products; no error |

---

## TC05 – F05 Category Navigation

| Field | Detail |
|---|---|
| Test Case ID | TC05 |
| Function | F05 Category Navigation |
| Description | Check that shoppers can reach every category and subcategory from the menu, breadcrumbs and left column, that the product counts are accurate, and that empty and invalid categories are handled. |
| Preconditions | Store reachable; no login needed. |
| Automated in | `tests/test_tc05_category_navigation.py` |

### Scenario 1 – Top menu and breadcrumbs

| Step | Action | Expected result |
|---|---|---|
| 1 | Open home page | Menu shows Desktops, Laptops & Notebooks, Components, Tablets, Software, Phones & PDAs, Cameras, MP3 Players |
| 2 | Hover Desktops, click "Show All Desktops" | Desktops page, breadcrumb Home > Desktops, 12 products, "Showing 1 to 12 of 12 (1 Pages)" |
| 3 | Hover Desktops, click "Mac (1)" | Mac page, breadcrumb Home > Desktops > Mac, only iMac |
| 4 | Click "Desktops" in the breadcrumb | Back on Desktops |
| 5 | Click Tablets in the menu | Tablets page with Samsung Galaxy Tab 10.1 |
| 6 | Click the home icon in the breadcrumb | Home page |

### Scenario 2 – Counts match reachable products (run for all 8 top categories)

| Category | Count shown | Expected result |
|---|---|---|
| Desktops | 13 | 12 listed + iMac from Mac = 13; PC (0) and Mac (1) each list that many |
| Laptops & Notebooks | 5 | 5 listed; Macs (0), Windows (0) |
| Components | 2 | 0 listed directly + Monitors (2) = 2 |
| Tablets | 1 | 1 listed |
| Software | 0 | 0 listed |
| Phones & PDAs | 3 | 3 listed |
| Cameras | 2 | 2 listed |
| MP3 Players | 4 | 4 listed; each "test N (0)" subcategory empty |

For each: the left column highlights the category with its count; every Refine Search subcategory lists exactly its own count; the parent's count equals the distinct products in it and its subcategories.

### Scenario 3 – Empty and invalid categories

| Step | Input | Expected result |
|---|---|---|
| 1 | Software (path 17), Desktops > PC (path 20_26) | Heading shown, no products, message "There are no products to list in this category.", Continue returns home |
| 2 | path `99999`, `abc`, `20_99999` | HTTP 404, "Category not found!", no products, no error text, Continue returns home |

---

## TC06 – F06 Product Details

| Field | Detail |
|---|---|
| Test Case ID | TC06 |
| Function | F06 Product Details |
| Description | Check that a product page shows correct, consistent information (matching the listing), handles special prices, discounts, options, tabs and images, and rejects missing options and invalid products. |
| Preconditions | Store reachable; no login needed; empty cart. |
| Automated in | `tests/test_tc06_product_details.py` |

### Scenario 1 – Details match the listing (iPhone, MacBook from Desktops)

| Field | iPhone | MacBook |
|---|---|---|
| Breadcrumb | Home > Desktops > iPhone | Home > Desktops > MacBook |
| Brand | Apple | Apple |
| Product Code | product 11 | Product 16 |
| Reward Points | – | 600 |
| Availability | In Stock | Out Of Stock |
| Price / Ex Tax | $123.20 / $101.00 (same as tile) | $602.00 / $500.00 (same as tile) |
| Tabs | Description, Reviews (0) | Description, Specification, Reviews (0) |
| Images | 6 | 5 |
| Qty default / Add to Cart | 1 / shown | 1 / shown |

### Scenario 2 – Special price, discounts, options, tabs, images

| Step | Action | Expected result |
|---|---|---|
| 1 | Open Apple Cinema 30" | Old price $122.00 struck through, special $110.00, Ex Tax $90.00 |
| 2 | Read discounts | 10 or more $107.60; 20 or more $94.40; 30 or more $81.20; Reward Points 100; Price in reward points 400; stock shown as a number |
| 3 | Read options | Radio, Checkbox, Text, Select, Textarea, File, Date, Time, Date & Time, then Qty |
| 4 | Click Specification, Reviews, Description tabs | Each tab's content shows (spec table; review form) |
| 5 | Click main image, press Escape | Large image popup opens, then closes |
| 6 | Open Canon EOS 5D | $122.00 → $98.00, Ex Tax $80.00; one Select option |

### Scenario 3 – Missing options and invalid IDs

| Step | Action / Input | Expected result |
|---|---|---|
| 1 | Open Apple Cinema 30" and click Add to Cart without changing the default values | Five validation errors: Radio, Checkbox, Select, Textarea and File; cart remains empty |
| 2 | Clear the pre-filled Text, Date, Time and Date & Time fields, then click Add to Cart again | Nine validation errors appear, one for each required option; cart remains empty |
| 3 | Enter invalid product IDs `99999`, `-1` and `abc` | HTTP 404, "Product not found!", no Add to Cart button, no server error; Continue returns home |

---

## Defects found

| ID | Where | Expected | Actual | Test |
|---|---|---|---|---|
| D01 | Search with no results (TC04 S3) and empty category (TC05 S3) | "There is no product that matches the search criteria." / "There are no products to list in this category." | Both show "Your shopping cart is empty!", which is the cart's message and misleads the shopper | `test_tc04_s3_no_result_message`, `test_tc05_s3_empty_category_message` (marked `xfail`, strict) |

Expected wording is OpenCart's default English text for these pages.

---

## How the 30 pytest rows map to the 9 scenarios

| Test case | Scenario | pytest rows |
|---|---|---|
| TC04 | S1 Keyword search | 1 |
| TC04 | S2 Advanced criteria | 1 |
| TC04 | S3 No-match / invalid | 5 inputs + 1 message check (D01) = 6 |
| TC05 | S1 Menu and breadcrumbs | 1 |
| TC05 | S2 Counts | 8 (one per top category) |
| TC05 | S3 Empty / invalid | 2 empty + 1 message check (D01) + 3 invalid = 6 |
| TC06 | S1 Details match listing | 2 |
| TC06 | S2 Specials, options, tabs, images | 1 |
| TC06 | S3 Missing options / invalid IDs | 1 + 3 = 4 |
| | **9 scenarios** | **30** |

Expected outcome of a full run: **28 passed, 2 xfailed** (the two D01 checks). If D01 is ever fixed, those two turn into failures ("XPASS strict") so you know to update the report.
