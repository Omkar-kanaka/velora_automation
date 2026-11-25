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
        input_loc = self.page.locator(self.storage_path_input)
        self.fill_locator(input_loc, path, "Storage Path input")
        input_loc.press("Tab")
        return self

    def cancel_storage_edit_form(self) -> None:
        section = self.page.locator(self.storage_section).first
        cancel_btn = section.get_by_role("button", name=self.cancel_button_name)
        if self.is_locator_visible(cancel_btn, timeout_ms=1000):
            self.click_locator(cancel_btn, "Storage Cancel button")
            self.wait_for_hidden(self.page.locator(self.storage_path_input))

    def click_storage_test_connection_button(self) -> "SettingsPage":
        section = self.page.locator(self.storage_section).first
        test_btn = section.get_by_role("button", name=self.test_connection_button_name)
        self.click_locator(test_btn, "Storage Test connection button")
        return self

    def get_storage_feedback_locator(self):
        section = self.page.locator(self.storage_section).first
        return section.locator(self.section_feedback).first

    def get_storage_feedback_text(self) -> str:
        locator = self.get_storage_feedback_locator()
        self.wait_for_visible(locator)
        return locator.inner_text().strip()

    def get_storage_field_error_text(self) -> str:
        section = self.page.locator(self.storage_section).first
        error_loc = section.locator(".text-destructive, [role='alert'], p").filter(
            has_text="absolute"
        ).first
        if self.is_locator_visible(error_loc, timeout_ms=3000):
            return error_loc.inner_text().strip()
        fallback = section.locator(".text-destructive").first
        if self.is_locator_visible(fallback, timeout_ms=1000):
            return fallback.inner_text().strip()
        return ""

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
        feedback_locator = self.get_storage_feedback_locator()
        self.wait_for_visible(feedback_locator)
        return response.status, payload, feedback_locator.inner_text().strip()

    # ------------------------------------------------------------------
    # AI Model Inline Form Actions (SET-11 through SET-14)
    # ------------------------------------------------------------------
    ai_provider_combobox = 'button[role="combobox"], [data-slot="combobox"]'
    ai_model_input = 'input[placeholder*="model" i], input[id*="model" i], input[name*="model" i]'
    ai_api_key_input = 'input[type="password"], input[id*="key" i], input[placeholder*="key" i]'
    ai_base_url_input = 'input[placeholder*="http" i], input[id*="url" i], input[placeholder*="url" i]'

    def _ai_section(self):
        return self.page.locator(self.ai_model_section).first

    def get_ai_model_header_summary(self) -> str:
        section = self._ai_section()
        summary = section.locator(self.db_header_summary).first
        if self.is_locator_visible(summary, timeout_ms=2000):
            return summary.inner_text().strip()
        header = section.locator("header").first
        return header.inner_text().strip()

    def open_ai_model_edit_form(self) -> "SettingsPage":
        section = self._ai_section()
        edit_btn = section.get_by_role("button", name=self.edit_button_name)
        self.click_locator(edit_btn, "AI model Edit button")
        cancel_btn = section.get_by_role("button", name=self.cancel_button_name)
        self.wait_for_visible(cancel_btn)
        return self

    def is_ai_model_edit_form_open(self, timeout_ms: int = 2000) -> bool:
        cancel_btn = self._ai_section().get_by_role("button", name=self.cancel_button_name)
        return self.is_locator_visible(cancel_btn, timeout_ms=timeout_ms)

    def select_ai_provider(self, provider_text: str) -> "SettingsPage":
        combobox = self._ai_section().locator(self.ai_provider_combobox).first
        current_text = combobox.inner_text().strip()
        if provider_text not in current_text:
            self.click_locator(combobox, f"AI Provider combobox ({provider_text})")
            option = self.page.locator('[role="option"]').filter(has_text=provider_text).first
            self.wait_for_visible(option)
            self.click_locator(option, f"AI Provider option '{provider_text}'")
        return self

    def get_selected_ai_provider(self) -> str:
        combobox = self._ai_section().locator(self.ai_provider_combobox).first
        return combobox.inner_text().strip()

    def get_ai_provider_options(self) -> list[str]:
        """Click combobox if not open, gather all role=option texts, close dropdown."""
        combobox = self._ai_section().locator(self.ai_provider_combobox).first
        self.click_locator(combobox, "AI Provider combobox to list options")
        options = self.page.locator('[role="option"]')
        self.wait_for_visible(options.first)
        texts = [opt.inner_text().strip() for opt in options.all()]
        self.page.keyboard.press("Escape")
        return texts

    def enter_ai_model(self, model_name: str) -> "SettingsPage":
        input_loc = self._ai_section().locator(self.ai_model_input).first
        self.fill_locator(input_loc, model_name, "AI Model input")
        return self

    def get_ai_model_value(self) -> str:
        return self._ai_section().locator(self.ai_model_input).first.input_value()

    def enter_ai_api_key(self, api_key: str) -> "SettingsPage":
        input_loc = self._ai_section().locator(self.ai_api_key_input).first
        self.fill_locator(input_loc, api_key, "AI API key input")
        return self

    def is_ai_api_key_masked(self) -> bool:
        input_loc = self._ai_section().locator(self.ai_api_key_input).first
        return (input_loc.get_attribute("type") or "").lower() == "password"

    def enter_ai_base_url(self, base_url: str) -> "SettingsPage":
        input_loc = self._ai_section().locator(self.ai_base_url_input).first
        self.fill_locator(input_loc, base_url, "AI Base URL input")
        return self

    def get_ai_base_url_value(self) -> str:
        return self._ai_section().locator(self.ai_base_url_input).first.input_value()

    def is_ai_base_url_visible(self) -> bool:
        input_loc = self._ai_section().locator(self.ai_base_url_input).first
        return self.is_locator_visible(input_loc, timeout_ms=1000)

    def cancel_ai_model_form(self) -> None:
        section = self._ai_section()
        cancel_btn = section.get_by_role("button", name=self.cancel_button_name)
        if self.is_locator_visible(cancel_btn, timeout_ms=1000):
            self.click_locator(cancel_btn, "AI model Cancel button")
            self.wait_for_hidden(cancel_btn)

    def click_ai_test_connection_button(self) -> "SettingsPage":
        test_btn = self._ai_section().get_by_role("button", name=self.test_connection_button_name)
        self.click_locator(test_btn, "AI model Test connection button")
        return self

    def get_ai_model_feedback_text(self, timeout_ms: int = 15000) -> str:
        feedback = self._ai_section().locator(self.section_feedback).first
        self.wait_for_visible(feedback, timeout_ms=timeout_ms)
        return feedback.inner_text().strip()

    def test_ai_model_connection(self) -> tuple[int, dict[str, Any], str]:
        """Trigger AI Model Test connection, capture API status/payload and inline UI feedback."""
        section = self._ai_section()
        test_btn = section.get_by_role("button", name=self.test_connection_button_name)
        with self.page.expect_response(
            lambda resp: "/settings/" in resp.url and "test" in resp.url and resp.request.method == "POST",
            timeout=self.navigation_timeout_ms,
        ) as resp_info:
            self.click_locator(test_btn, "AI model Test connection button")

        response = resp_info.value
        payload: dict[str, Any] = response.json() if response.ok else {}
        feedback_text = self.get_ai_model_feedback_text(timeout_ms=15000)
        return response.status, payload, feedback_text

    def save_ai_model_config(self) -> tuple[int, dict[str, Any]]:
        """Trigger Save button in AI Model section, return response status and payload."""
        section = self._ai_section()
        save_btn = section.get_by_role("button", name=self.save_button_name)
        with self.page.expect_response(
            lambda resp: "/settings/" in resp.url and resp.request.method in ("POST", "PUT", "PATCH"),
            timeout=self.navigation_timeout_ms,
        ) as resp_info:
            self.click_locator(save_btn, "AI model Save button")

        response = resp_info.value
        payload: dict[str, Any] = response.json() if response.ok else {}
        cancel_btn = section.get_by_role("button", name=self.cancel_button_name)
        self.wait_for_hidden(cancel_btn)
        return response.status, payload

    def fill_ai_model_form(self, profile: dict[str, Any], api_key: str = "") -> "SettingsPage":
        """Fill AI Model form with profile details and provided API key."""
        if "provider_option" in profile:
            self.select_ai_provider(profile["provider_option"])
        if "model" in profile and profile["model"]:
            self.enter_ai_model(profile["model"])
        if api_key:
            self.enter_ai_api_key(api_key)
        if "base_url" in profile and profile["base_url"] and self.is_ai_base_url_visible():
            self.enter_ai_base_url(profile["base_url"])
        return self


