"""Page Object for Velora Stage 2: Pick my Brain (/questions)."""

import time
from typing import TYPE_CHECKING, Any

from playwright.sync_api import Locator, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage

if TYPE_CHECKING:
    from pages.projects.run_specs_page import RunSpecsPage


class RunQuestionsPage(BasePage):
    """Encapsulates locators and actions for Stage 2 clarification questions."""

    # Stepper and page state locators (Rule 7)
    stepper_step_setup = "text='Setup'"
    stepper_step_pick_my_brain = "text='Pick my Brain'"
    stepper_step_specs = "text='Specs'"
    stepper_step_delivery = "text='Delivery'"

    # Question interaction locators
    waiting_for_you_badge = "text='Waiting for you'"
    question_heading = (
        'div:has-text("Waiting for you") p.text-lg, '
        'p.text-lg, '
        'main h2, '
        'main h3, '
        'main div.font-semibold, '
        'main p.font-semibold'
    )
    suggested_chip = (
        'button:has-text("Suggested"), '
        '[data-slot="button"]:has-text("Suggested")'
    )
    answer_textarea = 'main textarea[placeholder*="Type your answer"], main textarea'
    submit_answer_button = 'button:has-text("Submit answer")'
    submit_answer_button_enabled = 'button:has-text("Submit answer"):not([disabled])'

    # Completion state locators
    completion_banner = "text=\"That's everything for now\""
    continue_to_specs_button = (
        'button:has-text("Continue to Specs"), '
        'a:has-text("Continue to Specs"), '
        '[data-slot="button"]:has-text("Continue to Specs")'
    )
    answered_so_far_header = 'button:has-text("Answered so far"), div:has-text("Answered so far")'
    answered_toggle_button = 'button:has-text("Hide"), button:has-text("Show")'

    def wait_until_loaded(self, timeout_ms: int = 15000) -> None:
        """Wait for questions page URL and dynamic components to render."""
        self.wait_for_loading_settled(timeout_ms=timeout_ms)
        self.page.wait_for_url("**/questions", timeout=timeout_ms)
        self.logger.info("Questions page loaded: %s", self.page.url)

    def has_unanswered_question(self, timeout_ms: int = 3000) -> bool:
        """Return True if an active unanswered question card is displayed."""
        submit_btn = self.page.locator(self.submit_answer_button).first
        textarea = self.page.locator(self.answer_textarea).first
        badge = self.page.locator(self.waiting_for_you_badge).first
        suggested = self.page.locator(self.suggested_chip).first
        return (
            self.is_locator_visible(submit_btn, timeout_ms=timeout_ms)
            or self.is_locator_visible(textarea, timeout_ms=500)
            or self.is_locator_visible(badge, timeout_ms=500)
            or self.is_locator_visible(suggested, timeout_ms=500)
        )

    def is_completion_card_visible(self, timeout_ms: int = 3000) -> bool:
        """Check if 'That's everything for now' card or 'Continue to Specs' button is visible."""
        continue_btn = self.page.locator(self.continue_to_specs_button).first
        return self.is_locator_visible(continue_btn, timeout_ms=timeout_ms)

    def wait_for_next_round_or_completion(self, timeout_ms: int = 35000) -> str:
        """Wait dynamically for either a new question or the completion card to appear.

        Returns:
            'completion' if 'Continue to Specs' or completion card is visible.
            'question' if an active question is visible.
            'timeout' if neither is visible within timeout_ms.
        """
        start = time.time()
        timeout_sec = timeout_ms / 1000.0

        while time.time() - start < timeout_sec:
            if self.is_completion_card_visible(timeout_ms=500):
                return "completion"
            if self.has_unanswered_question(timeout_ms=500):
                return "question"
            self.page.wait_for_timeout(500)

        # Final check
        if self.is_completion_card_visible(timeout_ms=1000):
            return "completion"
        if self.has_unanswered_question(timeout_ms=1000):
            return "question"
        return "timeout"

    def get_current_question_text(self) -> str:
        """Extract current question text using textarea aria-label or question card paragraph."""
        # 1. From textarea aria-label (accessible property set by Velora UI)
        textarea = self.page.locator(self.answer_textarea).first
        if self.is_locator_visible(textarea, timeout_ms=1500):
            aria_label = textarea.get_attribute("aria-label") or ""
            if len(aria_label.strip()) > 5:
                return aria_label.strip()

        # 2. From paragraph inside question card
        card_p = self.page.locator('div:has-text("Waiting for you") p.text-lg, p.text-lg').first
        if self.is_locator_visible(card_p, timeout_ms=1500):
            text = card_p.inner_text().strip()
            if len(text) > 5:
                return text

        # 3. Fallback scan of heading elements
        headings = self.page.locator(self.question_heading)
        for i in range(headings.count()):
            text = headings.nth(i).inner_text().strip()
            if len(text) > 5 and not any(skip in text for skip in ["Projects", "Pick my Brain", "Waiting for you", "Answered"]):
                return text
        return ""

    def get_suggested_chip_locator(self) -> Locator:
        """Get the locator for the suggested answer chip or button."""
        # 1. Primary: Button with 'Suggested' text
        chip = self.page.locator(self.suggested_chip).first
        if chip.count() > 0 and chip.is_visible():
            return chip

        # 2. Secondary: Fallback to the first action button on the question card (//button[@data-slot="button"])[1]
        fallback_chip = self.page.locator('xpath=(//button[@data-slot="button"])[1]').first
        if fallback_chip.count() > 0 and fallback_chip.is_visible():
            return fallback_chip

        return chip

    def has_suggested_chip(self, timeout_ms: int = 2000) -> bool:
        """Check if a '💡 Suggested: ...' chip is available for the current question."""
        chip = self.get_suggested_chip_locator()
        return self.is_locator_visible(chip, timeout_ms=timeout_ms)

    def get_suggested_chip_text(self) -> str:
        """Extract the text inside the suggested chip."""
        chip = self.get_suggested_chip_locator()
        if chip.count() > 0 and chip.is_visible():
            return chip.inner_text().strip()
        return ""

    def click_suggested_chip(self) -> "RunQuestionsPage":
        """Click the suggested answer chip to populate the textarea."""
        chip = self.get_suggested_chip_locator()
        self.click_locator(chip, "Suggested answer chip")
        return self

    def fill_custom_answer(self, text: str) -> "RunQuestionsPage":
        """Type custom answer text into the question textarea."""
        textarea = self.page.locator(self.answer_textarea).first
        self.fill_locator(textarea, text, "Answer textarea")
        return self

    def submit_answer(self) -> "RunQuestionsPage":
        """Click 'Submit answer' and wait for loading settlement."""
        submit_btn = self.page.locator(self.submit_answer_button_enabled).first
        self.wait_for_visible(submit_btn, timeout_ms=5000)
        self.click_locator(submit_btn, "Submit answer button")
        self.wait_for_loading_settled(timeout_ms=10000)
        return self

    def answer_current_question(self, preferred_text: str | None = None) -> "RunQuestionsPage":
        """Answer the active question using preferred_text, suggested chip, or fallback."""
        if preferred_text:
            self.fill_custom_answer(preferred_text)
        elif self.has_suggested_chip():
            self.click_suggested_chip()
        else:
            self.fill_custom_answer("Confirmed and aligned with requirements.")
        self.submit_answer()
        return self

    def answer_all_questions_dynamically(
        self,
        max_rounds: int = 35,
    ) -> "RunQuestionsPage":
        """Loop through all dynamic questions by clicking suggested answers until completion card appears."""
        self.logger.info("Starting dynamic question answering loop (max_rounds=%d)...", max_rounds)

        for round_idx in range(1, max_rounds + 1):
            state = self.wait_for_next_round_or_completion(timeout_ms=35000)
            if state == "completion":
                self.logger.info("Completion card reached after %d rounds.", round_idx - 1)
                break
            if state == "timeout":
                self.logger.warning(
                    "Neither a question nor completion card appeared within 35s at round %d.", round_idx
                )
                break

            question_text = self.get_current_question_text()
            self.logger.info("Round %d Question: %s", round_idx, question_text)

            # Click suggested answer button and submit (don't type the same text every time)
            if self.has_suggested_chip(timeout_ms=4000):
                chip_text = self.get_suggested_chip_text()
                self.logger.info("Round %d: Clicking suggested answer chip: %s", round_idx, chip_text)
                self.click_suggested_chip()
            else:
                textarea = self.page.locator(self.answer_textarea).first
                if self.is_locator_visible(textarea, timeout_ms=1000):
                    self.logger.info("Round %d: No suggested chip found, typing confirmation...", round_idx)
                    self.fill_custom_answer("Yes, proceed as planned.")

            self.submit_answer()
            self.wait_ms(1500, reason="Wait for question transition animation")

        return self

    def toggle_answered_accordion(self) -> "RunQuestionsPage":
        """Toggle the 'Answered so far' accordion view."""
        toggle_btn = self.page.locator(self.answered_toggle_button).first
        if self.is_locator_visible(toggle_btn, timeout_ms=3000):
            self.click_locator(toggle_btn, "Answered accordion toggle")
        return self

    def click_continue_to_specs(self) -> "RunSpecsPage":
        """Click 'Continue to Specs' and transition to Stage 3 (Specs)."""
        continue_btn = self.page.locator(self.continue_to_specs_button).first
        self.click_locator(continue_btn, "Continue to Specs button")
        from pages.projects.run_specs_page import RunSpecsPage

        specs_page = RunSpecsPage(self.page, self.base_url)
        specs_page.wait_until_loaded()
        return specs_page
