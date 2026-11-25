"""Settings Configuration & Connectivity Test Suite (/app/settings) — SET-01 through SET-07."""

from typing import Any

import pytest

from config.config import UserCredentials, get_llm_api_key
from pages.settings_page import SettingsPage


@pytest.mark.smoke
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-01")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_settings_displays_database_ai_model_and_storage_sections(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-01: Settings page renders Database, AI model, and Storage sections with active status."""
    settings_page.open()

    assert settings_page.get_heading_text() == "Settings"
    assert settings_page.is_database_section_visible()
    assert settings_page.is_ai_model_section_visible()
    assert settings_page.is_storage_section_visible()
    assert settings_test_data["ai_model_expected_text"] in settings_page.get_ai_model_section_text()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-02")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_database_edit_form_expands_and_cancel_restores_summary(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-02: Expanding Database Edit form, modifying Port, and clicking Cancel keeps saved config intact."""
    settings_page.open()
    original_summary = settings_page.get_database_section_text()

    settings_page.open_database_edit_form()
    assert settings_page.is_database_edit_form_open()

    settings_page.enter_database_port(settings_test_data["database"]["temp_edit_port"])
    settings_page.cancel_database_edit_form()

    assert not settings_page.is_database_edit_form_open()
    assert settings_page.get_database_section_text() == original_summary


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-03")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_database_test_connection_returns_status_feedback(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-03: Database Test connection must strictly assert green 'Connection works.' feedback."""
    postgres_profile = next(
        p for p in settings_test_data["database_profiles"] if p["name"] == "PostgreSQL"
    )
    settings_page.open()
    settings_page.open_database_edit_form()

    try:
        settings_page.enter_database_password(postgres_profile["password"])
        status_code, payload, feedback_text = settings_page.test_database_connection()

        # Primary assertion: Strictly assert visible UI feedback text on the screen
        assert feedback_text == settings_test_data["database"]["expected_success_text"], (
            f"Test connection failed on UI! Expected '{settings_test_data['database']['expected_success_text']}', "
            f"but UI displayed: '{feedback_text}'"
        )
        assert status_code == 200, f"Expected HTTP 200 but received {status_code}"
        assert payload.get("ok") is True, f"Connection failed with payload error: {payload.get('error')}"
    finally:
        settings_page.cancel_database_edit_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-04")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_database_test_connection_fails_with_invalid_port_and_cancel_preserves_config(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-04: Unreachable DB port reports connection error and Cancel preserves original DB config."""
    db_data = settings_test_data["database"]
    settings_page.open()
    original_summary = settings_page.get_database_section_text()

    settings_page.open_database_edit_form()
    settings_page.enter_database_port(db_data["invalid_port"])
    status_code, payload, feedback_text = settings_page.test_database_connection()

    assert status_code == 200
    assert payload.get("ok") is False
    assert db_data["expected_unreachable_text"] in feedback_text
    assert db_data["invalid_port"] in feedback_text

    settings_page.cancel_database_edit_form()
    assert settings_page.get_database_section_text() == original_summary


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-05")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_storage_edit_form_expands_and_cancel_restores_summary(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-05: Expanding Storage Edit form, modifying Path, and clicking Cancel preserves saved path."""
    settings_page.open()
    original_summary = settings_page.get_storage_section_text()

    settings_page.open_storage_edit_form()
    assert settings_page.is_storage_edit_form_open()

    settings_page.enter_storage_path(settings_test_data["storage"]["temp_edit_path"])
    settings_page.cancel_storage_edit_form()

    assert not settings_page.is_storage_edit_form_open()
    assert settings_page.get_storage_section_text() == original_summary


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-06")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_storage_test_connection_succeeds_with_valid_local_path(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-06: Storage Test connection must strictly assert green 'Connection works.' feedback."""
    settings_page.open()
    settings_page.open_storage_edit_form()

    try:
        status_code, payload, feedback_text = settings_page.test_storage_connection()

        # Primary assertion: Strictly assert visible UI feedback text on the screen
        assert feedback_text == settings_test_data["storage"]["expected_success_text"], (
            f"Storage test connection failed on UI! Expected '{settings_test_data['storage']['expected_success_text']}', "
            f"but UI displayed: '{feedback_text}'"
        )
        assert status_code == 200, f"Expected HTTP 200 but received {status_code}"
        assert payload.get("ok") is True, f"Storage test failed with error: {payload.get('error')}"
    finally:
        settings_page.cancel_storage_edit_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-06b")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_storage_test_connection_succeeds_with_custom_valid_path(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-06b: Storage Test connection with custom valid path (C:\\QA) strictly asserts green 'Connection works.'."""
    storage_data = settings_test_data["storage"]
    settings_page.open()
    settings_page.open_storage_edit_form()

    try:
        settings_page.enter_storage_path(storage_data.get("valid_custom_path", "C:\\QA"))
        status_code, payload, feedback_text = settings_page.test_storage_connection()

        # Primary assertion: Strictly assert visible UI feedback text on the screen
        assert feedback_text == storage_data["expected_success_text"], (
            f"Storage test connection failed on UI! Expected '{storage_data['expected_success_text']}', "
            f"but UI displayed: '{feedback_text}'"
        )
        assert status_code == 200, f"Expected HTTP 200 but received {status_code}"
        assert payload.get("ok") is True, f"Storage test failed with error: {payload.get('error')}"
    finally:
        settings_page.cancel_storage_edit_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-07")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_storage_test_connection_fails_with_invalid_path_and_cancel_preserves_config(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-07: Non-existent storage path fails Test connection and Cancel preserves valid config."""
    storage_data = settings_test_data["storage"]
    settings_page.open()
    original_summary = settings_page.get_storage_section_text()

    settings_page.open_storage_edit_form()
    try:
        settings_page.enter_storage_path(storage_data["invalid_path"])
        status_code, payload, feedback_text = settings_page.test_storage_connection()

        assert status_code == 200
        assert payload.get("ok") is False
        assert storage_data["expected_invalid_text"] in feedback_text
    finally:
        settings_page.cancel_storage_edit_form()

    assert settings_page.get_storage_section_text() == original_summary


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-07b")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_storage_path_validation_rejects_non_absolute_path(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-07b: Entering non-absolute path displays 'Use an absolute path.' validation error."""
    storage_data = settings_test_data["storage"]
    settings_page.open()
    settings_page.open_storage_edit_form()

    try:
        settings_page.enter_storage_path(storage_data.get("malformed_path", "Z:hsdb/sddf/sdvsc"))
        settings_page.click_storage_test_connection_button()
        error_text = settings_page.get_storage_field_error_text()
        assert storage_data.get("expected_malformed_text", "Use an absolute path.") in error_text
    finally:
        settings_page.cancel_storage_edit_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-08")
@pytest.mark.parametrize(
    "profile_name",
    ["PostgreSQL", "MySQL", "SQL Server", "Oracle"],
)
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_settings_database_connectivity_across_profiles(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
    profile_name: str,
) -> None:
    """SET-08: Database connectivity testing across Docker profiles (PostgreSQL, MySQL, SQL Server, Oracle)."""
    profile = next(
        p for p in settings_test_data["database_profiles"] if p["name"] == profile_name
    )
    settings_page.open()
    settings_page.open_database_edit_form()
    try:
        settings_page.fill_database_form(profile)
        status_code, payload, feedback_text = settings_page.test_database_connection()

        # Primary assertion: Strictly assert the UI text visible to the user on the screen
        assert feedback_text == profile["expected_feedback"], (
            f"Database '{profile_name}' test connection failed on UI! "
            f"Expected '{profile['expected_feedback']}', but UI displayed: '{feedback_text}'"
        )

        # Secondary API assertion
        assert status_code == 200, f"Expected HTTP 200 but received {status_code}"
        assert payload.get("ok") is True, (
            f"API returned error for '{profile_name}': {payload.get('error')}"
        )
    finally:
        settings_page.cancel_database_edit_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-09")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_database_configuration_cancel_preserves_baseline_config(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-09: Modifying database configuration and clicking Cancel discards edits and preserves baseline PostgreSQL."""
    mysql_profile = next(
        p for p in settings_test_data["database_profiles"] if p["name"] == "MySQL"
    )
    settings_page.open()
    baseline_summary = settings_page.get_database_header_summary()
    assert "PostgreSQL" in baseline_summary

    settings_page.open_database_edit_form()
    baseline_port = settings_page.get_database_port_value()
    assert baseline_port == "5432"

    try:
        settings_page.fill_database_form(mysql_profile)
        assert settings_page.get_database_port_value() == "3306"
        settings_page.cancel_database_edit_form()

        assert not settings_page.is_database_edit_form_open()
        assert settings_page.get_database_header_summary() == baseline_summary

        # Reopen to verify values were reset and not persisted in memory/form
        settings_page.open_database_edit_form()
        assert settings_page.get_database_port_value() == baseline_port
    finally:
        settings_page.cancel_database_edit_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-10")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_database_test_connection_rejects_invalid_credentials(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-10: Database test connection with incorrect password reports credential rejection error."""
    postgres_profile = next(
        p for p in settings_test_data["database_profiles"] if p["name"] == "PostgreSQL"
    )
    invalid_cred_profile = dict(postgres_profile)
    invalid_cred_profile["password"] = "Invalid_Pass_999!"

    settings_page.open()
    settings_page.open_database_edit_form()
    try:
        settings_page.fill_database_form(invalid_cred_profile)
        status_code, payload, feedback_text = settings_page.test_database_connection()

        assert status_code == 200
        assert payload.get("ok") is False
        assert (
            settings_test_data["database"]["expected_rejected_credentials_text"] in feedback_text
            or "rejected" in feedback_text.lower()
            or "password" in feedback_text.lower()
        )
    finally:
        settings_page.cancel_database_edit_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-11")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_ai_model_edit_form_expands_and_cancel_restores_summary(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-11: Expanding AI Model Edit form, verifying masked API key, and clicking Cancel preserves saved config."""
    settings_page.open()
    original_summary = settings_page.get_ai_model_header_summary()

    settings_page.open_ai_model_edit_form()
    assert settings_page.is_ai_model_edit_form_open(), "AI Model edit form did not open"
    assert settings_page.is_ai_api_key_masked(), "AI API key field must be masked (type='password')"

    settings_page.cancel_ai_model_form()
    assert not settings_page.is_ai_model_edit_form_open(), "AI Model edit form did not close after Cancel"
    assert settings_page.get_ai_model_header_summary() == original_summary


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-12")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_ai_model_dropdown_options_match_expected_providers(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-12: AI Model provider dropdown contains all supported providers."""
    expected_providers = settings_test_data["ai_model"]["all_provider_options"]
    settings_page.open()
    settings_page.open_ai_model_edit_form()

    try:
        available_options = settings_page.get_ai_provider_options()
        for expected in expected_providers:
            assert any(expected.lower() in opt.lower() for opt in available_options), (
                f"Expected provider '{expected}' not found in available options: {available_options}"
            )
    finally:
        settings_page.cancel_ai_model_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-13")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_ai_model_test_connection_fails_with_invalid_api_key(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-13: AI Model Test connection with an invalid API key displays an error feedback message."""
    ai_data = settings_test_data["ai_model"]
    settings_page.open()
    settings_page.open_ai_model_edit_form()

    try:
        settings_page.enter_ai_api_key(ai_data["invalid_api_key"])
        status_code, payload, feedback_text = settings_page.test_ai_model_connection()

        # The backend should report failure for invalid key
        assert feedback_text != ai_data["expected_success_feedback"], (
            f"Expected error feedback for invalid API key, but received success: '{feedback_text}'"
        )
        assert len(feedback_text) > 0, "Expected non-empty failure feedback message on UI"
    finally:
        settings_page.cancel_ai_model_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.tc("SET-14")
@pytest.mark.parametrize(
    "profile_name",
    ["Other (LiteLLM)", "Gemini", "OpenAI", "OpenRouter"],
)
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_ai_model_connectivity_across_configured_providers(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
    profile_name: str,
) -> None:
    """SET-14: Test connection for configured AI model providers using API keys from .env."""
    ai_data = settings_test_data["ai_model"]
    profile = next((p for p in ai_data["profiles"] if p["name"] == profile_name), None)
    if not profile:
        pytest.skip(f"No profile defined for '{profile_name}'")

    api_key = get_llm_api_key(profile["env_key"])

    if not api_key:
        pytest.skip(
            f"Skipping '{profile_name}': No API key configured in .env for '{profile['env_key']}'"
        )

    settings_page.open()
    settings_page.open_ai_model_edit_form()
    try:
        settings_page.fill_ai_model_form(profile, api_key=api_key)
        status_code, payload, feedback_text = settings_page.test_ai_model_connection()

        # Primary assertion: Strictly assert the UI text visible to the user on the screen
        assert feedback_text == ai_data["expected_success_feedback"], (
            f"AI Model '{profile_name}' test connection failed on UI! "
            f"Expected '{ai_data['expected_success_feedback']}', but UI displayed: '{feedback_text}'"
        )
        assert status_code == 200, f"Expected HTTP 200 but received {status_code}"
        assert payload.get("ok") is True, f"API returned error: {payload.get('error')}"
    finally:
        settings_page.cancel_ai_model_form()


@pytest.mark.regression
@pytest.mark.settings
@pytest.mark.ui
@pytest.mark.tc("SET-15")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_ai_model_cancel_preserves_baseline_config(
    authenticated_user: UserCredentials,
    settings_page: SettingsPage,
    settings_test_data: dict[str, Any],
) -> None:
    """SET-15: Modifying AI model form fields and clicking Cancel discards changes and preserves baseline summary."""
    settings_page.open()
    baseline_summary = settings_page.get_ai_model_header_summary()

    settings_page.open_ai_model_edit_form()
    try:
        settings_page.select_ai_provider("Gemini (API key)")
        settings_page.enter_ai_model("gemini-1.5-pro")
        settings_page.cancel_ai_model_form()

        assert not settings_page.is_ai_model_edit_form_open()
        assert settings_page.get_ai_model_header_summary() == baseline_summary
    finally:
        if settings_page.is_ai_model_edit_form_open():
            settings_page.cancel_ai_model_form()

