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
def test_products_support_status_filter(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", params={"status": "archived"}, timeout=5)
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all(item["status"] == "archived" for item in items)


@pytest.mark.api
def test_products_reject_invalid_sort(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", params={"sort": "made_up_column"}, timeout=5)
    assert response.status_code == 422


@pytest.mark.api
def test_products_paginate(api_url: str) -> None:
    response = requests.get(f"{api_url}/products", params={"page": 1, "page_size": 2}, timeout=5)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 2
    assert payload["total"] >= 6
    second = requests.get(f"{api_url}/products", params={"page": 2, "page_size": 2}, timeout=5).json()
    assert [item["id"] for item in second["items"]] != [item["id"] for item in payload["items"]]


@pytest.mark.api
def test_product_write_requires_auth(api_url: str) -> None:
    response = requests.post(f"{api_url}/products", json=product_payload(), timeout=5)
    assert response.status_code == 401


@pytest.mark.api
def test_product_write_forbidden_for_viewer(api_url: str, api_login) -> None:
    response = requests.post(
        f"{api_url}/products", json=product_payload(), headers=api_login("viewer"), timeout=5
    )
    assert response.status_code == 403


@pytest.mark.regression
def test_products_create_update_delete_contract(api_url: str, api_login) -> None:
    editor = api_login("editor")
    admin = api_login("admin")

    create_response = requests.post(f"{api_url}/products", json=product_payload(), headers=editor, timeout=5)
    assert create_response.status_code == 201
    product_id = create_response.json()["item"]["id"]

    update_payload = product_payload() | {"name": "QA Product Updated", "stock": 9}
    update_response = requests.patch(
        f"{api_url}/products/{product_id}", json=update_payload, headers=editor, timeout=5
    )
    assert update_response.status_code == 200
    assert update_response.json()["item"]["stock"] == 9

    editor_delete = requests.delete(f"{api_url}/products/{product_id}", headers=editor, timeout=5)
    assert editor_delete.status_code == 403

    delete_response = requests.delete(f"{api_url}/products/{product_id}", headers=admin, timeout=5)
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    gone = requests.get(f"{api_url}/products/{product_id}", timeout=5)
    assert gone.status_code == 404
