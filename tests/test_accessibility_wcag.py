from __future__ import annotations

import pytest

PAGES = [
    ("dashboard", "nav-dashboard", "Dashboard"),
    ("login", "nav-login", "Authentication Lab"),
    ("forms", "nav-forms", "Form Gauntlet"),
    ("grid", "nav-grid", "Data Grid Lab"),
    ("async", "nav-async", "Async Lab"),
]


def open_page(page, base_url: str, nav_test_id: str) -> None:
    page.goto(base_url)
    page.get_by_test_id(nav_test_id).click()


@pytest.mark.accessibility
@pytest.mark.regression
def test_page_has_language_and_title(page, base_url: str) -> None:
    page.goto(base_url)
    assert page.locator("html").get_attribute("lang") == "en"
    assert page.title().strip() == "QA KSink Site"


@pytest.mark.accessibility
@pytest.mark.regression
@pytest.mark.parametrize(("page_name", "nav_test_id", "heading"), PAGES)
def test_each_view_has_programmatic_heading(page, base_url: str, page_name: str, nav_test_id: str, heading: str) -> None:
    open_page(page, base_url, nav_test_id)
    assert page.locator("h1").count() == 1
    assert page.get_by_role("heading", name=heading).is_visible()


@pytest.mark.accessibility
@pytest.mark.regression
def test_navigation_has_accessible_name(page, base_url: str) -> None:
    page.goto(base_url)
    nav = page.get_by_role("navigation", name="Main navigation")
    assert nav.is_visible()


@pytest.mark.accessibility
@pytest.mark.regression
@pytest.mark.parametrize(("page_name", "nav_test_id", "heading"), PAGES)
def test_buttons_have_accessible_names(page, base_url: str, page_name: str, nav_test_id: str, heading: str) -> None:
    open_page(page, base_url, nav_test_id)
    unnamed = page.evaluate(
        """
        () => Array.from(document.querySelectorAll('button'))
          .filter(button => button.offsetParent !== null)
          .filter(button => !button.innerText.trim() && !button.getAttribute('aria-label'))
          .map(button => button.outerHTML)
        """
    )
    assert unnamed == []


@pytest.mark.accessibility
@pytest.mark.regression
@pytest.mark.parametrize(("page_name", "nav_test_id", "heading"), PAGES)
def test_form_controls_have_labels(page, base_url: str, page_name: str, nav_test_id: str, heading: str) -> None:
    open_page(page, base_url, nav_test_id)
    unlabeled = page.evaluate(
        """
        () => Array.from(document.querySelectorAll('input, select, textarea'))
          .filter(el => el.offsetParent !== null)
          .filter(el => {
            const id = el.getAttribute('id');
            const hasForLabel = id && document.querySelector(`label[for="${id}"]`);
            const hasWrappingLabel = el.closest('label') && el.closest('label').innerText.trim();
            const hasAria = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby');
            return !(hasForLabel || hasWrappingLabel || hasAria);
          })
          .map(el => el.outerHTML)
        """
    )
    assert unlabeled == []


@pytest.mark.accessibility
@pytest.mark.regression
def test_keyboard_focus_reaches_main_navigation(page, base_url: str) -> None:
    page.goto(base_url)
    page.keyboard.press("Tab")
    focused_text = page.evaluate("() => document.activeElement?.textContent?.trim()")
    assert focused_text == "Dashboard"


@pytest.mark.accessibility
@pytest.mark.regression
@pytest.mark.parametrize(("page_name", "nav_test_id", "heading"), PAGES)
def test_interactive_targets_are_at_least_24px(page, base_url: str, page_name: str, nav_test_id: str, heading: str) -> None:
    open_page(page, base_url, nav_test_id)
    too_small = page.evaluate(
        """
        () => Array.from(document.querySelectorAll('button, input, select, textarea, a'))
          .filter(el => el.offsetParent !== null)
          .map(el => ({ html: el.outerHTML, rect: el.getBoundingClientRect() }))
          .filter(item => item.rect.width < 24 || item.rect.height < 24)
          .map(item => item.html)
        """
    )
    assert too_small == []


@pytest.mark.accessibility
@pytest.mark.regression
@pytest.mark.parametrize(("page_name", "nav_test_id", "heading"), PAGES)
def test_visible_text_meets_minimum_contrast(page, base_url: str, page_name: str, nav_test_id: str, heading: str) -> None:
    open_page(page, base_url, nav_test_id)
    failures = page.evaluate(
        """
        () => {
          function parseRgb(value) {
            if (!value) return null;
            const comma = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
            if (comma) return [Number(comma[1]), Number(comma[2]), Number(comma[3])];
            const space = value.match(/rgba?\((\d+)\s+(\d+)\s+(\d+)/);
            if (space) return [Number(space[1]), Number(space[2]), Number(space[3])];
            return null;
          }

          function channel(v) {
            v = v / 255;
            return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
          }

          function luminance(rgb) {
            return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2]);
          }

          function contrast(fg, bg) {
            const l1 = luminance(fg);
            const l2 = luminance(bg);
            const lighter = Math.max(l1, l2);
            const darker = Math.min(l1, l2);
            return (lighter + 0.05) / (darker + 0.05);
          }

          function isTransparent(value) {
            return !value || value === 'transparent' || value === 'rgba(0, 0, 0, 0)' || value === 'rgb(0 0 0 / 0)';
          }

          function effectiveBackground(el) {
            let node = el;
            while (node && node !== document.documentElement) {
              const bg = getComputedStyle(node).backgroundColor;
              if (!isTransparent(bg)) return bg;
              node = node.parentElement;
            }
            return getComputedStyle(document.body).backgroundColor || 'rgb(255, 255, 255)';
          }

          function visibleLeafTextElements() {
            return Array.from(document.querySelectorAll('h1, h2, h3, p, label, button, a, td, th, span, strong'))
              .filter(el => el.offsetParent !== null)
              .filter(el => {
                const text = el.innerText || el.textContent || '';
                return text.trim().length > 0;
              })
              .filter(el => !Array.from(el.children).some(child => (child.innerText || child.textContent || '').trim().length > 0));
          }

          return visibleLeafTextElements()
            .map(el => {
              const styles = getComputedStyle(el);
              const fg = parseRgb(styles.color);
              const bg = parseRgb(effectiveBackground(el));
              if (!fg || !bg) return null;

              const ratio = contrast(fg, bg);
              const fontSize = parseFloat(styles.fontSize);
              const fontWeight = Number(styles.fontWeight) || 400;
              const isLarge = fontSize >= 24 || (fontSize >= 18.66 && fontWeight >= 700);
              const required = isLarge ? 3 : 4.5;

              return {
                text: (el.innerText || el.textContent || '').trim(),
                ratio,
                required
              };
            })
            .filter(Boolean)
            .filter(item => item.ratio < item.required)
            .map(item => `${item.text} (${item.ratio.toFixed(2)} < ${item.required})`);
        }
        """
    )
    assert failures == []
