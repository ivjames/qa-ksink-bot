from __future__ import annotations

import requests
import pytest


@pytest.mark.api
def test_health_endpoint(api_url: str) -> None:
    response = requests.get(f"{api_url}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.api
def test_build_info_endpoint(api_url: str) -> None:
    response = requests.get(f"{api_url}/build-info", timeout=5)
    assert response.status_code == 200
    payload = response.json()
    assert payload["app"] == "qa-ksink-site"
    assert "branch" in payload


@pytest.mark.api
def test_products_endpoint_returns_seed_data(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", timeout=5)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert any(item["name"] == "Anvil" for item in payload["items"])
