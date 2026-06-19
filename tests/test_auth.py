from __future__ import annotations

import pytest
import requests


@pytest.mark.api
def test_api_login_accepts_demo_user(api_url: str) -> None:
    response = requests.post(
        f"{api_url}/auth/login",
        json={"email": "admin@example.com", "password": "demo"},
        timeout=5,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["role"] == "admin"
    assert payload["token"].startswith("demo-token-")


@pytest.mark.api
def test_api_login_rejects_bad_password(api_url: str) -> None:
    response = requests.post(
        f"{api_url}/auth/login",
        json={"email": "admin@example.com", "password": "wrong"},
        timeout=5,
    )
    assert response.status_code == 401


@pytest.mark.api
def test_api_me_requires_token(api_url: str) -> None:
    response = requests.get(f"{api_url}/auth/me", timeout=5)
    assert response.status_code == 401


@pytest.mark.api
def test_api_me_accepts_valid_token(api_url: str) -> None:
    login = requests.post(
        f"{api_url}/auth/login",
        json={"email": "viewer@example.com", "password": "demo"},
        timeout=5,
    )
    assert login.status_code == 200
    token = login.json()["token"]

    response = requests.get(
        f"{api_url}/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "viewer"


@pytest.mark.regression
def test_ui_login_accepts_demo_user(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-login").click()
    page.get_by_test_id("login-email").fill("admin@example.com")
    page.get_by_test_id("login-password").fill("demo")
    page.get_by_test_id("login-submit").click()
    page.get_by_text("Signed in as admin").wait_for(timeout=3000)


@pytest.mark.regression
def test_ui_login_rejects_bad_password(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-login").click()
    page.get_by_test_id("login-email").fill("admin@example.com")
    page.get_by_test_id("login-password").fill("wrong")
    page.get_by_test_id("login-submit").click()
    page.get_by_text("Invalid email or password").wait_for(timeout=3000)
