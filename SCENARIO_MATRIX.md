# QA KSink Scenario Matrix

This bot asserts correct behavior against both targets:

- `qa-demo.lab980.com`: expected to pass.
- `qa-bugs.lab980.com`: expected to fail selected regression checks.

## Current scenario groups

### Smoke

- Homepage loads.
- App title renders.
- Dashboard heading renders.
- Build info renders.

### Authentication & roles

- API accepts valid demo login.
- API rejects bad password.
- API `/auth/me` requires a bearer token.
- API `/auth/me` accepts a valid bearer token.
- UI login accepts valid demo user.
- UI login rejects bad password.
- Session persists in the top bar (name + role) and survives navigation.
- Sign-out clears the session chip.
- Admin nav entry is hidden for non-admin roles.
- Product writes require auth (401 anonymous, 403 viewer).
- Product delete requires admin (403 editor).
- Viewer sees no create/edit/delete controls in the grid UI.
- Audit log requires admin (401 anonymous).

### Forms

- Complex form accepts valid payload.
- Currency amount normalizes to expected rounded value.
- Blank name is rejected.
- Invalid email is rejected.
- Terms unchecked is rejected.
- Quantity below minimum is rejected.
- UI form submission shows normalized amount.
- Client-side validation blocks submit and shows per-field errors.

### Products API

- Product search finds seeded record.
- Search is case-insensitive.
- Search supports apostrophes/special characters.
- Status filter returns only matching products.
- Pagination returns distinct pages.
- Invalid sort parameter is rejected.
- Product create/update/delete contract works (role-gated).
- Deleted product 404s on detail fetch.

### Grid UI

- Grid loads seeded products.
- Grid filters by product name.
- Grid filters by category.
- Grid shows zero-count empty result behavior.
- Column sorting works ascending and descending (price).
- Pagination controls page through results at the selected page size.
- Product detail modal opens, traps focus, and closes on Escape.
- Admin can create a product via the modal form and delete it via the
  confirm dialog.

### Orders

- Orders API requires auth; viewer can list but not create.
- Placing an order decrements stock and computes the total.
- Cancelling a pending order restores stock.
- Shipping keeps the stock decrement in place.
- Invalid transitions (from shipped/cancelled) are rejected with 409.
- Insufficient stock and archived products are rejected with 409.
- Status filter returns only matching orders.
- UI: editor places an order, ships it, and the status badge updates.

### Files: export, import, upload

- CSV export has the expected header and honors active filters.
- CSV import requires auth and a .csv file with the exact header.
- Import reports accepted count and per-line rejection errors.
- Upload reports text metadata (size, line count).
- Upload rejects unknown extensions (415), oversize files (413), and
  empty files (400).
- UI upload and import surface success metadata and server rejections.

### Async UI

- Slow request shows completion message.
- In-flight request can be cancelled (AbortController).
- Flaky endpoint is deterministic (fails N times per key, then succeeds).
- UI retry loop recovers after the expected number of attempts.

### Dashboard & audit

- Stats endpoint reports product/order aggregates.
- Dashboard cards populate from live stats.
- Product writes appear in the admin audit log (UI).

### Accessibility / WCAG-oriented checks

These are automated checks mapped to common WCAG A/AA concerns. They are not a complete WCAG conformance audit. They run across all anonymous views (dashboard, login, forms, grid, orders, upload, async).

- Page has a language attribute and non-empty title.
- Each view has a single page-level `h1` and visible view heading.
- Main navigation has an accessible name.
- Visible buttons have accessible names.
- Visible form controls have labels or accessible names.
- Keyboard focus reaches the main navigation.
- Interactive targets are at least 24 by 24 CSS pixels.
- Visible text meets minimum contrast ratio checks.
- Modal dialogs set `aria-modal` and trap keyboard focus.

## Expected bug-lab failures

The `bug-lab` target is intentionally defective. Expected failures include:

- Currency rounding returns the wrong value.
- Slow request reports the wrong completion delay.
- Product delete returns the wrong HTTP status/body.
- UI copy/status regressions.
- Search edge-case regressions.
- Form validation regressions.

See "Bug-seeding candidates" in the site repo README for regression ideas
covering the newer surfaces (roles, orders, export/import, upload, modal,
flaky retry, stats, audit).

## Next scenario groups

- axe-core accessibility scan integration.
- Visual snapshots for dashboard, form, and grid pages.
- Mobile viewport layout checks.
- Console error and network error collection.
