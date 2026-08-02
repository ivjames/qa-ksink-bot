from __future__ import annotations

import pytest


@pytest.mark.regression
def test_session_persists_and_role_gates_nav(page, base_url: str, ui_login) -> None:
    ui_login("admin")
    assert "(admin)" in page.get_by_test_id("session-user").inner_text()
    page.get_by_test_id("nav-admin").click()
    page.get_by_role("heading", name="Admin Audit").wait_for()
    page.get_by_test_id("audit-status").wait_for()

    page.get_by_test_id("session-logout").click()
    assert page.get_by_test_id("session-user").inner_text() == "Not signed in"
    assert page.get_by_test_id("nav-admin").count() == 0


@pytest.mark.regression
def test_admin_nav_hidden_for_viewer(page, base_url: str, ui_login) -> None:
    ui_login("viewer")
    assert page.get_by_test_id("nav-admin").count() == 0
    page.get_by_test_id("nav-orders").click()
    page.get_by_role("heading", name="Orders Desk").wait_for()
    page.get_by_test_id("orders-readonly-note").wait_for()


@pytest.mark.regression
def test_viewer_sees_no_write_controls_in_grid(page, base_url: str, ui_login) -> None:
    ui_login("viewer")
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-status").wait_for()
    page.get_by_test_id("row-view").first.wait_for()
    assert page.get_by_test_id("product-new").count() == 0
    assert page.get_by_test_id("row-edit").count() == 0
    assert page.get_by_test_id("row-delete").count() == 0


@pytest.mark.regression
def test_product_detail_modal_focus_trap_and_escape(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("row-view").first.click()
    modal = page.get_by_test_id("product-detail-modal")
    modal.wait_for()
    assert modal.get_attribute("aria-modal") == "true"

    for _ in range(8):
        page.keyboard.press("Tab")
        inside = page.evaluate(
            "() => document.querySelector('[role=dialog]').contains(document.activeElement)"
        )
        assert inside, "focus escaped the modal dialog"

    page.keyboard.press("Escape")
    assert page.get_by_test_id("product-detail-modal").count() == 0


@pytest.mark.regression
def test_admin_creates_and_deletes_product_via_ui(page, base_url: str, ui_login) -> None:
    ui_login("admin")
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("product-new").click()
    page.get_by_test_id("product-name").fill("UI Made Widget")
    page.get_by_test_id("product-category").fill("ui-test")
    page.get_by_test_id("product-price").fill("5.55")
    page.get_by_test_id("product-stock").fill("3")
    page.get_by_test_id("product-save").click()
    page.get_by_test_id("product-form-modal").wait_for(state="detached")

    page.get_by_test_id("grid-search").fill("UI Made Widget")
    page.wait_for_timeout(500)
    grid_body = page.locator('[data-testid="grid-body"]')
    assert grid_body.get_by_text("UI Made Widget").first.is_visible()

    # delete every matching row (self-heals leftovers from earlier runs)
    while page.get_by_test_id("row-delete").count() > 0:
        page.get_by_test_id("row-delete").first.click()
        page.get_by_test_id("confirm-modal").wait_for()
        page.get_by_test_id("confirm-accept").click()
        page.wait_for_timeout(500)
    assert page.get_by_test_id("grid-status").inner_text() == "Loaded 0 products"


@pytest.mark.regression
def test_grid_sorts_by_price_both_directions(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-status").wait_for()

    def first_two_prices() -> list[float]:
        rows = page.get_by_test_id("grid-row")
        return [
            float(rows.nth(index).locator("td").nth(2).inner_text()) for index in range(2)
        ]

    page.get_by_test_id("grid-sort-price").click()
    page.wait_for_timeout(400)
    ascending = first_two_prices()
    assert ascending[0] <= ascending[1]

    page.get_by_test_id("grid-sort-price").click()
    page.wait_for_timeout(400)
    descending = first_two_prices()
    assert descending[0] >= descending[1]


@pytest.mark.regression
def test_grid_pagination_controls(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-status").wait_for()
    page.get_by_test_id("grid-page-size").select_option("5")
    page.wait_for_timeout(400)
    assert page.get_by_test_id("grid-row").count() == 5
    assert "Page 1" in page.get_by_test_id("grid-page-label").inner_text()

    page.get_by_test_id("grid-next").click()
    page.wait_for_timeout(400)
    assert "Page 2" in page.get_by_test_id("grid-page-label").inner_text()
    assert page.get_by_test_id("grid-row").count() >= 1


@pytest.mark.regression
def test_orders_ui_place_and_ship(page, base_url: str, ui_login) -> None:
    ui_login("editor")
    page.get_by_test_id("nav-orders").click()
    page.get_by_role("heading", name="Orders Desk").wait_for()
    page.locator('[data-testid="order-product"] option').first.wait_for(state="attached")

    page.get_by_test_id("order-quantity").fill("1")
    page.get_by_test_id("order-customer").fill("UI Test Customer")
    page.get_by_test_id("order-submit").click()
    page.wait_for_timeout(500)

    first_row = page.get_by_test_id("order-row").first
    assert "UI Test Customer" in first_row.inner_text()
    assert first_row.get_by_test_id("order-status-badge").inner_text() == "pending"

    first_row.get_by_test_id("order-ship").click()
    page.wait_for_timeout(500)
    first_row = page.get_by_test_id("order-row").first
    assert first_row.get_by_test_id("order-status-badge").inner_text() == "shipped"


@pytest.mark.regression
def test_form_client_validation_blocks_submit(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-forms").click()
    page.get_by_test_id("form-full-name").fill("")
    page.get_by_test_id("form-terms").uncheck()
    page.get_by_test_id("form-submit").click()
    assert page.get_by_test_id("error-full-name").inner_text() == "Full name is required"
    assert page.get_by_test_id("error-terms").inner_text() == "You must accept the terms"
    assert page.get_by_test_id("form-message").inner_text() == "Fix the highlighted fields"


@pytest.mark.regression
def test_upload_ui_reports_metadata(page, base_url: str, tmp_path) -> None:
    sample = tmp_path / "notes.txt"
    sample.write_text("alpha\nbravo\n")
    page.goto(base_url)
    page.get_by_test_id("nav-upload").click()
    page.get_by_test_id("upload-input").set_input_files(str(sample))
    page.get_by_test_id("upload-submit").click()
    page.get_by_text("Uploaded notes.txt").wait_for(timeout=3000)
    assert "2 lines" in page.get_by_test_id("upload-result").inner_text()


@pytest.mark.regression
def test_upload_ui_surfaces_server_rejection(page, base_url: str, tmp_path) -> None:
    sample = tmp_path / "data.json"
    sample.write_text("{}")
    page.goto(base_url)
    page.get_by_test_id("nav-upload").click()
    page.get_by_test_id("upload-input").set_input_files(str(sample))
    page.get_by_test_id("upload-submit").click()
    page.get_by_text("Rejected:").wait_for(timeout=3000)


@pytest.mark.regression
def test_import_ui_reports_rejected_rows(page, base_url: str, ui_login, tmp_path) -> None:
    sample = tmp_path / "batch.csv"
    sample.write_text(
        "name,category,price,stock,status\n"
        "UI Import Widget,import-ui,9.99,2,active\n"
        "Bad Row,import-ui,-1,2,active\n"
    )
    ui_login("editor")
    page.get_by_test_id("nav-upload").click()
    page.get_by_test_id("import-input").set_input_files(str(sample))
    page.get_by_test_id("import-submit").click()
    page.get_by_text("Imported 1 products, rejected 1 rows").wait_for(timeout=3000)
    assert page.get_by_test_id("import-rejected-row").count() == 1


@pytest.mark.regression
def test_async_request_can_be_cancelled(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-async").click()
    page.get_by_test_id("async-delay").fill("3000")
    page.get_by_test_id("async-run").click()
    page.get_by_text("Loading").wait_for()
    page.get_by_test_id("async-cancel").click()
    page.get_by_text("Cancelled").wait_for(timeout=3000)


@pytest.mark.regression
def test_flaky_ui_recovers_with_retry(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_test_id("nav-async").click()
    page.get_by_test_id("flaky-times").fill("2")
    page.get_by_test_id("flaky-run").click()
    page.get_by_text("Recovered after 3 attempts").wait_for(timeout=10000)


@pytest.mark.regression
def test_dashboard_stats_populate(page, base_url: str) -> None:
    page.goto(base_url)
    page.get_by_text("Metrics loaded").wait_for(timeout=3000)
    total = page.get_by_test_id("stat-products-total").inner_text()
    assert total.isdigit() and int(total) >= 1
    assert page.get_by_test_id("stat-inventory-value").inner_text().startswith("$")


@pytest.mark.regression
def test_admin_audit_records_product_write(page, base_url: str, ui_login) -> None:
    ui_login("admin")
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("product-new").click()
    page.get_by_test_id("product-name").fill("Audit Trail Widget")
    page.get_by_test_id("product-category").fill("audit-test")
    page.get_by_test_id("product-price").fill("1.23")
    page.get_by_test_id("product-stock").fill("1")
    page.get_by_test_id("product-save").click()
    page.get_by_test_id("product-form-modal").wait_for(state="detached")

    page.get_by_test_id("nav-admin").click()
    page.get_by_text("audit entries").wait_for(timeout=3000)
    assert "Audit Trail Widget" in page.get_by_test_id("audit-body").inner_text()

    # clean up the product we created
    page.get_by_test_id("nav-grid").click()
    page.get_by_test_id("grid-search").fill("Audit Trail Widget")
    page.wait_for_timeout(500)
    page.get_by_test_id("row-delete").first.click()
    page.get_by_test_id("confirm-accept").click()
    page.wait_for_timeout(500)
