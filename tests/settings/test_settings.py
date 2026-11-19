"""Settings Configuration & Connectivity Test Suite (/app/settings) — SET-01 through SET-07."""

from typing import Any

import pytest

from config.config import UserCredentials
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
    """SET-03: Database Test connection calls backend test endpoint and displays matching UI feedback."""
    settings_page.open()
    settings_page.open_database_edit_form()

    status_code, payload, feedback_text = settings_page.test_database_connection()
    settings_page.cancel_database_edit_form()

    assert status_code == 200
    assert "ok" in payload
    if payload["ok"]:
        assert settings_test_data["database"]["expected_success_text"] in feedback_text
    else:
        assert payload.get("error", "") in feedback_text
        assert feedback_text != ""


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
    """SET-06: Storage Test connection succeeds for the active local folder path."""
    settings_page.open()
    settings_page.open_storage_edit_form()

    status_code, payload, feedback_text = settings_page.test_storage_connection()
    settings_page.cancel_storage_edit_form()

    assert status_code == 200
    assert payload.get("ok") is True
    assert settings_test_data["storage"]["expected_success_text"] in feedback_text


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
    settings_page.enter_storage_path(storage_data["invalid_path"])
    status_code, payload, feedback_text = settings_page.test_storage_connection()

    assert status_code == 200
    assert payload.get("ok") is False
    assert storage_data["expected_invalid_text"] in feedback_text

    settings_page.cancel_storage_edit_form()
    assert settings_page.get_storage_section_text() == original_summary


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

        assert status_code == 200
        assert "ok" in payload
        if profile["expected_success"]:
            assert payload["ok"] is True
            assert profile["expected_feedback"] in feedback_text
        else:
            assert payload["ok"] is False
            assert profile["expected_feedback"] in feedback_text
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
