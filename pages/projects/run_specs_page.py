"""Page Object for Velora Stage 3: Specs (/specs) Review & Verification."""

import time
from typing import Any

from playwright.sync_api import Download, Locator, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage


class RunSpecsPage(BasePage):
    """Encapsulates locators and actions for Stage 3 specs generation, 10-file tabs, download, and drawer."""

    # Stepper and status locators (Rule 7)
    stepper_step_setup = "text='Setup'"
    stepper_step_pick_my_brain = "text='Pick my Brain'"
    stepper_step_specs = "text='Specs'"
    stepper_step_delivery = "text='Delivery'"

    specs_heading = "h1:has-text('Specs')"
    writing_specs_indicator = "text=/Writing the specs/i"
    ready_for_review_indicator = "text=/Ready for (your )?review/i"

    # Action buttons
    download_trigger_button = 'button:has-text("Download"), a:has-text("Download"), [data-slot="dropdown-menu-trigger"]:has-text("Download"), [data-slot="button"]:has-text("Download")'
    download_menu_item = '[role="menu"] [role="menuitem"], [data-slot="dropdown-menu-item"], [role="menuitem"]'
    request_changes_trigger_button = 'button:has-text("Request changes"), a:has-text("Request changes"), [data-slot="button"]:has-text("Request changes")'
    continue_to_delivery_button = 'button:has-text("Continue to Delivery"), a:has-text("Continue to Delivery"), [data-slot="button"]:has-text("Continue to Delivery")'

    # Request changes drawer ("Spec changes")
    drawer_container = "aside[aria-label='Spec changes'], [aria-label='Spec changes']"
    drawer_textarea = "aside[aria-label='Spec changes'] textarea, textarea[placeholder*='Updating the specs'], textarea[placeholder*='Describe a change']"
    drawer_send_button = "aside[aria-label='Spec changes'] button:has-text('Send')"
    drawer_close_button = "aside[aria-label='Spec changes'] button[aria-label='Close'], aside[aria-label='Spec changes'] button:has(svg.lucide-x)"

    # Tab selector & markdown container
    tab_button = "button[role='tab'], div.flex button:has-text('.md')"
    markdown_body = "article.prose, div.prose, div.markdown-body, main article, main div:has(h1)"

    def wait_until_loaded(self, timeout_ms: int = 20000) -> None:
        """Wait for /specs URL and main layout to load."""
        self.wait_for_loading_settled(timeout_ms=timeout_ms)
        self.page.wait_for_url("**/specs*", timeout=timeout_ms)
        self.logger.info("Specs page loaded: %s", self.page.url)

    def is_writing_specs(self, timeout_ms: int = 3000) -> bool:
        """Check if specs are currently being generated ('Writing the specs...')."""
        indicator = self.page.locator(self.writing_specs_indicator).first
        return self.is_locator_visible(indicator, timeout_ms=timeout_ms)

    def is_ready_for_review(self, timeout_ms: int = 3000) -> bool:
        """Check if specs generation has completed ('Ready for your review')."""
        ready_indicator = self.page.locator(self.ready_for_review_indicator).first
        if self.is_locator_visible(ready_indicator, timeout_ms=timeout_ms):
            return True
        # Fallback check: Continue to Delivery is enabled and writing indicator is gone
        btn = self.page.locator(self.continue_to_delivery_button).first
        writing = self.page.locator(self.writing_specs_indicator).first
        return self.is_locator_visible(btn, timeout_ms=1000) and not btn.is_disabled() and not writing.is_visible()

    def wait_for_specs_ready(self, timeout_ms: int = 600000) -> "RunSpecsPage":
        """Wait dynamically for specs generation to settle and become ready for review."""
        self.logger.info("Waiting for specs generation to complete (timeout=%d ms)...", timeout_ms)
        start_time = time.time()
        timeout_sec = timeout_ms / 1000.0

        ready_locator = self.page.locator(self.ready_for_review_indicator).first
        continue_btn = self.page.locator(self.continue_to_delivery_button).first
        writing_locator = self.page.locator(self.writing_specs_indicator).first

        while time.time() - start_time < timeout_sec:
            # Check if ready indicator is visible
            if ready_locator.is_visible():
                self.logger.info("Specs generation completed: 'Ready for your review' detected!")
                self.wait_for_loading_settled()
                return self

            # Check if continue button is enabled AND writing indicator is gone
            if continue_btn.is_visible() and not continue_btn.is_disabled():
                if not writing_locator.is_visible():
                    self.logger.info(
                        "Specs generation completed: 'Continue to Delivery' is enabled and writing indicator gone!"
                    )
                    self.wait_for_loading_settled()
                    return self

            # Log progress: count visible tabs
            tab_count = self.page.locator("button[role='tab'], [data-slot='tabs-trigger']").count()
            elapsed = int(time.time() - start_time)
            self.logger.info(
                "Specs generation in progress (%ds elapsed) — %d tabs visible so far...", elapsed, tab_count
            )
            self.page.wait_for_timeout(5000)

        # Final check with wait_for_visible so Playwright raises standard TimeoutError with details if timed out
        self.wait_for_visible(ready_locator, timeout_ms=5000)
        return self

    def is_continue_to_delivery_enabled(self, timeout_ms: int = 3000) -> bool:
        """Check if the 'Continue to Delivery' button is enabled and clickable."""
        btn = self.page.locator(self.continue_to_delivery_button).first
        if not self.is_locator_visible(btn, timeout_ms=timeout_ms):
            return False
        is_disabled = btn.is_disabled() or (btn.get_attribute("aria-disabled") == "true")
        return not is_disabled

    def is_continue_to_delivery_disabled(self, timeout_ms: int = 3000) -> bool:
        """Check if the 'Continue to Delivery' button is disabled."""
        btn = self.page.locator(self.continue_to_delivery_button).first
        if not self.is_locator_visible(btn, timeout_ms=timeout_ms):
            return True
        return btn.is_disabled() or (btn.get_attribute("aria-disabled") == "true")

    # ------------------------------------------------------------------
    # Spec Changes Side Drawer
    # ------------------------------------------------------------------
    def open_request_changes_drawer(self) -> "RunSpecsPage":
        """Click 'Request changes' button to open the side drawer."""
        btn = self.page.locator(self.request_changes_trigger_button).first
        self.click_locator(btn, "Request changes button")
        drawer = self.page.locator(self.drawer_container).first
        self.wait_for_visible(drawer, timeout_ms=5000)
        return self

    def is_request_changes_drawer_open(self, timeout_ms: int = 2000) -> bool:
        """Check if the 'Spec changes' drawer is currently visible."""
        drawer = self.page.locator(self.drawer_container).first
        if drawer.count() == 0:
            return False
        return self.is_locator_visible(drawer, timeout_ms=timeout_ms)

    def is_drawer_textarea_disabled(self) -> bool:
        """Check if the drawer textarea is disabled (e.g., during specs generation)."""
        textarea = self.page.locator(self.drawer_textarea).first
        if not textarea.is_visible():
            return False
        placeholder = textarea.get_attribute("placeholder") or ""
        return textarea.is_disabled() or "Updating the specs" in placeholder

    def is_drawer_send_button_disabled(self) -> bool:
        """Check if the drawer 'Send' button is disabled."""
        send_btn = self.page.locator(self.drawer_send_button).first
        if not send_btn.is_visible():
            return True
        return send_btn.is_disabled() or (send_btn.get_attribute("aria-disabled") == "true")

    def enter_request_changes_feedback(self, feedback: str) -> "RunSpecsPage":
        """Fill change feedback into the drawer textarea."""
        textarea = self.page.locator(self.drawer_textarea).first
        self.fill_locator(textarea, feedback, "Spec changes textarea")
        return self

    def submit_request_changes(self) -> "RunSpecsPage":
        """Click 'Send' in the Spec changes drawer."""
        send_btn = self.page.locator(self.drawer_send_button).first
        self.click_locator(send_btn, "Drawer Send button")
        self.wait_for_loading_settled()
        return self

    def close_request_changes_drawer(self) -> "RunSpecsPage":
        """Close the Spec changes drawer using the close 'X' button or Escape."""
        close_btn = self.page.locator(self.drawer_close_button).first
        drawer = self.page.locator(self.drawer_container).first
        if self.is_locator_visible(close_btn, timeout_ms=3000):
            self.click_locator(close_btn, "Spec changes close button")
        else:
            self.page.keyboard.press("Escape")

        # Wait for drawer element to be hidden/detached
        try:
            drawer.wait_for(state="hidden", timeout=4000)
        except Exception:
            self.logger.warning("Drawer not hidden after close click, pressing Escape...")
            self.page.keyboard.press("Escape")
            try:
                drawer.wait_for(state="hidden", timeout=3000)
            except Exception:
                pass

        self.wait_ms(500, reason="Wait for drawer animation to close")
        return self

    # ------------------------------------------------------------------
    # 10-File Tabs & Content Verification
    # ------------------------------------------------------------------
    def get_tab_locator(self, tab_name: str) -> Locator:
        """Get locator for a specific specification tab button."""
        return self.page.locator(
            f'button:has-text("{tab_name}"), a:has-text("{tab_name}"), [role="tab"]:has-text("{tab_name}")'
        ).first

    def is_tab_visible(self, tab_name: str, timeout_ms: int = 3000) -> bool:
        """Check if a specification tab button is visible."""
        return self.is_locator_visible(self.get_tab_locator(tab_name), timeout_ms=timeout_ms)

    def select_tab(self, tab_name: str) -> "RunSpecsPage":
        """Click a specification tab to switch documents."""
        tab = self.get_tab_locator(tab_name)
        self.click_locator(tab, f"Specification tab '{tab_name}'")
        self.wait_for_loading_settled()
        return self

    def get_document_preview_text(self) -> str:
        """Extract the full rendered markdown text of the currently open specification document."""
        container = self.page.locator(self.markdown_body).first
        self.wait_for_visible(container, timeout_ms=5000)
        return container.inner_text().strip()

    # ------------------------------------------------------------------
    # Download Flow
    # ------------------------------------------------------------------
    def trigger_download(self, timeout_ms: int = 15000) -> Download:
        """Trigger the download flow and return the captured Playwright Download object."""
        self.logger.info("Triggering specification download flow...")
        with self.page.expect_download(timeout=timeout_ms) as download_info:
            download_btn = self.page.locator(self.download_trigger_button).first
            self.click_locator(download_btn, "Download button")

            # Check if a menu opened with a specific download option
            menu_item = self.page.locator(self.download_menu_item).first
            if self.is_locator_visible(menu_item, timeout_ms=3000):
                self.click_locator(menu_item, "Download menu item")

        download = download_info.value
        self.logger.info("Download captured successfully: filename='%s'", download.suggested_filename)
        return download

    # ------------------------------------------------------------------
    # Stage 4 Delivery Transition
    # ------------------------------------------------------------------
    def click_continue_to_delivery(self) -> None:
        """Click 'Continue to Delivery' and advance to Stage 4."""
        btn = self.page.locator(self.continue_to_delivery_button).first
        self.click_locator(btn, "Continue to Delivery button")
        self.wait_for_loading_settled()
