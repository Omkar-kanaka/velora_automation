"""New Project & Context Inputs Test Suite (/app) — PROJ-01 through PROJ-12."""

from typing import Any

import pytest

from config.config import UserCredentials
from pages.projects.meeting_notes_modal import MeetingNotesModal
from pages.projects.new_project_page import NewProjectPage
from pages.projects.repository_modal import RepositoryModal
from utils.paths import TESTDATA_FILES_DIR, TESTDATA_FRD_DIR


@pytest.mark.smoke
@pytest.mark.projects
@pytest.mark.ui
@pytest.mark.tc("PROJ-01")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_start_button_state_follows_prompt_input(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-01: Start button is disabled when empty, enabled on text input, disabled when cleared."""
    new_project_page.wait_until_loaded()
    assert new_project_page.is_start_button_disabled()

    new_project_page.enter_prompt(project_test_data["sample_prompt"])
    assert new_project_page.is_start_button_enabled()

    new_project_page.clear_prompt()
    assert new_project_page.is_start_button_disabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-02")
@pytest.mark.parametrize(
    "example_name",
    [
        "Quick product discovery",
        "Partner self-serve onboarding",
        "Fix duplicate order emails",
    ],
)
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_example_prompt_populates_textarea_and_enables_start(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    example_name: str,
) -> None:
    """PROJ-02: Clicking an example prompt populates the composer and enables Start."""
    new_project_page.wait_until_loaded()
    new_project_page.click_example_prompt(example_name)

    assert new_project_page.get_prompt_value().strip() != ""
    assert new_project_page.is_start_button_enabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-03")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_add_meeting_notes_attaches_context_chip(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    meeting_notes_modal: MeetingNotesModal,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-03: Adding meeting notes closes the modal, attaches NOTES context, and enables Start."""
    notes = project_test_data["meeting_notes"]
    new_project_page.wait_until_loaded()
    new_project_page.open_meeting_notes_modal()

    meeting_notes_modal.add_meeting_notes(title=notes["title"], notes=notes["body"])

    assert not meeting_notes_modal.is_open()
    assert new_project_page.is_context_item_visible(notes["title"])
    assert new_project_page.is_start_button_enabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.ui
@pytest.mark.tc("PROJ-04")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_cancel_meeting_notes_modal_discards_input(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    meeting_notes_modal: MeetingNotesModal,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-04: Clicking Cancel closes meeting notes modal without attaching any context."""
    notes = project_test_data["meeting_notes"]
    new_project_page.wait_until_loaded()
    new_project_page.open_meeting_notes_modal()

    meeting_notes_modal.wait_until_open()
    meeting_notes_modal.enter_title(notes["title"])
    meeting_notes_modal.enter_notes(notes["body"])
    meeting_notes_modal.click_cancel()

    assert not meeting_notes_modal.is_open()
    assert not new_project_page.is_context_item_visible(notes["title"], timeout_ms=1000)
    assert new_project_page.is_start_button_disabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-05")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_empty_meeting_notes_keeps_submit_disabled(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    meeting_notes_modal: MeetingNotesModal,
) -> None:
    """PROJ-05: Add notes submit button remains disabled when meeting notes content is empty."""
    new_project_page.wait_until_loaded()
    new_project_page.open_meeting_notes_modal()
    meeting_notes_modal.wait_until_open()

    assert not meeting_notes_modal.is_add_notes_enabled()
    meeting_notes_modal.click_cancel()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-06")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_add_public_repository_attaches_context_chip(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    repository_modal: RepositoryModal,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-06: Adding a valid public repository closes modal and attaches REPO chip."""
    repo = project_test_data["repository"]
    new_project_page.wait_until_loaded()
    new_project_page.open_repository_modal()

    repository_modal.add_public_repository(url=repo["valid_url"], branch=repo["valid_branch"])

    assert not repository_modal.is_open()
    assert new_project_page.is_context_item_visible(repo["expected_chip_text"])
    assert new_project_page.is_start_button_enabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.ui
@pytest.mark.tc("PROJ-07")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_repository_private_radio_reveals_access_token_field(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    repository_modal: RepositoryModal,
) -> None:
    """PROJ-07: Selecting Private reveals the Access token input; switching back to Public hides it."""
    new_project_page.wait_until_loaded()
    new_project_page.open_repository_modal()
    repository_modal.wait_until_open()

    assert repository_modal.is_public_selected()
    assert not repository_modal.is_access_token_visible(timeout_ms=1000)

    repository_modal.select_private()
    assert repository_modal.is_private_selected()
    assert repository_modal.is_access_token_visible()

    repository_modal.select_public()
    assert repository_modal.is_public_selected()
    assert not repository_modal.is_access_token_visible(timeout_ms=1000)
    repository_modal.click_cancel()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-08")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_repository_invalid_url_shows_validation_and_cancel_discards(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    repository_modal: RepositoryModal,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-08: Invalid repository URL keeps modal open with validation error; Cancel discards."""
    repo = project_test_data["repository"]
    new_project_page.wait_until_loaded()
    new_project_page.open_repository_modal()
    repository_modal.wait_until_open()

    repository_modal.enter_repository_link(repo["invalid_url"])
    repository_modal.click_add_repository(expect_close=False)

    assert repository_modal.is_open()
    assert repo["expected_invalid_message"] in repository_modal.get_dialog_text()

    repository_modal.click_cancel()
    assert not repository_modal.is_open()
    assert new_project_page.is_start_button_disabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-09")
@pytest.mark.parametrize(
    "frd_filename",
    [
        "Test_frd.md",
        "Test_Hospital_Management_System_FRD (1).pdf",
        "Test_Hospital_Management_System_FRD.docx",
    ],
)
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_upload_valid_frd_documents_attaches_context(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    frd_filename: str,
) -> None:
    """PROJ-09: Uploading valid .md, .pdf, and .docx FRD files attaches DOC context and enables Start."""
    frd_path = TESTDATA_FRD_DIR / frd_filename
    assert frd_path.exists()

    new_project_page.wait_until_loaded()
    new_project_page.upload_document(frd_path)

    assert new_project_page.is_context_item_visible(frd_filename)
    assert new_project_page.is_start_button_enabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-10")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_upload_unsupported_file_format_displays_error_alert(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-10: Uploading an unsupported file format displays an error alert and rejects attachment."""
    uploads = project_test_data["uploads"]
    invalid_file_path = TESTDATA_FILES_DIR / uploads["invalid_filename"]
    assert invalid_file_path.exists()

    new_project_page.wait_until_loaded()
    new_project_page.upload_document(invalid_file_path)

    alert_text = new_project_page.get_upload_alert_text()
    assert uploads["expected_invalid_alert"] in alert_text
    assert not new_project_page.is_context_item_visible(uploads["invalid_filename"], timeout_ms=1000)


@pytest.mark.smoke
@pytest.mark.projects
@pytest.mark.tc("PROJ-11")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_start_project_with_prompt_opens_run_setup_step(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-11: Entering a prompt and clicking Start opens Step 2 run setup with Timeline & Start the run."""
    prompt = project_test_data["sample_prompt"]
    new_project_page.wait_until_loaded()
    new_project_page.enter_prompt(prompt)
    new_project_page.click_start()

    step_two_text = new_project_page.get_main_content_text()
    assert prompt in step_two_text
    assert "Timeline" in step_two_text
    assert new_project_page.is_start_run_button_visible()
    assert new_project_page.is_start_run_button_disabled()

    new_project_page.enter_project_name(project_test_data["sample_project_name"])
    assert new_project_page.is_start_run_button_disabled()

    new_project_page.select_end_date()
    assert new_project_page.is_start_run_button_enabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-12")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_start_project_with_prompt_and_attached_context_preserves_state(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    meeting_notes_modal: MeetingNotesModal,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-12: Combining prompt + meeting notes + FRD doc advances to Step 2 and Back restores composer."""
    prompt = project_test_data["sample_prompt"]
    notes = project_test_data["meeting_notes"]
    frd_name = project_test_data["uploads"]["primary_frd_file"]
    frd_path = TESTDATA_FRD_DIR / frd_name

    new_project_page.wait_until_loaded()
    new_project_page.open_meeting_notes_modal()
    meeting_notes_modal.add_meeting_notes(title=notes["title"], notes=notes["body"])
    new_project_page.upload_document(frd_path)
    new_project_page.enter_prompt(prompt)

    new_project_page.click_start()
    step_two_text = new_project_page.get_main_content_text()
    assert prompt in step_two_text
    assert new_project_page.is_start_run_button_visible()

    new_project_page.click_back_to_composer()
    assert new_project_page.get_prompt_value() == prompt
    assert new_project_page.is_context_item_visible(notes["title"])
    assert new_project_page.is_context_item_visible(frd_name)
