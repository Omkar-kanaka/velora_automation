"""BasePage encapsulating resilient browser actions, waits, and Shadow DOM support."""

from pathlib import Path
from typing import Pattern

from playwright.sync_api import Download, Locator, Page, TimeoutError as PlaywrightTimeoutError

from utils.logger import get_logger


class BasePage:
    """Reusable Playwright interaction layer inherited by all Page Objects (Rule 1.1)."""

    DEFAULT_TIMEOUT_MS: int = 10000
    DEFAULT_NAVIGATION_RETRIES: int = 3

    # Class-level locators (Rule 7)
    loading_indicators = (
        '[role="status"][aria-label="Loading"], '
        '[role="status"]:has-text("Loading"), '
        '[aria-busy="true"], '
        'md-spinner, '
        '.skeleton'
    )
    notification_region = '[aria-label^="Notifications"]'
    notification_items = '[aria-label^="Notifications"] li, [data-sonner-toast]'
    inline_alerts = '[role="alert"]'

    def __init__(
        self,
        page: Page,
        base_url: str,
        default_timeout_ms: int = DEFAULT_TIMEOUT_MS,
        navigation_timeout_ms: int = 20000,
    ) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.default_timeout_ms = default_timeout_ms
        self.navigation_timeout_ms = navigation_timeout_ms
        self.logger = get_logger(self.__class__.__name__)

    def _resolve_url(self, path_or_url: str) -> str:
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url
        normalized = path_or_url if path_or_url.startswith("/") else f"/{path_or_url}"
        return f"{self.base_url}{normalized}"

    # ------------------------------------------------------------------
    # Resilient Navigation (Rule 2.3)
    # ------------------------------------------------------------------
    def navigate_to(
        self,
        path_or_url: str,
        max_attempts: int = DEFAULT_NAVIGATION_RETRIES,
    ) -> None:
        """Navigate with retry: Attempt 1 waits for 'load', fallback attempts use 'domcontentloaded'."""
        target_url = self._resolve_url(path_or_url)
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            wait_until = "load" if attempt == 1 else "domcontentloaded"
            try:
                self.logger.info(
                    "Navigating to URL: %s (attempt %d/%d, wait_until='%s')",
                    target_url,
                    attempt,
                    max_attempts,
                    wait_until,
                )
                self.page.goto(
                    target_url,
                    wait_until=wait_until,
                    timeout=self.navigation_timeout_ms,
                )
                self.wait_for_loading_settled()
                return
            except PlaywrightTimeoutError as exc:
                last_error = exc
                self.logger.warning(
                    "Navigation attempt %d/%d timed out for %s: %s",
                    attempt,
                    max_attempts,
                    target_url,
                    exc,
                )

        raise RuntimeError(
            f"Navigation to {target_url} failed after {max_attempts} attempts."
        ) from last_error

    def reload_page(self) -> None:
        """Reload the current page and wait for SPA loading states to settle."""
        self.logger.info("Reloading current page: %s", self.page.url)
        self.page.reload(wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
        self.wait_for_loading_settled()

    # ------------------------------------------------------------------
    # Synchronization & Loading Settlement (Rules 2.1 & 2.2)
    # ------------------------------------------------------------------
    def wait_for_loading_settled(self, timeout_ms: int | None = None) -> None:
        """Wait for spinners, loading overlays, and aria-busy indicators to disappear."""
        timeout = timeout_ms or self.default_timeout_ms
        loader = self.page.locator(self.loading_indicators).first
        try:
            if loader.count() > 0 and loader.is_visible():
                self.logger.info("Waiting for loading indicator to settle")
                loader.wait_for(state="hidden", timeout=timeout)
        except PlaywrightTimeoutError:
            self.logger.warning(
                "Loading indicator did not settle within %d ms on %s",
                timeout,
                self.page.url,
            )

    def wait_for_visible(self, locator: Locator, timeout_ms: int | None = None) -> None:
        """Dynamically wait for a locator to become visible."""
        locator.wait_for(state="visible", timeout=timeout_ms or self.default_timeout_ms)

    def wait_for_hidden(self, locator: Locator, timeout_ms: int | None = None) -> None:
        """Dynamically wait for a locator to become hidden."""
        locator.wait_for(state="hidden", timeout=timeout_ms or self.default_timeout_ms)

    def wait_for_url(
        self,
        url_pattern: str | Pattern[str],
        timeout_ms: int | None = None,
    ) -> None:
        """Dynamically wait for the page URL to match a pattern."""
        self.logger.info("Waiting for URL matching: %s", url_pattern)
        self.page.wait_for_url(url_pattern, timeout=timeout_ms or self.default_timeout_ms)
        self.wait_for_loading_settled()

    def wait_ms(self, milliseconds: int, reason: str = "") -> None:
        """Centralized fallback wait (tracked via logs; use dynamic waits whenever possible)."""
        self.logger.debug("Centralized wait_ms(%d) - reason: %s", milliseconds, reason or "unspecified")
        self.page.wait_for_timeout(milliseconds)

    # ------------------------------------------------------------------
    # Standard Reusable Interactions
    # ------------------------------------------------------------------
    def click_locator(self, locator: Locator, description: str = "element") -> None:
        """Ensure loading settled and element visible before clicking."""
        self.wait_for_loading_settled()
        self.wait_for_visible(locator)
        self.logger.info("Clicking element: %s", description)
        locator.click(timeout=self.default_timeout_ms)

    def fill_locator(self, locator: Locator, value: str, description: str = "input") -> None:
        """Ensure loading settled and input visible before filling."""
        self.wait_for_loading_settled()
        self.wait_for_visible(locator)
        self.logger.info("Filling element: %s", description)
        locator.fill(value, timeout=self.default_timeout_ms)

    def scroll_into_view(self, locator: Locator) -> None:
        """Scroll target element into the viewport."""
        locator.scroll_into_view_if_needed(timeout=self.default_timeout_ms)

    def trigger_download(self, trigger_locator: Locator, save_dir: Path) -> Path:
        """Click a download trigger and save the downloaded file using pathlib.Path."""
        save_dir.mkdir(parents=True, exist_ok=True)
        self.wait_for_loading_settled()
        with self.page.expect_download(timeout=self.default_timeout_ms) as download_info:
            trigger_locator.click()
        download: Download = download_info.value
        destination = save_dir / download.suggested_filename
        download.save_as(str(destination))
        self.logger.info("Saved downloaded file to: %s", destination)
        return destination

    # ------------------------------------------------------------------
    # Shadow DOM Helpers (Rule 2.4)
    # ------------------------------------------------------------------
    def click_shadow_element(self, host_selector: str, inner_selector: str) -> None:
        """Click an element inside a ShadowRoot via JS evaluation."""
        self.wait_for_loading_settled()
        self.logger.info("Clicking shadow element '%s' inside host '%s'", inner_selector, host_selector)
        clicked: bool = self.page.evaluate(
            """([hostSel, innerSel]) => {
                const host = document.querySelector(hostSel);
                if (!host || !host.shadowRoot) return false;
                const target = host.shadowRoot.querySelector(innerSel);
                if (!target) return false;
                target.click();
                return true;
            }""",
            [host_selector, inner_selector],
        )
        if not clicked:
            raise RuntimeError(
                f"Shadow DOM element '{inner_selector}' not found inside host '{host_selector}'."
            )

    def get_shadow_element_text(self, host_selector: str, inner_selector: str) -> str:
        """Retrieve innerText of an element located inside a ShadowRoot."""
        text: str | None = self.page.evaluate(
            """([hostSel, innerSel]) => {
                const host = document.querySelector(hostSel);
                if (!host || !host.shadowRoot) return null;
                const target = host.shadowRoot.querySelector(innerSel);
                return target ? (target.innerText || target.textContent || '').trim() : null;
            }""",
            [host_selector, inner_selector],
        )
        if text is None:
            raise RuntimeError(
                f"Shadow DOM element '{inner_selector}' not found inside host '{host_selector}'."
            )
        return text

    def fill_shadow_element(self, host_selector: str, inner_selector: str, value: str) -> None:
        """Set value and dispatch input/change events on an input inside a ShadowRoot."""
        self.wait_for_loading_settled()
        self.logger.info("Filling shadow element '%s' inside host '%s'", inner_selector, host_selector)
        filled: bool = self.page.evaluate(
            """([hostSel, innerSel, val]) => {
                const host = document.querySelector(hostSel);
                if (!host || !host.shadowRoot) return false;
                const target = host.shadowRoot.querySelector(innerSel);
                if (!target) return false;
                target.focus();
                target.value = val;
                target.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                target.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                return true;
            }""",
            [host_selector, inner_selector, value],
        )
        if not filled:
            raise RuntimeError(
                f"Shadow DOM input '{inner_selector}' not found inside host '{host_selector}'."
            )

    # ------------------------------------------------------------------
    # State Queries (Never assertions!)
    # ------------------------------------------------------------------
    def get_current_url(self) -> str:
        return self.page.url

    def get_page_title(self) -> str:
        return self.page.title()

    def is_locator_visible(self, locator: Locator, timeout_ms: int = 3000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def get_validation_message(self, locator: Locator) -> str:
        """Read native HTML5 validationMessage from a form input."""
        return str(locator.evaluate("el => el.validationMessage || ''"))

    def wait_for_feedback_text(self, timeout_ms: int = 6000) -> str:
        """Wait for either a Sonner toast notification or an inline [role='alert'] error/info banner."""
        feedback = self.page.locator(f"{self.notification_items}, {self.inline_alerts}").first
        try:
            feedback.wait_for(state="visible", timeout=timeout_ms)
            return feedback.inner_text().strip()
        except PlaywrightTimeoutError:
            return ""
