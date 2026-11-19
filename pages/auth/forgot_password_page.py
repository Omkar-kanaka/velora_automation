"""Page Object for Velora Forgot Password screen (/forgot-password)."""

import re

from pages.base_page import BasePage


class ForgotPasswordPage(BasePage):
    """Encapsulates locators and actions for /forgot-password (Rule 1.1)."""

    ROUTE: str = "/forgot-password"
    PASSWORD_RESET_ENDPOINT_SUBSTRING: str = "accounts:sendOobCode"

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    work_email_label = "Work email"
    email_field_error = "#email-error"
    send_reset_link_button = 'button[type="submit"]'
    back_to_sign_in_link_name = "Back to sign in"
    confirmation_heading_text = "Check your inbox"
    change_email_button_name = "Change"
    resend_link_button_name = "resend the link"
    main_container = "main"

    def _email_locator(self):
        return self.page.get_by_label(self.work_email_label, exact=True)

    def open(self) -> "ForgotPasswordPage":
        self.navigate_to(self.ROUTE)
        self.wait_for_visible(self._email_locator())
        return self

    def enter_email(self, email: str) -> "ForgotPasswordPage":
        self.fill_locator(self._email_locator(), email, "Forgot password Work email input")
        return self

    def click_send_reset_link(self) -> None:
        self.click_locator(self.page.locator(self.send_reset_link_button), "Send reset link button")

    def request_password_reset(self, email: str) -> None:
        self.enter_email(email)
        self.click_send_reset_link()

    def request_password_reset_and_get_api_status(self, email: str) -> int:
        """Submit password reset, wait for Firebase sendOobCode response and Step 2 UI."""
        self.enter_email(email)
        with self.page.expect_response(
            lambda resp: self.PASSWORD_RESET_ENDPOINT_SUBSTRING in resp.url
            and resp.request.method == "POST",
            timeout=self.navigation_timeout_ms,
        ) as response_info:
            self.click_send_reset_link()

        status_code = response_info.value.status
        self.wait_for_confirmation_step()
        return status_code

    def submit_invalid_email_and_check_api_called(self, email: str) -> bool:
        """Submit empty/malformed email and return whether the reset API was triggered."""
        api_called = False

        def _on_request(request) -> None:
            nonlocal api_called
            if self.PASSWORD_RESET_ENDPOINT_SUBSTRING in request.url:
                api_called = True

        self.page.on("request", _on_request)
        try:
            if email:
                self.enter_email(email)
            self.click_send_reset_link()
            self.wait_for_visible(self.page.locator(self.email_field_error), timeout_ms=3000)
        finally:
            self.page.remove_listener("request", _on_request)

        return api_called

    def wait_for_confirmation_step(self, timeout_ms: int | None = None) -> None:
        """Dynamically wait for Step 2 ('Check your inbox') heading to become visible."""
        heading = self.page.get_by_role("heading", name=self.confirmation_heading_text)
        self.wait_for_visible(heading, timeout_ms=timeout_ms or self.navigation_timeout_ms)

    def click_back_to_sign_in(self) -> None:
        link = self.page.get_by_role("link", name=self.back_to_sign_in_link_name)
        self.click_locator(link, "Back to sign in link")
        self.wait_for_url(re.compile(r".*/sign-in($|\?.*)"))

    def get_heading_text(self) -> str:
        heading = self.page.locator(self.page_heading).first
        self.wait_for_visible(heading)
        return heading.inner_text().strip()

    def get_email_validation_message(self) -> str:
        error_locator = self.page.locator(self.email_field_error)
        if self.is_locator_visible(error_locator, timeout_ms=2000):
            return error_locator.inner_text().strip()
        return self.get_validation_message(self._email_locator())

    def get_confirmation_body_text(self) -> str:
        container = self.page.locator(self.main_container).first
        self.wait_for_visible(container)
        return container.inner_text().strip()

    def is_change_email_button_visible(self) -> bool:
        return self.is_locator_visible(
            self.page.get_by_role("button", name=self.change_email_button_name),
            timeout_ms=3000,
        )

    def is_resend_link_button_visible(self) -> bool:
        return self.is_locator_visible(
            self.page.get_by_role("button", name=self.resend_link_button_name),
            timeout_ms=3000,
        )
