from __future__ import annotations

import pytest


@pytest.mark.regression
def test_form_submission_normalizes_currency(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-forms").click()
    page.get_by_test_id("form-submit").click()
    page.get_by_test_id("form-message").wait_for()
    assert "10.01" in page.get_by_test_id("form-message").inner_text()


@pytest.mark.regression
def test_grid_search_finds_seed_record(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-search").fill("anvil")
    page.wait_for_timeout(500)
    assert page.get_by_text("Anvil").is_visible()


@pytest.mark.regression
def test_async_lab_shows_completion(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-async").click()
    page.get_by_test_id("async-run").click()
    page.get_by_text("Completed after 750ms").wait_for(timeout=3000)
