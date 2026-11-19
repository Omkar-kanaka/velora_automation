"""Page Object for Velora Settings screen (/app/settings)."""

from typing import Any

from pages.base_page import BasePage


class SettingsPage(BasePage):
    """Encapsulates locators and actions for /app/settings (Rule 1.1)."""

    ROUTE: str = "/app/settings"
    DB_TEST_ENDPOINT_SUBSTRING: str = "/v1/settings/database/test"
    DB_SAVE_ENDPOINT_SUBSTRING: str = "/v1/settings/database"
    STORAGE_TEST_ENDPOINT_SUBSTRING: str = "/v1/settings/storage/test"

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    expected_heading_text = "Settings"
    database_section_text = "Database"
    ai_model_section_text = "AI model"
    storage_section_text = "Storage"

    database_section = 'main section:has(h2:has-text("Database"))'
    ai_model_section = 'main section:has(h2:has-text("AI model"))'
    storage_section = 'main section:has(h2:has-text("Storage"))'

    db_kind_combobox = "#settings-database-kind"
    db_kind_option = '[role="option"]'
    db_host_input = "#settings-database-host"
    db_port_input = "#settings-database-port"
    db_name_input = "#settings-database-database"
    db_username_input = "#settings-database-username"
    db_password_input = "#settings-database-password"
    db_header_summary = "header span.truncate"
    storage_path_input = "#settings-storage-path"

    edit_button_name = "Edit"
    cancel_button_name = "Cancel"
    save_button_name = "Save"
    test_connection_button_name = "Test connection"
    section_feedback = '[role="alert"], [role="status"]'

    def wait_until_loaded(self) -> None:
        self.wait_for_loading_settled()
        self.wait_for_visible(
            self.page.get_by_role("heading", name=self.expected_heading_text, level=1)
        )

    def open(self) -> "SettingsPage":
        self.navigate_to(self.ROUTE)
        self.wait_until_loaded()
        return self

    def get_heading_text(self) -> str:
        self.wait_until_loaded()
        return self.page.locator(self.page_heading).first.inner_text().strip()

    def is_loaded(self) -> bool:
        return self.is_locator_visible(self.page.locator(self.page_heading).first)

    # ------------------------------------------------------------------
    # Section Queries (SET-01)
    # ------------------------------------------------------------------
    def is_database_section_visible(self) -> bool:
        return self.is_locator_visible(self.page.locator(self.database_section).first)

    def is_ai_model_section_visible(self) -> bool:
        return self.is_locator_visible(self.page.locator(self.ai_model_section).first)

    def is_storage_section_visible(self) -> bool:
        return self.is_locator_visible(self.page.locator(self.storage_section).first)

    def get_database_section_text(self) -> str:
        section = self.page.locator(self.database_section).first
        self.wait_for_visible(section)
        return section.inner_text().strip()

    def get_ai_model_section_text(self) -> str:
        section = self.page.locator(self.ai_model_section).first
        self.wait_for_visible(section)
        return section.inner_text().strip()

    def get_storage_section_text(self) -> str:
        section = self.page.locator(self.storage_section).first
        self.wait_for_visible(section)
        return section.inner_text().strip()

    # ------------------------------------------------------------------
    # Database Inline Form Actions (SET-02, SET-03, SET-04)
    # ------------------------------------------------------------------
    def open_database_edit_form(self) -> "SettingsPage":
        section = self.page.locator(self.database_section).first
        edit_btn = section.get_by_role("button", name=self.edit_button_name)
        self.click_locator(edit_btn, "Database Edit button")
        self.wait_for_visible(self.page.locator(self.db_port_input))
        return self

    def is_database_edit_form_open(self, timeout_ms: int = 1500) -> bool:
        return self.is_locator_visible(self.page.locator(self.db_port_input), timeout_ms=timeout_ms)

    def select_database_kind(self, option_text: str) -> "SettingsPage":
        combobox = self.page.locator(self.db_kind_combobox).first
        current_text = combobox.inner_text().strip()
        if option_text not in current_text:
            self.click_locator(combobox, f"Database Kind combobox ({option_text})")
            option = self.page.locator(self.db_kind_option).filter(has_text=option_text).first
            self.wait_for_visible(option)
            self.click_locator(option, f"Database Kind option '{option_text}'")
        return self

    def enter_database_host(self, host: str) -> "SettingsPage":
        self.fill_locator(self.page.locator(self.db_host_input), host, "Database Host input")
        return self

    def enter_database_port(self, port: str) -> "SettingsPage":
        self.fill_locator(self.page.locator(self.db_port_input), str(port), "Database Port input")
        return self

    def enter_database_name(self, db_name: str) -> "SettingsPage":
        self.fill_locator(self.page.locator(self.db_name_input), db_name, "Database Name input")
        return self

    def enter_database_username(self, username: str) -> "SettingsPage":
        self.fill_locator(self.page.locator(self.db_username_input), username, "Database Username input")
        return self

    def enter_database_password(self, password: str) -> "SettingsPage":
        self.fill_locator(self.page.locator(self.db_password_input), password, "Database Password input")
        return self

    def fill_database_form(self, profile: dict[str, Any]) -> "SettingsPage":
        """Fill database connection form with provided profile values."""
        if "option_text" in profile:
            self.select_database_kind(profile["option_text"])
        if "host" in profile:
            self.enter_database_host(profile["host"])
        if "port" in profile:
            self.enter_database_port(str(profile["port"]))
        if "database" in profile:
            self.enter_database_name(profile["database"])
        if "username" in profile:
            self.enter_database_username(profile["username"])
        if "password" in profile:
            self.enter_database_password(profile["password"])
        return self

    def get_database_host_value(self) -> str:
        return self.page.locator(self.db_host_input).input_value()

    def get_database_port_value(self) -> str:
        return self.page.locator(self.db_port_input).input_value()

    def get_database_name_value(self) -> str:
        return self.page.locator(self.db_name_input).input_value()

    def get_database_username_value(self) -> str:
        return self.page.locator(self.db_username_input).input_value()

    def get_database_kind_value(self) -> str:
        return self.page.locator(self.db_kind_combobox).inner_text().strip()

    def get_database_header_summary(self) -> str:
        section = self.page.locator(self.database_section).first
        summary = section.locator(self.db_header_summary).first
        if self.is_locator_visible(summary, timeout_ms=2000):
            return summary.inner_text().strip()
        header = section.locator("header").first
        return header.inner_text().strip()

    def cancel_database_edit_form(self) -> None:
        section = self.page.locator(self.database_section).first
        cancel_btn = section.get_by_role("button", name=self.cancel_button_name)
        if self.is_locator_visible(cancel_btn, timeout_ms=1000):
            self.click_locator(cancel_btn, "Database Cancel button")
            self.wait_for_hidden(self.page.locator(self.db_port_input))

    def save_database_config(self) -> tuple[int, dict[str, Any]]:
        """Trigger Save button in Database section, return response status and payload."""
        section = self.page.locator(self.database_section).first
        save_btn = section.get_by_role("button", name=self.save_button_name)
        with self.page.expect_response(
            lambda resp: self.DB_SAVE_ENDPOINT_SUBSTRING in resp.url
            and resp.request.method in ("POST", "PUT", "PATCH"),
            timeout=self.navigation_timeout_ms,
        ) as resp_info:
            self.click_locator(save_btn, "Database Save button")

        response = resp_info.value
        payload: dict[str, Any] = response.json() if response.ok else {}
        self.wait_for_hidden(self.page.locator(self.db_port_input))
        return response.status, payload

    def test_database_connection(self) -> tuple[int, dict[str, Any], str]:
        """Trigger Database Test connection, capture API status/payload and inline UI feedback."""
        section = self.page.locator(self.database_section).first
        test_btn = section.get_by_role("button", name=self.test_connection_button_name)
        with self.page.expect_response(
            lambda resp: self.DB_TEST_ENDPOINT_SUBSTRING in resp.url
            and resp.request.method == "POST",
            timeout=self.navigation_timeout_ms,
        ) as resp_info:
            self.click_locator(test_btn, "Database Test connection button")

        response = resp_info.value
        payload: dict[str, Any] = response.json() if response.ok else {}
        feedback_locator = section.locator(self.section_feedback).first
        self.wait_for_visible(feedback_locator)
        return response.status, payload, feedback_locator.inner_text().strip()

    # ------------------------------------------------------------------
    # Storage Inline Form Actions (SET-05, SET-06, SET-07)
    # ------------------------------------------------------------------
    def open_storage_edit_form(self) -> "SettingsPage":
        section = self.page.locator(self.storage_section).first
        edit_btn = section.get_by_role("button", name=self.edit_button_name)
        self.click_locator(edit_btn, "Storage Edit button")
        self.wait_for_visible(self.page.locator(self.storage_path_input))
        return self

    def is_storage_edit_form_open(self, timeout_ms: int = 1500) -> bool:
        return self.is_locator_visible(self.page.locator(self.storage_path_input), timeout_ms=timeout_ms)

    def enter_storage_path(self, path: str) -> "SettingsPage":
        self.fill_locator(self.page.locator(self.storage_path_input), path, "Storage Path input")
        return self

    def cancel_storage_edit_form(self) -> None:
        section = self.page.locator(self.storage_section).first
        cancel_btn = section.get_by_role("button", name=self.cancel_button_name)
        self.click_locator(cancel_btn, "Storage Cancel button")
        self.wait_for_hidden(self.page.locator(self.storage_path_input))

    def test_storage_connection(self) -> tuple[int, dict[str, Any], str]:
        """Trigger Storage Test connection, capture API status/payload and inline UI feedback."""
        section = self.page.locator(self.storage_section).first
        test_btn = section.get_by_role("button", name=self.test_connection_button_name)
        with self.page.expect_response(
            lambda resp: self.STORAGE_TEST_ENDPOINT_SUBSTRING in resp.url
            and resp.request.method == "POST",
            timeout=self.navigation_timeout_ms,
        ) as resp_info:
            self.click_locator(test_btn, "Storage Test connection button")

        response = resp_info.value
        payload: dict[str, Any] = response.json() if response.ok else {}
        feedback_locator = section.locator(self.section_feedback).first
        self.wait_for_visible(feedback_locator)
        return response.status, payload, feedback_locator.inner_text().strip()
