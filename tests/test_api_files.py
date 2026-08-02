from __future__ import annotations

import pytest
import requests

CSV_HEADER = "id,name,category,price,stock,status"


@pytest.mark.api
def test_export_csv_contract(api_url: str) -> None:
    response = requests.get(f"{api_url}/products/export.csv", params={"q": "anvil"}, timeout=5)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers.get("content-disposition", "")
    lines = response.text.strip().splitlines()
    assert lines[0] == CSV_HEADER
    assert any("Anvil" in line for line in lines[1:])


@pytest.mark.regression
def test_export_csv_respects_filters(api_url: str) -> None:
    response = requests.get(
        f"{api_url}/products/export.csv", params={"q": "definitely-no-such-product"}, timeout=5
    )
    assert response.status_code == 200
    assert response.text.strip() == CSV_HEADER


@pytest.mark.api
def test_import_requires_auth(api_url: str) -> None:
    response = requests.post(
        f"{api_url}/products/import",
        files={"file": ("batch.csv", "name,category,price,stock,status\n", "text/csv")},
        timeout=5,
    )
    assert response.status_code == 401


@pytest.mark.api
def test_import_rejects_non_csv(api_url: str, api_login) -> None:
    response = requests.post(
        f"{api_url}/products/import",
        files={"file": ("batch.txt", "not a csv", "text/plain")},
        headers=api_login("editor"),
        timeout=5,
    )
    assert response.status_code == 415


@pytest.mark.api
def test_import_rejects_wrong_header(api_url: str, api_login) -> None:
    response = requests.post(
        f"{api_url}/products/import",
        files={"file": ("batch.csv", "wrong,header,row\n1,2,3\n", "text/csv")},
        headers=api_login("editor"),
        timeout=5,
    )
    assert response.status_code == 400


@pytest.mark.regression
def test_import_reports_per_line_validation(api_url: str, api_login) -> None:
    editor = api_login("editor")
    admin = api_login("admin")
    body = (
        "name,category,price,stock,status\n"
        "Imported Widget QA,import-test,19.99,5,active\n"
        "Bad Price,import-test,-3,5,active\n"
        ",import-test,1.00,1,active\n"
    )
    response = requests.post(
        f"{api_url}/products/import",
        files={"file": ("batch.csv", body, "text/csv")},
        headers=editor,
        timeout=5,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] == 1
    assert [row["line"] for row in payload["rejected"]] == [3, 4]

    listing = requests.get(f"{api_url}/products", params={"q": "imported widget qa"}, timeout=5).json()
    imported = [item for item in listing["items"] if item["name"] == "Imported Widget QA"]
    assert imported
    for item in imported:
        requests.delete(f"{api_url}/products/{item['id']}", headers=admin, timeout=5)


@pytest.mark.api
def test_upload_reports_text_metadata(api_url: str) -> None:
    response = requests.post(
        f"{api_url}/upload",
        files={"file": ("notes.txt", "alpha\nbravo\ncharlie", "text/plain")},
        timeout=5,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["kind"] == "text"
    assert payload["lines"] == 3
    assert payload["size"] == len("alpha\nbravo\ncharlie")


@pytest.mark.api
def test_upload_rejects_unknown_extension(api_url: str) -> None:
    response = requests.post(
        f"{api_url}/upload",
        files={"file": ("payload.exe", "MZ", "application/octet-stream")},
        timeout=5,
    )
    assert response.status_code == 415


@pytest.mark.api
def test_upload_rejects_oversize_file(api_url: str) -> None:
    response = requests.post(
        f"{api_url}/upload",
        files={"file": ("big.txt", "x" * (64 * 1024 + 1), "text/plain")},
        timeout=5,
    )
    assert response.status_code == 413


@pytest.mark.api
def test_upload_rejects_empty_file(api_url: str) -> None:
    response = requests.post(
        f"{api_url}/upload",
        files={"file": ("empty.txt", "", "text/plain")},
        timeout=5,
    )
    assert response.status_code == 400
