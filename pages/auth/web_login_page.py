"""Page Object for Velora Web Sign-In screen (/sign-in)."""

import re

from pages.base_page import BasePage


class WebLoginPage(BasePage):
    """Encapsulates locators and actions for /sign-in (Rule 1.1)."""

    ROUTE: str = "/sign-in"

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    work_email_input = "#email"
    password_input = "#password"
    email_field_error = "#email-error"
    password_field_error = "#password-error"
    password_visibility_toggle = 'button:has-text("Show"), button:has-text("Hide")'
    sign_in_button = 'button[type="submit"]'
    sign_up_link = 'a[href="/sign-up"]'
    forgot_password_link = 'a[href="/forgot-password"]'
    error_message_banner = '[role="alert"], [data-sonner-toast], [aria-label^="Notifications"] li'

    def open(self) -> "WebLoginPage":
        self.navigate_to(self.ROUTE)
        self.wait_for_visible(self.page.locator(self.work_email_input))
        return self

    def enter_email(self, email: str) -> "WebLoginPage":
        self.fill_locator(self.page.locator(self.work_email_input), email, "Work email input")
        return self

    def enter_password(self, password: str) -> "WebLoginPage":
        self.fill_locator(self.page.locator(self.password_input), password, "Password input")
        return self

    def toggle_password_visibility(self) -> "WebLoginPage":
        self.click_locator(
            self.page.locator(self.password_visibility_toggle).first,
            "Password visibility toggle",
        )
        return self

    def get_password_input_type(self) -> str:
        return self.page.locator(self.password_input).get_attribute("type") or ""

    def click_sign_in(self) -> None:
        self.click_locator(self.page.locator(self.sign_in_button), "Sign in button")

    def login(self, email: str, password: str) -> None:
        """Execute full sign-in form submission."""
        self.enter_email(email)
        self.enter_password(password)
        self.click_sign_in()

    def login_and_wait_for_app(self, email: str, password: str) -> None:
        """Sign in and wait until the browser navigates to /app."""
        self.login(email, password)
        self.wait_for_url(re.compile(r".*/app($|/.*)"), timeout_ms=self.navigation_timeout_ms)

    def click_sign_up_link(self) -> None:
        self.click_locator(self.page.locator(self.sign_up_link), "Sign up link")
        self.wait_for_url(re.compile(r".*/sign-up($|\?.*)"))

    def click_forgot_password_link(self) -> None:
        self.click_locator(self.page.locator(self.forgot_password_link), "Forgot password link")
        self.wait_for_url(re.compile(r".*/forgot-password($|\?.*)"))

    def get_heading_text(self) -> str:
        heading = self.page.locator(self.page_heading).first
        self.wait_for_visible(heading)
        return heading.inner_text().strip()

    def get_email_validation_message(self) -> str:
        error_locator = self.page.locator(self.email_field_error)
        if self.is_locator_visible(error_locator, timeout_ms=2000):
            return error_locator.inner_text().strip()
        return self.get_validation_message(self.page.locator(self.work_email_input))

    def get_password_validation_message(self) -> str:
        error_locator = self.page.locator(self.password_field_error)
        if self.is_locator_visible(error_locator, timeout_ms=2000):
            return error_locator.inner_text().strip()
        return self.get_validation_message(self.page.locator(self.password_input))

    def wait_for_auth_error_message(self, timeout_ms: int = 8000) -> str:
        """Wait for an error toast or inline alert after a failed login attempt."""
        return self.wait_for_feedback_text(timeout_ms=timeout_ms)

    def wait_until_on_sign_in_page(self) -> None:
        self.wait_for_url(re.compile(r".*/sign-in($|\?.*)"))
        self.wait_for_visible(self.page.locator(self.work_email_input))

    def is_sign_in_page_visible(self) -> bool:
        return self.is_locator_visible(self.page.locator(self.work_email_input))
