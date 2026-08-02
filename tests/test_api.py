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


@pytest.mark.api
def test_stats_endpoint_shape(api_url: str) -> None:
    response = requests.get(f"{api_url}/stats", timeout=5)
    assert response.status_code == 200
    payload = response.json()
    assert payload["products"]["total"] >= 1
    assert payload["products"]["totalStock"] >= 0
    assert payload["products"]["inventoryValue"] >= 0
    assert set(payload["orders"]) >= {"total", "pending", "shipped", "cancelled", "openValue"}


@pytest.mark.regression
def test_flaky_endpoint_is_deterministic(api_url: str) -> None:
    import uuid

    key = f"bot-{uuid.uuid4().hex[:8]}"
    codes = [
        requests.get(f"{api_url}/flaky", params={"key": key, "fail_times": 2}, timeout=5).status_code
        for _ in range(3)
    ]
    assert codes == [503, 503, 200]
    success = requests.get(f"{api_url}/flaky", params={"key": key, "fail_times": 0}, timeout=5)
    assert success.status_code == 200
    assert success.json()["attempts"] == 1


@pytest.mark.api
def test_forced_error_endpoint(api_url: str) -> None:
    response = requests.get(f"{api_url}/error", params={"code": 418}, timeout=5)
    assert response.status_code == 418


@pytest.mark.api
def test_audit_requires_admin(api_url: str) -> None:
    anonymous = requests.get(f"{api_url}/audit", timeout=5)
    assert anonymous.status_code == 401
