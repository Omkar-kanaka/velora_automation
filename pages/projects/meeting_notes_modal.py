"""Page Object for the 'Add meeting notes' modal on /app."""

from pages.base_page import BasePage


class MeetingNotesModal(BasePage):
    """Encapsulates locators and actions for the Add meeting notes dialog (Rule 1.1)."""

    # Class-level snake_case locators (Rule 7)
    dialog_root = '[role="dialog"]'
    title_input = "#notes-title"
    notes_textarea = "#notes-text"
    add_notes_button_name = "Add notes"
    cancel_button_name = "Cancel"

    def _dialog(self):
        return self.page.locator(self.dialog_root)

    def wait_until_open(self) -> "MeetingNotesModal":
        self.wait_for_visible(self._dialog())
        return self

    def is_open(self, timeout_ms: int = 1500) -> bool:
        return self.is_locator_visible(self._dialog(), timeout_ms=timeout_ms)

    def enter_title(self, title: str) -> "MeetingNotesModal":
        self.fill_locator(self.page.locator(self.title_input), title, "Meeting notes title input")
        return self

    def enter_notes(self, notes: str) -> "MeetingNotesModal":
        self.fill_locator(self.page.locator(self.notes_textarea), notes, "Meeting notes textarea")
        return self

    def is_add_notes_enabled(self) -> bool:
        return self._dialog().get_by_role("button", name=self.add_notes_button_name).is_enabled()

    def click_add_notes(self) -> None:
        btn = self._dialog().get_by_role("button", name=self.add_notes_button_name)
        self.click_locator(btn, "Add notes submit button")
        self.wait_for_hidden(self._dialog())

    def click_cancel(self) -> None:
        btn = self._dialog().get_by_role("button", name=self.cancel_button_name)
        self.click_locator(btn, "Cancel meeting notes button")
        self.wait_for_hidden(self._dialog())

    def add_meeting_notes(self, title: str, notes: str) -> None:
        self.wait_until_open()
        self.enter_title(title)
        self.enter_notes(notes)
        self.click_add_notes()
