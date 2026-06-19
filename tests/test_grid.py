from __future__ import annotations

import pytest


@pytest.mark.regression
def test_grid_loads_seed_products(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-status").wait_for()
    assert page.get_by_text("Anvil").is_visible()


@pytest.mark.regression
def test_grid_filters_by_product_name(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-search").fill("anvil")
    page.wait_for_timeout(500)
    assert page.get_by_text("Anvil").is_visible()
    assert page.get_by_test_id("grid-status").inner_text() == "Loaded 1 products"


@pytest.mark.regression
def test_grid_filters_by_category(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-search").fill("hardware")
    page.wait_for_timeout(500)
    assert page.get_by_text("Anvil").is_visible()
    assert page.get_by_text("Cobalt Drill").is_visible()


@pytest.mark.regression
def test_grid_shows_empty_result_state_count(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-search").fill("no matching product")
    page.wait_for_timeout(500)
    assert page.get_by_test_id("grid-status").inner_text() == "Loaded 0 products"
