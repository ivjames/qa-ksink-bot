from __future__ import annotations

import pytest
import requests


def product_payload() -> dict[str, object]:
    return {
        "name": "QA Product",
        "category": "contract",
        "price": 12.34,
        "stock": 5,
        "status": "active",
    }


@pytest.mark.api
def test_products_support_search(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", params={"q": "anvil"}, timeout=5)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert any(item["name"] == "Anvil" for item in payload["items"])


@pytest.mark.api
def test_products_support_case_insensitive_search(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", params={"q": "ANVIL"}, timeout=5)
    assert response.status_code == 200
    assert any(item["name"] == "Anvil" for item in response.json()["items"])


@pytest.mark.api
def test_products_support_special_character_search(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", params={"q": "foo's"}, timeout=5)
    assert response.status_code == 200
    assert any(item["name"] == "Foo's Widget" for item in response.json()["items"])


@pytest.mark.api
def test_products_reject_invalid_sort(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", params={"sort": "made_up_column"}, timeout=5)
    assert response.status_code == 422


@pytest.mark.regression
def test_products_create_update_delete_contract(api_url: str) -> None:
    create_response = requests.post(f"{api_url}/products", json=product_payload(), timeout=5)
    assert create_response.status_code == 201
    product_id = create_response.json()["item"]["id"]

    update_payload = product_payload() | {"name": "QA Product Updated", "stock": 9}
    update_response = requests.patch(f"{api_url}/products/{product_id}", json=update_payload, timeout=5)
    assert update_response.status_code == 200
    assert update_response.json()["item"]["stock"] == 9

    delete_response = requests.delete(f"{api_url}/products/{product_id}", timeout=5)
    assert delete_response.status_code == 204
    assert delete_response.text == ""
