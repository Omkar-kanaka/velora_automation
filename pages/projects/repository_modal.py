"""Page Object for the 'Add a repository' modal on /app."""

from pages.base_page import BasePage


class RepositoryModal(BasePage):
    """Encapsulates locators and actions for the Add a repository dialog (Rule 1.1)."""

    # Class-level snake_case locators (Rule 7)
    dialog_root = '[role="dialog"]'
    repo_link_input = "#repo-link"
    repo_branch_input = "#repo-branch"
    repo_token_input = "#repo-token"
    public_radio_name = "Public"
    private_radio_name = "Private"
    add_repository_button_name = "Add repository"
    cancel_button_name = "Cancel"

    def _dialog(self):
        return self.page.locator(self.dialog_root)

    def wait_until_open(self) -> "RepositoryModal":
        self.wait_for_visible(self._dialog())
        return self

    def is_open(self, timeout_ms: int = 1500) -> bool:
        return self.is_locator_visible(self._dialog(), timeout_ms=timeout_ms)

    def enter_repository_link(self, url: str) -> "RepositoryModal":
        self.fill_locator(self.page.locator(self.repo_link_input), url, "Repository link input")
        return self

    def enter_branch(self, branch: str) -> "RepositoryModal":
        self.fill_locator(self.page.locator(self.repo_branch_input), branch, "Repository branch input")
        return self

    def select_public(self) -> "RepositoryModal":
        radio = self._dialog().get_by_role("radio", name=self.public_radio_name)
        self.click_locator(radio, "Public repository radio")
        return self

    def select_private(self) -> "RepositoryModal":
        radio = self._dialog().get_by_role("radio", name=self.private_radio_name)
        self.click_locator(radio, "Private repository radio")
        return self

    def is_private_selected(self) -> bool:
        radio = self._dialog().get_by_role("radio", name=self.private_radio_name)
        return (radio.get_attribute("aria-checked") or "").lower() == "true"

    def is_public_selected(self) -> bool:
        radio = self._dialog().get_by_role("radio", name=self.public_radio_name)
        return (radio.get_attribute("aria-checked") or "").lower() == "true"

    def is_access_token_visible(self, timeout_ms: int = 2000) -> bool:
        return self.is_locator_visible(self.page.locator(self.repo_token_input), timeout_ms=timeout_ms)

    def enter_access_token(self, token: str) -> "RepositoryModal":
        self.fill_locator(self.page.locator(self.repo_token_input), token, "Repository access token input")
        return self

    def get_access_token_value(self) -> str:
        return self.page.locator(self.repo_token_input).input_value()

    def is_add_repository_button_disabled(self) -> bool:
        btn = self._dialog().get_by_role("button", name=self.add_repository_button_name)
        return btn.is_disabled() or (btn.get_attribute("aria-disabled") == "true")

    def click_add_repository(self, expect_close: bool = True) -> None:
        btn = self._dialog().get_by_role("button", name=self.add_repository_button_name)
        self.click_locator(btn, "Add repository submit button")
        if expect_close:
            self.wait_for_hidden(self._dialog())

    def click_cancel(self) -> None:
        btn = self._dialog().get_by_role("button", name=self.cancel_button_name)
        self.click_locator(btn, "Cancel repository modal button")
        self.wait_for_hidden(self._dialog())

    def get_dialog_text(self) -> str:
        self.wait_for_visible(self._dialog())
        return self._dialog().inner_text().strip()

    def add_public_repository(self, url: str, branch: str = "") -> None:
        self.wait_until_open()
        self.enter_repository_link(url)
        if branch:
            self.enter_branch(branch)
        self.click_add_repository(expect_close=True)

    def add_private_repository(
        self,
        url: str,
        token: str = "",
        branch: str = "",
        expect_close: bool = True,
    ) -> None:
        self.wait_until_open()
        self.select_private()
        self.enter_repository_link(url)
        if token:
            self.enter_access_token(token)
        if branch:
            self.enter_branch(branch)
        self.click_add_repository(expect_close=expect_close)
