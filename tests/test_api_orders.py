from __future__ import annotations

import pytest
import requests


def make_product(api_url: str, headers: dict[str, str], **overrides: object) -> dict:
    payload = {
        "name": "Order Target",
        "category": "orders-test",
        "price": 10.00,
        "stock": 10,
        "status": "active",
    } | overrides
    response = requests.post(f"{api_url}/products", json=payload, headers=headers, timeout=5)
    assert response.status_code == 201
    return response.json()["item"]


def delete_product(api_url: str, headers: dict[str, str], product_id: int) -> None:
    requests.delete(f"{api_url}/products/{product_id}", headers=headers, timeout=5)


def get_stock(api_url: str, product_id: int) -> int:
    response = requests.get(f"{api_url}/products/{product_id}", timeout=5)
    assert response.status_code == 200
    return response.json()["item"]["stock"]


@pytest.mark.api
def test_orders_require_auth(api_url: str) -> None:
    response = requests.get(f"{api_url}/orders", timeout=5)
    assert response.status_code == 401


@pytest.mark.api
def test_viewer_can_list_but_not_create_orders(api_url: str, api_login) -> None:
    viewer = api_login("viewer")
    listing = requests.get(f"{api_url}/orders", headers=viewer, timeout=5)
    assert listing.status_code == 200
    assert "items" in listing.json()

    create = requests.post(
        f"{api_url}/orders",
        json={"product_id": 1, "quantity": 1, "customer_name": "Viewer"},
        headers=viewer,
        timeout=5,
    )
    assert create.status_code == 403


@pytest.mark.regression
def test_order_lifecycle_updates_stock(api_url: str, api_login) -> None:
    editor = api_login("editor")
    admin = api_login("admin")
    product = make_product(api_url, editor, stock=10, price=10.00)
    try:
        create = requests.post(
            f"{api_url}/orders",
            json={"product_id": product["id"], "quantity": 4, "customer_name": "Lifecycle"},
            headers=editor,
            timeout=5,
        )
        assert create.status_code == 201
        order = create.json()["item"]
        assert order["status"] == "pending"
        assert order["total"] == 40.00
        assert get_stock(api_url, product["id"]) == 6

        cancel = requests.post(
            f"{api_url}/orders/{order['id']}/status", json={"status": "cancelled"}, headers=editor, timeout=5
        )
        assert cancel.status_code == 200
        assert cancel.json()["item"]["status"] == "cancelled"
        assert get_stock(api_url, product["id"]) == 10

        again = requests.post(
            f"{api_url}/orders/{order['id']}/status", json={"status": "shipped"}, headers=editor, timeout=5
        )
        assert again.status_code == 409
    finally:
        delete_product(api_url, admin, product["id"])


@pytest.mark.regression
def test_order_ship_transition(api_url: str, api_login) -> None:
    editor = api_login("editor")
    admin = api_login("admin")
    product = make_product(api_url, editor, stock=3)
    try:
        order = requests.post(
            f"{api_url}/orders",
            json={"product_id": product["id"], "quantity": 1, "customer_name": "Shipper"},
            headers=editor,
            timeout=5,
        ).json()["item"]
        ship = requests.post(
            f"{api_url}/orders/{order['id']}/status", json={"status": "shipped"}, headers=editor, timeout=5
        )
        assert ship.status_code == 200
        assert ship.json()["item"]["status"] == "shipped"
        # shipping keeps the stock decrement in place
        assert get_stock(api_url, product["id"]) == 2
    finally:
        delete_product(api_url, admin, product["id"])


@pytest.mark.api
def test_order_rejects_insufficient_stock(api_url: str, api_login) -> None:
    editor = api_login("editor")
    admin = api_login("admin")
    product = make_product(api_url, editor, stock=1)
    try:
        response = requests.post(
            f"{api_url}/orders",
            json={"product_id": product["id"], "quantity": 5, "customer_name": "Greedy"},
            headers=editor,
            timeout=5,
        )
        assert response.status_code == 409
        assert get_stock(api_url, product["id"]) == 1
    finally:
        delete_product(api_url, admin, product["id"])


@pytest.mark.api
def test_order_rejects_archived_product(api_url: str, api_login) -> None:
    editor = api_login("editor")
    admin = api_login("admin")
    product = make_product(api_url, editor, status="archived")
    try:
        response = requests.post(
            f"{api_url}/orders",
            json={"product_id": product["id"], "quantity": 1, "customer_name": "Archivist"},
            headers=editor,
            timeout=5,
        )
        assert response.status_code == 409
    finally:
        delete_product(api_url, admin, product["id"])


@pytest.mark.api
def test_order_status_filter(api_url: str, api_login) -> None:
    viewer = api_login("viewer")
    response = requests.get(f"{api_url}/orders", params={"status": "pending"}, headers=viewer, timeout=5)
    assert response.status_code == 200
    assert all(item["status"] == "pending" for item in response.json()["items"])
