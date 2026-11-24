"""New Project & Context Inputs Test Suite (/app) — PROJ-01 through PROJ-12."""

import time
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
def test_add_public_repository_full_workflow_to_start_answering(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    repository_modal: RepositoryModal,
    project_test_data: dict[str, Any],
    track_and_cleanup_project: Any,
) -> None:
    """PROJ-06: Add repository, configure timeline, settle kickoff checklist, verify 'Start answering' enables."""
    repo = project_test_data["repository"]
    new_project_page.open()
    new_project_page.wait_until_loaded()
    new_project_page.open_repository_modal()

    # Step 1: Add repository
    repository_modal.add_public_repository(url=repo["valid_url"], branch=repo["valid_branch"])
    assert not repository_modal.is_open()
    assert new_project_page.is_context_item_visible(repo["expected_chip_text"])
    assert new_project_page.is_start_button_enabled()

    # Step 2: Click Start -> Step 2
    new_project_page.click_start()
    new_project_page.wait_for_step_two_loaded()

    # Step 3: Enter project name & timeline end date
    unique_name = f"Repo Full Flow {int(time.time())}"
    new_project_page.enter_project_name(unique_name)
    new_project_page.select_end_date()
    assert new_project_page.is_start_run_button_enabled()

    # Step 4: Click Next / Start the run
    new_project_page.click_start_the_run()

    # Guaranteed cleanup tracking immediately after run creation
    created_id = new_project_page.get_created_project_id(unique_name)
    if created_id:
        track_and_cleanup_project(created_id)

    # Step 5: Check all checklist steps are done and 'Start answering' enables
    new_project_page.wait_for_getting_it_ready_settled(timeout_ms=60000)
    assert new_project_page.is_kickoff_step_visible("Set up the project")
    assert new_project_page.is_kickoff_step_visible("Preparing your first question")
    assert new_project_page.is_start_answering_visible()
    assert new_project_page.is_start_answering_enabled()


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
@pytest.mark.tc("PROJ-07-MISSING-TOKEN")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_repository_private_missing_token_blocks_submission_and_cancel_discards(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    repository_modal: RepositoryModal,
    project_test_data: dict[str, Any],
) -> None:
    """PROJ-07-MISSING-TOKEN: Submitting a private repository with empty token keeps modal open."""
    repo = project_test_data["repository"]
    new_project_page.wait_until_loaded()
    new_project_page.open_repository_modal()
    repository_modal.wait_until_open()

    # Select private repo and fill valid URL, but leave token blank
    repository_modal.select_private()
    repository_modal.enter_repository_link(repo["valid_url"])
    repository_modal.enter_branch(repo["valid_branch"])
    assert repository_modal.get_access_token_value() == ""

    # Attempt submission with empty token
    repository_modal.click_add_repository(expect_close=False)

    # Validate modal remains open and no repo chip attached
    assert repository_modal.is_open(), "Modal closed unexpectedly without a token."
    repository_modal.click_cancel()
    assert not repository_modal.is_open()
    assert not new_project_page.is_context_item_visible(repo["expected_chip_text"])
    assert new_project_page.is_start_button_disabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-07-INVALID-TOKEN")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_repository_private_invalid_token_blocks_successful_run(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    repository_modal: RepositoryModal,
    project_test_data: dict[str, Any],
    track_and_cleanup_project: Any,
) -> None:
    """PROJ-07-INVALID-TOKEN: Private repo with invalid token fails analysis, shows clone error, and blocks 'Start answering'."""
    repo = project_test_data["repository"]
    private_cfg = repo.get("private_repository", {})
    invalid_token = private_cfg.get("invalid_token", "invalid_access_token_xyz999")

    new_project_page.open()
    new_project_page.wait_until_loaded()
    new_project_page.open_repository_modal()
    repository_modal.wait_until_open()

    # Step 1: Add private repo with invalid token
    repository_modal.select_private()
    repository_modal.enter_repository_link(private_cfg.get("valid_url", repo["valid_url"]))
    repository_modal.enter_branch(private_cfg.get("valid_branch", repo["valid_branch"]))
    repository_modal.enter_access_token(invalid_token)
    repository_modal.click_add_repository(expect_close=True)

    # Step 2: Attempt to start project
    new_project_page.click_start()
    new_project_page.wait_for_step_two_loaded()

    unique_name = f"Invalid Token {int(time.time())}"
    new_project_page.enter_project_name(unique_name)
    new_project_page.select_end_date()
    new_project_page.click_start_the_run()

    # Guaranteed cleanup
    created_id = new_project_page.get_created_project_id(unique_name)
    if created_id:
        track_and_cleanup_project(created_id)

    # Step 3: Verify that invalid token displays clone error and blocks 'Start answering'
    assert new_project_page.is_kickoff_clone_error_visible(timeout_ms=30000)
    error_msg = new_project_page.get_kickoff_clone_error_text()
    assert "Could not clone that repository" in error_msg
    assert new_project_page.is_edit_sources_button_visible()
    assert not new_project_page.is_start_answering_visible(timeout_ms=3000)


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.tc("PROJ-07-VALID-TOKEN")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_repository_private_valid_token_full_workflow_to_start_answering(
    authenticated_user: UserCredentials,
    new_project_page: NewProjectPage,
    repository_modal: RepositoryModal,
    project_test_data: dict[str, Any],
    track_and_cleanup_project: Any,
) -> None:
    """PROJ-07-VALID-TOKEN: Private repository with valid PAT token passes kickoff and enables 'Start answering'."""
    repo = project_test_data["repository"]
    private_cfg = repo.get("private_repository", {})

    new_project_page.open()
    new_project_page.wait_until_loaded()
    new_project_page.open_repository_modal()
    repository_modal.wait_until_open()

    # Step 1: Add private repo with valid token
    repository_modal.select_private()
    repository_modal.enter_repository_link(private_cfg.get("valid_url", repo["valid_url"]))
    repository_modal.enter_branch(private_cfg.get("valid_branch", "main"))
    repository_modal.enter_access_token(private_cfg["valid_token"])
    repository_modal.click_add_repository(expect_close=True)

    assert not repository_modal.is_open()
    assert new_project_page.is_context_item_visible(private_cfg.get("expected_chip_text", "private-crm-testing"))
    assert new_project_page.is_start_button_enabled()

    # Step 2: Click Start -> Step 2
    new_project_page.click_start()
    new_project_page.wait_for_step_two_loaded()

    # Step 3: Enter project name & timeline end date
    unique_name = f"Private Valid {int(time.time())}"
    new_project_page.enter_project_name(unique_name)
    new_project_page.select_end_date()
    assert new_project_page.is_start_run_button_enabled()

    # Step 4: Click Next / Start the run
    new_project_page.click_start_the_run()

    # Guaranteed cleanup tracking immediately after run creation
    created_id = new_project_page.get_created_project_id(unique_name)
    if created_id:
        track_and_cleanup_project(created_id)

    # Step 5: Check all checklist steps are done and 'Start answering' enables
    new_project_page.wait_for_getting_it_ready_settled(timeout_ms=60000)
    assert new_project_page.is_kickoff_step_visible("Set up the project")
    assert new_project_page.is_kickoff_step_visible("Preparing your first question")
    assert new_project_page.is_start_answering_visible()
    assert new_project_page.is_start_answering_enabled()


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
