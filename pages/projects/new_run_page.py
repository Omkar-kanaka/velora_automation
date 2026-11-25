"""Page Object for Velora Project 'New Run' Composer (/app/projects/<id>/new-run)."""

from pathlib import Path
import re

from pages.base_page import BasePage


class NewRunPage(BasePage):
    """Encapsulates locators and user actions for the New Run composer screen (Rule 1.1)."""

    # Class-level snake_case locators (Rule 7)
    page_heading = 'h1:has-text("What\'s changed in"), h2:has-text("What\'s changed in"), h1'
    subheading_text = "main p"
    prompt_textarea = "main textarea"
    start_run_button = 'button:has-text("Start Run"), button[type="submit"]:has-text("Start Run")'
    start_run_button_enabled = 'button:has-text("Start Run"):not([disabled]), button[type="submit"]:has-text("Start Run"):not([disabled])'
    start_run_button_disabled = 'button:has-text("Start Run")[disabled], button[type="submit"]:has-text("Start Run")[disabled]'
    add_context_button_name = "Add notes, docs or code"
    paste_meeting_notes_item_name = "Paste meeting notes"
    add_repository_item_name = "Add a repository"
    file_upload_input = 'input[type="file"]'
    start_answering_button = (
        'a:has-text("Start answering"), '
        'button:has-text("Start answering"), '
        '[data-slot="button"]:has-text("Start answering")'
    )
    getting_it_ready_card = 'div:has-text("Getting it ready")'
    first_question_ready_card = 'div:has-text("Your first question is ready")'

    def wait_until_loaded(self, project_name: str | None = None) -> None:
        """Wait for the New Run composer page to settle and heading to render."""
        self.wait_for_loading_settled()
        heading = self.page.locator(':is(h1, h2):has-text("What\'s changed in")').first
        self.wait_for_visible(heading, timeout_ms=self.default_timeout_ms)
        textarea = self.page.locator(self.prompt_textarea).first
        self.wait_for_visible(textarea, timeout_ms=self.default_timeout_ms)

        if project_name:
            self.wait_for_visible(
                self.page.locator(f':is(h1, h2):has-text("{project_name}")').first
            )

    def get_heading_text(self) -> str:
        """Get the h1 text, e.g. 'What's changed in nvidia?'."""
        heading = self.page.locator(':is(h1, h2):has-text("What\'s changed in")').first
        if not self.is_locator_visible(heading, timeout_ms=2000):
            heading = self.page.locator(self.page_heading).first
        self.wait_for_visible(heading)
        return heading.inner_text().strip()

    def get_subheading_text(self) -> str:
        """Get the subheading text, e.g. 'Run 2 starts fresh. Describe what's new...'."""
        sub = self.page.locator(self.subheading_text).first
        if self.is_locator_visible(sub, timeout_ms=3000):
            return sub.inner_text().strip()
        return ""

    def enter_prompt(self, text: str) -> "NewRunPage":
        """Type instruction or changes prompt into the textarea."""
        textarea = self.page.locator(self.prompt_textarea).first
        self.fill_locator(textarea, text, "New run prompt textarea")
        return self

    def clear_prompt(self) -> "NewRunPage":
        """Clear the prompt textarea."""
        textarea = self.page.locator(self.prompt_textarea).first
        self.fill_locator(textarea, "", "New run prompt textarea")
        return self

    def get_prompt_value(self) -> str:
        """Retrieve current text content of the prompt textarea."""
        textarea = self.page.locator(self.prompt_textarea).first
        self.wait_for_visible(textarea)
        return textarea.input_value()

    def is_start_run_button_enabled(self, timeout_ms: int = 3000) -> bool:
        """Verify the 'Start Run <N>' button is visible and enabled."""
        btn = self.page.locator(self.start_run_button_enabled).first
        return self.is_locator_visible(btn, timeout_ms=timeout_ms)

    def is_start_run_button_disabled(self, timeout_ms: int = 3000) -> bool:
        """Verify the 'Start Run <N>' button is disabled when prompt is empty."""
        btn = self.page.locator(self.start_run_button_disabled).first
        return self.is_locator_visible(btn, timeout_ms=timeout_ms)

    def get_start_run_button_text(self) -> str:
        """Return the label of the Start Run button (e.g. 'Start Run 2')."""
        btn = self.page.locator(self.start_run_button).first
        self.wait_for_visible(btn)
        return btn.inner_text().strip()

    def click_start_run(self) -> None:
        """Click the 'Start Run <N>' button to kick off the new run iteration."""
        btn = self.page.locator(self.start_run_button).first
        self.click_locator(btn, "Start Run button")
        self.wait_for_loading_settled()

    def open_add_context_menu(self) -> "NewRunPage":
        """Click the '+ Add notes, docs or code' dropdown button."""
        button = self.page.get_by_role("button", name=self.add_context_button_name)
        self.click_locator(button, "Add notes, docs or code button")
        return self

    def open_meeting_notes_modal(self) -> None:
        """Open the 'Paste meeting notes' modal."""
        self.open_add_context_menu()
        item = self.page.get_by_role("menuitem", name=self.paste_meeting_notes_item_name)
        self.click_locator(item, "Paste meeting notes menu item")

    def open_repository_modal(self) -> None:
        """Open the 'Add a repository' modal."""
        self.open_add_context_menu()
        item = self.page.get_by_role("menuitem", name=self.add_repository_item_name)
        self.click_locator(item, "Add a repository menu item")

    def upload_document(self, file_path: Path) -> None:
        """Upload a document file to the new run composer."""
        self.wait_for_loading_settled()
        self.logger.info("Uploading context document to new run: %s", file_path.name)
        self.page.locator(self.file_upload_input).first.set_input_files(str(file_path))

    def is_context_item_visible(self, label_text: str, timeout_ms: int = 4000) -> bool:
        """Check if an attached context badge or chip is rendered in the composer."""
        return self.is_locator_visible(
            self.page.locator("main").get_by_text(label_text, exact=False).first,
            timeout_ms=timeout_ms,
        )

    def wait_for_getting_it_ready_settled(self, timeout_ms: int = 60000) -> None:
        """Wait for the 'Getting it ready' checklist to settle and 'Start answering' card to appear."""
        self.logger.info("Waiting for new run kickoff preparation to settle...")
        start_answering = self.page.locator(self.start_answering_button).first
        self.wait_for_visible(start_answering, timeout_ms=timeout_ms)
        self.wait_for_visible(self.page.locator(self.first_question_ready_card).first, timeout_ms=10000)

    def is_start_answering_visible(self, timeout_ms: int = 3000) -> bool:
        """Check if the blue 'Start answering' card is visible."""
        return self.is_locator_visible(
            self.page.locator(self.start_answering_button).first,
            timeout_ms=timeout_ms,
        )

    def click_start_answering(self) -> None:
        """Click 'Start answering' button on kickoff completion card to advance to questions."""
        button = self.page.locator(self.start_answering_button).first
        self.click_locator(button, "Start answering button")
        self.wait_for_loading_settled()
