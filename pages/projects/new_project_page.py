"""Page Object for Velora New Project & Context Composer (/app)."""

from pathlib import Path

from pages.base_page import BasePage


class NewProjectPage(BasePage):
    """Encapsulates locators and actions for /app Step 1 composer & Step 2 run setup (Rule 1.1)."""

    ROUTE: str = "/app"

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    expected_heading_text = "What are you building?"
    main_container = "main"
    prompt_textarea = "main textarea"
    start_button_name = "Start"
    start_button_enabled = 'button[aria-label="Start"]:not([disabled])'
    start_button_disabled = 'button[aria-label="Start"][disabled]'
    add_context_button_name = "Add notes, docs or code"
    paste_meeting_notes_item_name = "Paste meeting notes"
    add_repository_item_name = "Add a repository"
    file_upload_input = 'input[type="file"]'
    upload_error_alert = 'main [role="alert"]'
    project_name_input = 'main input[placeholder="Project name"]'
    end_date_trigger = 'button[aria-label^="End date"]'
    calendar_popover = '[data-slot="popover-content"]'
    calendar_next_month_button = (
        '[data-slot="popover-content"] button[aria-label*="next" i], '
        '[data-slot="popover-content"] .rdp-button_next'
    )
    calendar_enabled_days = '[data-slot="popover-content"] table button:not([disabled])'
    step_two_back_button_name = "Back"
    step_two_start_run_button_name = "Start the run"
    start_run_button_enabled = 'button[type="submit"]:has-text("Start the run"):not([disabled])'
    start_run_button_disabled = 'button[type="submit"]:has-text("Start the run")[disabled]'
    start_answering_button = 'button:has-text("Start answering")'
    getting_it_ready_card = 'div:has-text("Getting it ready")'
    first_question_ready_card = 'div:has-text("Your first question is ready")'

    def wait_until_loaded(self) -> None:
        self.wait_for_loading_settled()
        self.wait_for_visible(
            self.page.get_by_role("heading", name=self.expected_heading_text, level=1)
        )

    def open(self) -> "NewProjectPage":
        self.navigate_to(self.ROUTE)
        self.wait_until_loaded()
        return self

    def enter_prompt(self, text: str) -> "NewProjectPage":
        self.fill_locator(self.page.locator(self.prompt_textarea).first, text, "Project prompt textarea")
        return self

    def clear_prompt(self) -> "NewProjectPage":
        self.fill_locator(self.page.locator(self.prompt_textarea).first, "", "Project prompt textarea")
        return self

    def get_prompt_value(self) -> str:
        textarea = self.page.locator(self.prompt_textarea).first
        self.wait_for_visible(textarea)
        return textarea.input_value()

    def is_start_button_enabled(self, timeout_ms: int = 3000) -> bool:
        return self.is_locator_visible(self.page.locator(self.start_button_enabled).first, timeout_ms=timeout_ms)

    def is_start_button_disabled(self, timeout_ms: int = 3000) -> bool:
        return self.is_locator_visible(self.page.locator(self.start_button_disabled).first, timeout_ms=timeout_ms)

    def click_start(self) -> None:
        button = self.page.get_by_role("button", name=self.start_button_name)
        self.click_locator(button, "Start button")
        self.wait_for_step_two_loaded()

    def click_example_prompt(self, example_name: str) -> None:
        button = self.page.get_by_role("button", name=example_name)
        self.click_locator(button, f"Example prompt '{example_name}'")

    def open_add_context_menu(self) -> "NewProjectPage":
        button = self.page.get_by_role("button", name=self.add_context_button_name)
        self.click_locator(button, "Add notes, docs or code button")
        return self

    def open_meeting_notes_modal(self) -> None:
        self.open_add_context_menu()
        item = self.page.get_by_role("menuitem", name=self.paste_meeting_notes_item_name)
        self.click_locator(item, "Paste meeting notes menu item")

    def open_repository_modal(self) -> None:
        self.open_add_context_menu()
        item = self.page.get_by_role("menuitem", name=self.add_repository_item_name)
        self.click_locator(item, "Add a repository menu item")

    def upload_document(self, file_path: Path) -> None:
        self.wait_for_loading_settled()
        self.logger.info("Uploading document file: %s", file_path.name)
        self.page.locator(self.file_upload_input).first.set_input_files(str(file_path))

    def get_upload_alert_text(self, timeout_ms: int = 4000) -> str:
        alert = self.page.locator(self.upload_error_alert).first
        if self.is_locator_visible(alert, timeout_ms=timeout_ms):
            return alert.inner_text().strip()
        return self.wait_for_feedback_text(timeout_ms=timeout_ms)

    def get_main_content_text(self) -> str:
        container = self.page.locator(self.main_container).first
        self.wait_for_visible(container)
        return container.inner_text().strip()

    def is_context_item_visible(self, label_text: str, timeout_ms: int = 4000) -> bool:
        return self.is_locator_visible(
            self.page.locator(self.main_container).get_by_text(label_text, exact=False).first,
            timeout_ms=timeout_ms,
        )

    # ------------------------------------------------------------------
    # Step 2 (Run Setup / Timeline Review Screen on /app)
    # ------------------------------------------------------------------
    def wait_for_step_two_loaded(self, timeout_ms: int | None = None) -> None:
        self.wait_for_loading_settled()
        start_run = self.page.get_by_role("button", name=self.step_two_start_run_button_name)
        self.wait_for_visible(start_run, timeout_ms=timeout_ms or self.default_timeout_ms)

    def enter_project_name(self, name: str) -> "NewProjectPage":
        self.fill_locator(self.page.locator(self.project_name_input).first, name, "Project name input")
        return self

    def select_end_date(self) -> "NewProjectPage":
        """Open the Timeline end-date calendar popover and pick an enabled future date."""
        self.click_locator(self.page.locator(self.end_date_trigger).first, "Pick an end date button")
        popover = self.page.locator(self.calendar_popover).first
        self.wait_for_visible(popover)

        next_month = self.page.locator(self.calendar_next_month_button).first
        if next_month.count() > 0 and next_month.is_visible():
            self.click_locator(next_month, "Calendar next month button")

        enabled_days = self.page.locator(self.calendar_enabled_days)
        self.wait_for_visible(enabled_days.first)
        target_index = min(14, enabled_days.count() - 1)
        self.click_locator(enabled_days.nth(target_index), "Calendar end date day button")
        return self

    def is_start_run_button_visible(self) -> bool:
        return self.is_locator_visible(
            self.page.get_by_role("button", name=self.step_two_start_run_button_name),
            timeout_ms=3000,
        )

    def is_start_run_button_enabled(self, timeout_ms: int = 3000) -> bool:
        return self.is_locator_visible(
            self.page.locator(self.start_run_button_enabled).first,
            timeout_ms=timeout_ms,
        )

    def is_start_run_button_disabled(self, timeout_ms: int = 3000) -> bool:
        return self.is_locator_visible(
            self.page.locator(self.start_run_button_disabled).first,
            timeout_ms=timeout_ms,
        )

    def click_back_to_composer(self) -> None:
        back_btn = self.page.get_by_role("button", name=self.step_two_back_button_name)
        self.click_locator(back_btn, "Back button on Step 2")
        self.wait_until_loaded()

    def click_start_the_run(self) -> None:
        """Submit the Step 2 run configuration by clicking 'Start the run'."""
        button = self.page.locator(self.start_run_button_enabled).first
        self.click_locator(button, "Start the run button")

    def wait_for_getting_it_ready_settled(self, timeout_ms: int = 60000) -> None:
        """Wait for the 'Getting it ready' checklist to settle and 'Start answering' card to appear."""
        self.logger.info("Waiting for run kickoff preparation to settle...")
        start_answering = self.page.locator(self.start_answering_button).first
        self.wait_for_visible(start_answering, timeout_ms=timeout_ms)

    def is_start_answering_visible(self, timeout_ms: int = 3000) -> bool:
        """Check if the blue 'Start answering' card is visible."""
        return self.is_locator_visible(
            self.page.locator(self.start_answering_button).first,
            timeout_ms=timeout_ms,
        )

    def click_start_answering(self) -> "RunQuestionsPage":
        """Click 'Start answering' and transition into Stage 2 (Pick my Brain)."""
        button = self.page.locator(self.start_answering_button).first
        self.click_locator(button, "Start answering button")
        from pages.projects.run_questions_page import RunQuestionsPage

        questions_page = RunQuestionsPage(self.page, self.base_url)
        questions_page.wait_until_loaded()
        return questions_page
