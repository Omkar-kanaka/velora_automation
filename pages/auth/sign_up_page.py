"""Page Object for Velora Sign-Up screen (/sign-up)."""

import re

from pages.base_page import BasePage


class SignUpPage(BasePage):
    """Encapsulates locators and actions for /sign-up (Rule 1.1)."""

    ROUTE: str = "/sign-up"

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    work_email_label = "Work email"
    password_label = "Password"
    confirm_password_label = "Confirm password"
    create_account_button = 'button[type="submit"]'
    sign_in_link = 'a[href="/sign-in"]'
    password_rule_length_text = "8+ characters"
    password_rule_case_text = "Upper & lowercase"
    password_rule_number_text = "A number"
    password_rule_symbol_text = "A symbol"
    mismatch_message_locator = 'text=/match|mismatch/i'

    def _email_locator(self):
        return self.page.get_by_label(self.work_email_label, exact=True)

    def _password_locator(self):
        return self.page.get_by_label(self.password_label, exact=True)

    def _confirm_password_locator(self):
        return self.page.get_by_label(self.confirm_password_label, exact=True)

    def open(self) -> "SignUpPage":
        self.navigate_to(self.ROUTE)
        self.wait_for_visible(self._email_locator())
        return self

    def enter_email(self, email: str) -> "SignUpPage":
        self.fill_locator(self._email_locator(), email, "Sign-up Work email input")
        return self

    def enter_password(self, password: str) -> "SignUpPage":
        self.fill_locator(self._password_locator(), password, "Sign-up Password input")
        return self

    def enter_confirm_password(self, confirm_password: str) -> "SignUpPage":
        self.fill_locator(
            self._confirm_password_locator(),
            confirm_password,
            "Sign-up Confirm password input",
        )
        return self

    def click_create_account(self) -> None:
        self.click_locator(self.page.locator(self.create_account_button), "Create account button")

    def submit_registration(self, email: str, password: str, confirm_password: str | None = None) -> None:
        self.enter_email(email)
        self.enter_password(password)
        self.enter_confirm_password(password if confirm_password is None else confirm_password)
        self.click_create_account()

    def click_sign_in_link(self) -> None:
        self.click_locator(self.page.locator(self.sign_in_link), "Sign in link")
        self.wait_for_url(re.compile(r".*/sign-in($|\?.*)"))

    def get_heading_text(self) -> str:
        self.wait_for_visible(self._confirm_password_locator())
        heading = self.page.locator(self.page_heading).first
        self.wait_for_visible(heading)
        return heading.inner_text().strip()

    def is_create_account_enabled(self) -> bool:
        return self.page.locator(self.create_account_button).is_enabled()

    def get_password_rule_labels_visibility(self) -> dict[str, bool]:
        """Verify each password requirement rule label is rendered on the form."""
        labels = (
            self.password_rule_length_text,
            self.password_rule_case_text,
            self.password_rule_number_text,
            self.password_rule_symbol_text,
        )
        return {
            label: self.is_locator_visible(self.page.get_by_text(label, exact=False).first, timeout_ms=2000)
            for label in labels
        }

    def get_password_rule_item_state(self, rule_text: str) -> dict[str, str]:
        """Inspect DOM attributes and classes of a password requirement checklist item."""
        item = self.page.get_by_text(rule_text, exact=False).first
        self.wait_for_visible(item)
        return item.evaluate(
            """el => {
                const container = el.closest('li, div') || el;
                return {
                    className: container.className || '',
                    dataState: container.getAttribute('data-state') || container.getAttribute('data-met') || '',
                    ariaChecked: container.getAttribute('aria-checked') || '',
                    innerHtml: container.innerHTML || ''
                };
            }"""
        )

    def has_password_mismatch_indicator(self, timeout_ms: int = 3000) -> bool:
        return self.is_locator_visible(
            self.page.locator(self.mismatch_message_locator).first,
            timeout_ms=timeout_ms,
        )

    def wait_for_signup_error(self, timeout_ms: int = 8000) -> str:
        return self.wait_for_feedback_text(timeout_ms=timeout_ms)

    def wait_for_post_signup_outcome(self, timeout_ms: int = 12000) -> str:
        """Wait until either redirected away from /sign-up or feedback/status is rendered."""
        try:
            self.page.wait_for_url(re.compile(r".*/(app|sign-in|verify|onboarding).*"), timeout=timeout_ms)
            self.wait_for_loading_settled()
            return self.get_current_url()
        except Exception:
            return self.wait_for_feedback_text(timeout_ms=3000) or self.get_current_url()
