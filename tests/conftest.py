from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--base-url", action="store", default=os.getenv("BASE_URL", "http://localhost:5173"))
    parser.addoption("--api-url", action="store", default=os.getenv("API_URL", "http://localhost:8000/api"))
    parser.addoption("--headed", action="store_true", default=os.getenv("HEADED", "false").lower() == "true")
    parser.addoption("--slowmo", action="store", default=os.getenv("SLOW_MO", "0"))


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


@pytest.fixture(scope="session")
def api_login(api_url: str):
    import requests

    def _login(role: str) -> dict[str, str]:
        response = requests.post(
            f"{api_url}/auth/login",
            json={"email": f"{role}@example.com", "password": "demo"},
            timeout=5,
        )
        response.raise_for_status()
        return {"Authorization": f"Bearer {response.json()['token']}"}

    return _login


@pytest.fixture()
def ui_login(page: Page, base_url: str):
    def _login(role: str) -> None:
        page.goto(base_url)
        page.get_by_test_id("nav-login").click()
        page.get_by_test_id("login-email").fill(f"{role}@example.com")
        page.get_by_test_id("login-password").fill("demo")
        page.get_by_test_id("login-submit").click()
        page.get_by_text(f"Signed in as {role}").wait_for(timeout=3000)

    return _login
