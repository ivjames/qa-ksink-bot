from __future__ import annotations

import pytest
import requests

VALID_FORM = {
    "full_name": "Test User",
    "email": "test@example.com",
    "quantity": 3,
    "requested_date": "2026-02-28",
    "currency_amount": 10.005,
    "terms": True,
}


@pytest.mark.api
def test_complex_form_accepts_valid_payload(api_url: str) -> None:
    response = requests.post(f"{api_url}/forms/complex", json=VALID_FORM, timeout=5)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["normalized"]["fullName"] == "Test User"


@pytest.mark.regression
def test_complex_form_rounds_currency_correctly(api_url: str) -> None:
    response = requests.post(f"{api_url}/forms/complex", json=VALID_FORM, timeout=5)
    assert response.status_code == 200
    assert response.json()["normalized"]["currencyAmount"] == 10.01


@pytest.mark.api
def test_complex_form_rejects_blank_name(api_url: str) -> None:
    payload = dict(VALID_FORM, full_name="   ")
    response = requests.post(f"{api_url}/forms/complex", json=payload, timeout=5)
    assert response.status_code == 422


@pytest.mark.api
def test_complex_form_rejects_invalid_email(api_url: str) -> None:
    payload = dict(VALID_FORM, email="not-an-email")
    response = requests.post(f"{api_url}/forms/complex", json=payload, timeout=5)
    assert response.status_code == 422


@pytest.mark.api
def test_complex_form_rejects_terms_false(api_url: str) -> None:
    payload = dict(VALID_FORM, terms=False)
    response = requests.post(f"{api_url}/forms/complex", json=payload, timeout=5)
    assert response.status_code == 422


@pytest.mark.api
def test_complex_form_rejects_quantity_below_minimum(api_url: str) -> None:
    payload = dict(VALID_FORM, quantity=0)
    response = requests.post(f"{api_url}/forms/complex", json=payload, timeout=5)
    assert response.status_code == 422


@pytest.mark.regression
def test_ui_form_submission_shows_normalized_amount(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-forms").click()
    page.get_by_test_id("form-submit").click()
    page.get_by_test_id("form-message").wait_for(timeout=3000)
    assert "10.01" in page.get_by_test_id("form-message").inner_text()
