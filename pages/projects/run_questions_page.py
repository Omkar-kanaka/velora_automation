"""Page Object for Velora Stage 2: Pick my Brain (/questions)."""

from typing import TYPE_CHECKING, Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

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
    question_heading = "main h2, main h3, main div.font-semibold, main p.font-semibold"
    suggested_chip = 'button:has-text("Suggested:")'
    answer_textarea = 'main textarea[placeholder*="Type your answer"], main textarea'
    submit_answer_button = 'button:has-text("Submit answer")'

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
        return self.is_locator_visible(submit_btn, timeout_ms=timeout_ms)

    def get_current_question_text(self) -> str:
        """Extract current question heading text."""
        headings = self.page.locator(self.question_heading)
        for i in range(headings.count()):
            text = headings.nth(i).inner_text().strip()
            if text and not any(skip in text for skip in ["Projects", "Pick my Brain", "Waiting for you", "Answered"]):
                return text
        return ""

    def has_suggested_chip(self, timeout_ms: int = 2000) -> bool:
        """Check if a '💡 Suggested: ...' chip is available for the current question."""
        chip = self.page.locator(self.suggested_chip).first
        return self.is_locator_visible(chip, timeout_ms=timeout_ms)

    def get_suggested_chip_text(self) -> str:
        """Extract the text inside the suggested chip."""
        chip = self.page.locator(self.suggested_chip).first
        if chip.count() > 0 and chip.is_visible():
            return chip.inner_text().strip()
        return ""

    def click_suggested_chip(self) -> "RunQuestionsPage":
        """Click the suggested answer chip to populate the textarea."""
        chip = self.page.locator(self.suggested_chip).first
        self.click_locator(chip, "Suggested answer chip")
        return self

    def fill_custom_answer(self, text: str) -> "RunQuestionsPage":
        """Type custom answer text into the question textarea."""
        textarea = self.page.locator(self.answer_textarea).first
        self.fill_locator(textarea, text, "Answer textarea")
        return self

    def submit_answer(self) -> "RunQuestionsPage":
        """Click 'Submit answer' and wait for loading settlement."""
        submit_btn = self.page.locator(self.submit_answer_button).first
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
            self.fill_custom_answer("Confirmed and aligned with functional requirements.")
        self.submit_answer()
        return self

    def is_completion_card_visible(self, timeout_ms: int = 3000) -> bool:
        """Check if 'That's everything for now' card or 'Continue to Specs' button is visible."""
        continue_btn = self.page.locator(self.continue_to_specs_button).first
        return self.is_locator_visible(continue_btn, timeout_ms=timeout_ms)

    def answer_all_questions_dynamically(
        self,
        qa_config: dict[str, Any] | None = None,
        max_rounds: int = 25,
    ) -> "RunQuestionsPage":
        """Loop through all dynamic questions until the completion card is displayed."""
        self.logger.info("Starting dynamic question answering loop (max_rounds=%d)...", max_rounds)

        for round_idx in range(1, max_rounds + 1):
            if self.is_completion_card_visible(timeout_ms=2500):
                self.logger.info("Completion card reached after %d rounds.", round_idx - 1)
                break

            if not self.has_unanswered_question(timeout_ms=5000):
                self.logger.info("No unanswered question found at round %d.", round_idx)
                break

            question_text = self.get_current_question_text().lower()
            self.logger.info("Round %d Question: %s", round_idx, question_text)

            selected_answer: str | None = None
            if qa_config and "answers_by_keyword" in qa_config:
                for entry in qa_config["answers_by_keyword"]:
                    if entry["keyword"].lower() in question_text:
                        selected_answer = entry["answer"]
                        self.logger.info("Matched keyword '%s' -> using configured answer.", entry["keyword"])
                        break

            if selected_answer:
                self.fill_custom_answer(selected_answer)
            elif self.has_suggested_chip():
                self.logger.info("Using suggested answer chip: %s", self.get_suggested_chip_text())
                self.click_suggested_chip()
            elif qa_config and "fallback_answer" in qa_config:
                self.fill_custom_answer(qa_config["fallback_answer"])
            else:
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
