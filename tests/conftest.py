from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--base-url", action="store", default=os.getenv("BASE_URL", "http://localhost:5173"))
    parser.addoption("--api-url", action="store", default=os.getenv("API_URL", "http://localhost:8000/api"))
    parser.addoption("--headed", action="store_true", default=os.getenv("HEADED", "true").lower() == "true")
    parser.addoption("--slowmo", action="store", default=os.getenv("SLOW_MO", "250"))


def pytest_configure() -> None:
    Path("reports/latest").mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    return str(pytestconfig.getoption("--base-url")).rstrip("/")


@pytest.fixture(scope="session")
def api_url(pytestconfig: pytest.Config) -> str:
    return str(pytestconfig.getoption("--api-url")).rstrip("/")


@pytest.fixture(scope="session")
def browser(pytestconfig: pytest.Config) -> Generator[Browser, None, None]:
    headed = bool(pytestconfig.getoption("--headed"))
    slowmo = int(pytestconfig.getoption("--slowmo"))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headed, slow_mo=slowmo)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser: Browser) -> Generator[Page, None, None]:
    page = browser.new_page(viewport={"width": 1366, "height": 900})
    yield page
    page.close()
