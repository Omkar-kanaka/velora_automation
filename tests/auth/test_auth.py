"""Authentication & Session Management Test Suite (AUTH-01 to AUTH-13)."""

import pytest

from config.config import UserCredentials
from pages.auth.forgot_password_page import ForgotPasswordPage
from pages.auth.sign_up_page import SignUpPage
from pages.auth.web_login_page import WebLoginPage
from pages.components.sidebar_component import SidebarComponent
from pages.dashboard_page import DashboardPage


@pytest.mark.smoke
@pytest.mark.auth
@pytest.mark.tc("AUTH-01")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_sign_in_with_valid_credentials_redirects_to_app(
    login_page: WebLoginPage,
    dashboard_page: DashboardPage,
    users: UserCredentials,
) -> None:
    """AUTH-01: Valid user signs in and lands on /app."""
    login_page.open()
    login_page.login_and_wait_for_app(users.email, users.password)

    assert "/app" in dashboard_page.get_current_url()
    assert dashboard_page.is_loaded()
    assert "What are you building?" in dashboard_page.get_heading_text()


@pytest.mark.smoke
@pytest.mark.auth
@pytest.mark.tc("AUTH-02")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_sign_out_clears_session_and_redirects_to_sign_in(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    login_page: WebLoginPage,
) -> None:
    """AUTH-02: Authenticated user signs out via sidebar menu and returns to /sign-in."""
    sidebar.click_sign_out(email=authenticated_user.email)

    assert "/sign-in" in login_page.get_current_url()
    assert login_page.is_sign_in_page_visible()


@pytest.mark.smoke
@pytest.mark.auth
@pytest.mark.security
@pytest.mark.tc("AUTH-03")
@pytest.mark.parametrize("protected_route", ["/app", "/app/projects", "/app/settings"])
def test_protected_routes_redirect_unauthenticated_user_to_sign_in(
    dashboard_page: DashboardPage,
    login_page: WebLoginPage,
    protected_route: str,
) -> None:
    """AUTH-03: Direct access to protected routes without auth redirects to /sign-in."""
    dashboard_page.open_protected_route(protected_route)
    login_page.wait_until_on_sign_in_page()

    assert "/sign-in" in login_page.get_current_url()
    assert login_page.is_sign_in_page_visible()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-04")
@pytest.mark.parametrize("users", ["invalid_password_user"], indirect=True)
def test_sign_in_with_wrong_password_displays_error(
    login_page: WebLoginPage,
    users: UserCredentials,
) -> None:
    """AUTH-04: Signing in with a valid email and wrong password fails with error feedback."""
    login_page.open()
    login_page.login(users.email, users.password)

    error_message = login_page.wait_for_auth_error_message()
    assert error_message != ""
    assert "/sign-in" in login_page.get_current_url()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-05")
@pytest.mark.parametrize("users", ["unregistered_user"], indirect=True)
def test_sign_in_with_unregistered_email_displays_error(
    login_page: WebLoginPage,
    users: UserCredentials,
) -> None:
    """AUTH-05: Signing in with an unregistered email fails with error feedback."""
    login_page.open()
    login_page.login(users.email, users.password)

    error_message = login_page.wait_for_auth_error_message()
    assert error_message != ""
    assert "/sign-in" in login_page.get_current_url()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-06")
@pytest.mark.parametrize(
    ("email_input", "password_input", "expected_invalid_field"),
    [
        ("", "", "email"),
        ("invalid-email-format", "SomePass@123", "email"),
        ("qa@example.com", "", "password"),
    ],
)
def test_sign_in_blocks_empty_and_invalid_email_submission(
    login_page: WebLoginPage,
    email_input: str,
    password_input: str,
    expected_invalid_field: str,
) -> None:
    """AUTH-06: Empty fields or malformed email prevent form submission."""
    login_page.open()
    if email_input:
        login_page.enter_email(email_input)
    if password_input:
        login_page.enter_password(password_input)
    login_page.click_sign_in()

    assert "/sign-in" in login_page.get_current_url()
    if expected_invalid_field == "email":
        assert login_page.get_email_validation_message() != ""
    else:
        assert login_page.get_password_validation_message() != ""


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.ui
@pytest.mark.tc("AUTH-07")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_password_visibility_toggle_switches_input_type(
    login_page: WebLoginPage,
    users: UserCredentials,
) -> None:
    """AUTH-07: Clicking Show/Hide toggles password input between 'password' and 'text'."""
    login_page.open()
    login_page.enter_password(users.password)

    assert login_page.get_password_input_type() == "password"

    login_page.toggle_password_visibility()
    assert login_page.get_password_input_type() == "text"

    login_page.toggle_password_visibility()
    assert login_page.get_password_input_type() == "password"


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-08")
def test_navigation_links_between_auth_screens(
    login_page: WebLoginPage,
    sign_up_page: SignUpPage,
    forgot_password_page: ForgotPasswordPage,
) -> None:
    """AUTH-08: Links cleanly navigate /sign-in -> /sign-up -> /sign-in -> /forgot-password -> /sign-in."""
    login_page.open()
    assert "Sign in" in login_page.get_heading_text()

    login_page.click_sign_up_link()
    assert "/sign-up" in sign_up_page.get_current_url()
    assert "Create your account" in sign_up_page.get_heading_text()

    sign_up_page.click_sign_in_link()
    login_page.wait_for_visible(login_page.page.locator(login_page.sign_in_button))
    assert "/sign-in" in login_page.get_current_url()

    login_page.click_forgot_password_link()
    forgot_password_page.wait_for_visible(forgot_password_page.page.locator(forgot_password_page.send_reset_link_button))
    assert "/forgot-password" in forgot_password_page.get_current_url()
    assert "Reset your password" in forgot_password_page.get_heading_text()

    forgot_password_page.click_back_to_sign_in()
    login_page.wait_for_visible(login_page.page.locator(login_page.sign_in_button))
    assert "/sign-in" in login_page.get_current_url()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-09")
@pytest.mark.parametrize("users", ["new_signup_user"], indirect=True)
def test_sign_up_with_valid_new_account_succeeds(
    sign_up_page: SignUpPage,
    users: UserCredentials,
) -> None:
    """AUTH-09: Registering a unique valid account succeeds and advances beyond /sign-up."""
    sign_up_page.open()
    sign_up_page.submit_registration(users.email, users.password)

    outcome = sign_up_page.wait_for_post_signup_outcome()
    assert outcome != ""
    assert "/sign-up" not in sign_up_page.get_current_url() or "account" in outcome.lower()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-10")
@pytest.mark.parametrize("users", ["duplicate_signup_user"], indirect=True)
def test_sign_up_with_existing_email_displays_error(
    sign_up_page: SignUpPage,
    users: UserCredentials,
) -> None:
    """AUTH-10: Registering an already existing email displays error feedback and stays on /sign-up."""
    sign_up_page.open()
    sign_up_page.submit_registration(users.email, users.password)

    error_message = sign_up_page.wait_for_signup_error()
    assert error_message != ""
    assert "/sign-up" in sign_up_page.get_current_url()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.ui
@pytest.mark.tc("AUTH-11")
@pytest.mark.parametrize("users", ["new_signup_user"], indirect=True)
def test_sign_up_password_rules_and_mismatch_validation(
    sign_up_page: SignUpPage,
    users: UserCredentials,
) -> None:
    """AUTH-11: Password checklist renders all 4 rules and reacts to weak vs strong/mismatched input."""
    sign_up_page.open()
    sign_up_page.enter_email(users.email)

    rule_visibility = sign_up_page.get_password_rule_labels_visibility()
    assert all(rule_visibility.values())

    # Weak password fails strength criteria
    sign_up_page.enter_password("weak")
    weak_length_state = sign_up_page.get_password_rule_item_state(sign_up_page.password_rule_length_text)

    # Strong password meets all criteria, but mismatched confirm password should block/flag mismatch
    sign_up_page.enter_password(users.password)
    strong_length_state = sign_up_page.get_password_rule_item_state(sign_up_page.password_rule_length_text)
    assert weak_length_state != strong_length_state

    sign_up_page.enter_confirm_password(f"{users.password}_different")
    mismatch_shown = sign_up_page.has_password_mismatch_indicator()
    submit_disabled = not sign_up_page.is_create_account_enabled()
    assert mismatch_shown or submit_disabled


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-12")
@pytest.mark.bug("VEL-025")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_forgot_password_submission_shows_confirmation_step(
    forgot_password_page: ForgotPasswordPage,
    users: UserCredentials,
) -> None:
    """AUTH-12 (VEL-025): Verify reset API returns 200 and Step 2 UI renders (email delivery tracked in VEL-025)."""
    forgot_password_page.open()
    api_status = forgot_password_page.request_password_reset_and_get_api_status(users.email)

    confirmation_text = forgot_password_page.get_confirmation_body_text()
    assert api_status == 200
    assert forgot_password_page.get_heading_text() == "Check your inbox"
    assert users.email in confirmation_text
    assert "If an account exists for this email" in confirmation_text
    assert forgot_password_page.is_change_email_button_visible()
    assert forgot_password_page.is_resend_link_button_visible()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-14")
@pytest.mark.bug("VEL-026")
@pytest.mark.parametrize(
    ("invalid_email", "expected_error"),
    [
        ("", "Enter your email."),
        ("not-an-email", "Enter a valid email address."),
    ],
)
def test_forgot_password_blocks_empty_and_malformed_email(
    forgot_password_page: ForgotPasswordPage,
    invalid_email: str,
    expected_error: str,
) -> None:
    """AUTH-14 (VEL-026): Empty or malformed email shows inline validation, stays on Step 1, and skips API call."""
    forgot_password_page.open()
    api_called = forgot_password_page.submit_invalid_email_and_check_api_called(invalid_email)

    assert not api_called
    assert forgot_password_page.get_heading_text() == "Reset your password"
    assert forgot_password_page.get_email_validation_message() == expected_error


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.security
@pytest.mark.tc("AUTH-15")
@pytest.mark.bug("VEL-026")
@pytest.mark.parametrize("users", ["unregistered_user"], indirect=True)
def test_forgot_password_unregistered_email_prevents_user_enumeration(
    forgot_password_page: ForgotPasswordPage,
    users: UserCredentials,
) -> None:
    """AUTH-15 (VEL-026): Unregistered valid email shows conditional OWASP Step 2 message without enumeration."""
    forgot_password_page.open()
    api_status = forgot_password_page.request_password_reset_and_get_api_status(users.email)

    confirmation_text = forgot_password_page.get_confirmation_body_text()
    assert api_status == 200
    assert forgot_password_page.get_heading_text() == "Check your inbox"
    assert "If an account exists for this email" in confirmation_text
    assert "not found" not in confirmation_text.lower()


@pytest.mark.regression
@pytest.mark.auth
@pytest.mark.tc("AUTH-13")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_authenticated_session_persists_across_page_reload(
    authenticated_user: UserCredentials,
    dashboard_page: DashboardPage,
    sidebar: SidebarComponent,
) -> None:
    """AUTH-13: Reloading /app retains the authenticated session without redirecting to /sign-in."""
    dashboard_page.reload_page()

    assert "/app" in dashboard_page.get_current_url()
    assert dashboard_page.is_loaded()
    assert sidebar.is_user_menu_visible(email=authenticated_user.email)
