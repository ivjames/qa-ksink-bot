from __future__ import annotations

import pytest


@pytest.mark.smoke
def test_homepage_loads(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("app-title").wait_for()
    assert page.get_by_test_id("app-title").inner_text() == "QA KSink Site"
    assert "Dashboard" in page.get_by_test_id("dashboard-heading").inner_text()


@pytest.mark.smoke
def test_build_info_renders(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("build-info").wait_for()
    assert "loading" not in page.get_by_test_id("build-info").inner_text().lower()
