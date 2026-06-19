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

### Authentication

- API accepts valid demo login.
- API rejects bad password.
- API `/auth/me` requires a bearer token.
- API `/auth/me` accepts a valid bearer token.
- UI login accepts valid demo user.
- UI login rejects bad password.

### Forms

- Complex form accepts valid payload.
- Currency amount normalizes to expected rounded value.
- Blank name is rejected.
- Invalid email is rejected.
- Terms unchecked is rejected.
- Quantity below minimum is rejected.
- UI form submission shows normalized amount.

### Products API

- Product search finds seeded record.
- Search is case-insensitive.
- Search supports apostrophes/special characters.
- Invalid sort parameter is rejected.
- Product create/update/delete contract works.

### Grid UI

- Grid loads seeded products.
- Grid filters by product name.
- Grid filters by category.
- Grid shows zero-count empty result behavior.

### Async UI

- Slow request shows completion message.

### Accessibility / WCAG-oriented checks

These are automated checks mapped to common WCAG A/AA concerns. They are not a complete WCAG conformance audit.

- Page has a language attribute and non-empty title.
- Each view has a single page-level `h1` and visible view heading.
- Main navigation has an accessible name.
- Visible buttons have accessible names.
- Visible form controls have labels or accessible names.
- Keyboard focus reaches the main navigation.
- Interactive targets are at least 24 by 24 CSS pixels.
- Visible text meets minimum contrast ratio checks.

## Expected bug-lab failures

The `bug-lab` target is intentionally defective. Expected failures include:

- Currency rounding returns the wrong value.
- Slow request reports the wrong completion delay.
- Product delete returns the wrong HTTP status/body.
- UI copy/status regressions.
- Search edge-case regressions.
- Form validation regressions.

## Next scenario groups

- axe-core accessibility scan integration.
- Role-based navigation and permissions.
- Modal focus trap and keyboard escape behavior.
- File upload validation.
- Export CSV filtered-data checks.
- Visual snapshots for dashboard, form, and grid pages.
- Mobile viewport layout checks.
- Console error and network error collection.
