"""Project 'New Run' Lifecycle & Composer Test Suite — RUN-NEW-01 through RUN-NEW-04."""

import uuid
from typing import Any, Callable

import pytest

from config.config import UserCredentials
from pages.components.sidebar_component import SidebarComponent
from pages.projects.meeting_notes_modal import MeetingNotesModal
from pages.projects.new_run_page import NewRunPage
from pages.projects.project_detail_page import ProjectDetailPage
from pages.projects_page import ProjectsPage


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.ui
@pytest.mark.tc("RUN-NEW-01")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_new_run_navigation_and_composer_layout(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
    project_detail_page: ProjectDetailPage,
    new_run_page: NewRunPage,
    managed_project: Callable[[str, str | None], dict[str, Any]],
    project_test_data: dict[str, Any],
) -> None:
    """RUN-NEW-01: Clicking 'New run' on Project Detail opens composer with 'What's changed in <project>?'."""
    unique_name = f"QA New Run {uuid.uuid4().hex[:6]}"
    created = managed_project(unique_name, "Project to test New run functionality")

    sidebar.wait_for_sidebar_ready()
    sidebar.click_all_projects()
    projects_page.reload_page()
    projects_page.wait_until_loaded()
    projects_page.open_project_by_id(created["id"])

    project_detail_page.wait_until_loaded(expected_project_name=unique_name)
    assert project_detail_page.is_new_run_button_visible(), "New run button must be visible in project header"
    assert project_detail_page.is_empty_runs_state_visible(), "Empty runs section should display 'No runs yet.'"
    assert project_detail_page.is_empty_runs_new_run_button_visible(), "Empty runs section should display 'New run' button"

    project_detail_page.click_new_run()
    new_run_page.wait_until_loaded(project_name=unique_name)

    # Verify heading and layout
    heading_text = new_run_page.get_heading_text()
    assert unique_name in heading_text, f"Expected project name '{unique_name}' in heading, got '{heading_text}'"
    assert project_test_data["new_run"]["expected_composer_heading_prefix"] in heading_text

    # Verify empty prompt disables the Start Run button
    assert new_run_page.is_start_run_button_disabled(), "Start Run button should be disabled when prompt is empty"


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.ui
@pytest.mark.tc("RUN-NEW-01B")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_empty_state_new_run_button_navigates_to_composer(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
    project_detail_page: ProjectDetailPage,
    new_run_page: NewRunPage,
    managed_project: Callable[[str, str | None], dict[str, Any]],
    project_test_data: dict[str, Any],
) -> None:
    """RUN-NEW-01B: Clicking the empty state 'No runs yet. [New run]' button opens the composer."""
    unique_name = f"QA Empty State {uuid.uuid4().hex[:6]}"
    created = managed_project(unique_name, "Project to test empty state New run button")

    sidebar.wait_for_sidebar_ready()
    sidebar.click_all_projects()
    projects_page.reload_page()
    projects_page.wait_until_loaded()
    projects_page.open_project_by_id(created["id"])

    project_detail_page.wait_until_loaded(expected_project_name=unique_name)
    assert project_detail_page.is_empty_runs_state_visible()
    assert project_detail_page.is_empty_runs_new_run_button_visible()

    project_detail_page.click_empty_state_new_run()
    new_run_page.wait_until_loaded(project_name=unique_name)

    heading_text = new_run_page.get_heading_text()
    assert unique_name in heading_text
    assert new_run_page.is_start_run_button_disabled()


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.ui
@pytest.mark.tc("RUN-NEW-02")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_new_run_prompt_entry_enables_start_run_button(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
    project_detail_page: ProjectDetailPage,
    new_run_page: NewRunPage,
    managed_project: Callable[[str, str | None], dict[str, Any]],
    project_test_data: dict[str, Any],
) -> None:
    """RUN-NEW-02: Typing prompt text enables 'Start Run <N>', clearing disables it."""
    unique_name = f"QA Prompt Run {uuid.uuid4().hex[:6]}"
    created = managed_project(unique_name, "Project to test prompt entry validation")

    sidebar.wait_for_sidebar_ready()
    sidebar.click_all_projects()
    projects_page.reload_page()
    projects_page.wait_until_loaded()
    projects_page.open_project_by_id(created["id"])

    project_detail_page.wait_until_loaded(expected_project_name=unique_name)
    project_detail_page.click_new_run()
    new_run_page.wait_until_loaded(project_name=unique_name)

    # Initial state: empty & disabled
    assert new_run_page.is_start_run_button_disabled()

    # Enter prompt: becomes enabled
    sample_prompt = project_test_data["new_run"]["sample_iteration_prompt"]
    new_run_page.enter_prompt(sample_prompt)
    assert new_run_page.get_prompt_value() == sample_prompt
    assert new_run_page.is_start_run_button_enabled(), "Start Run button should be enabled after entering prompt"

    # Clear prompt: becomes disabled again
    new_run_page.clear_prompt()
    assert new_run_page.is_start_run_button_disabled(), "Start Run button should be disabled after clearing prompt"


@pytest.mark.regression
@pytest.mark.projects
@pytest.mark.ui
@pytest.mark.tc("RUN-NEW-03")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_new_run_context_attachment_menu_options(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
    project_detail_page: ProjectDetailPage,
    new_run_page: NewRunPage,
    meeting_notes_modal: MeetingNotesModal,
    managed_project: Callable[[str, str | None], dict[str, Any]],
    project_test_data: dict[str, Any],
) -> None:
    """RUN-NEW-03: '+ Add notes, docs or code' menu allows attaching meeting notes to the new run."""
    unique_name = f"QA Context Run {uuid.uuid4().hex[:6]}"
    created = managed_project(unique_name, "Project to test context attachment on New Run")

    sidebar.wait_for_sidebar_ready()
    sidebar.click_all_projects()
    projects_page.reload_page()
    projects_page.wait_until_loaded()
    projects_page.open_project_by_id(created["id"])

    project_detail_page.wait_until_loaded(expected_project_name=unique_name)
    project_detail_page.click_new_run()
    new_run_page.wait_until_loaded(project_name=unique_name)

    # Attach meeting notes
    notes_cfg = project_test_data["meeting_notes"]
    new_run_page.open_meeting_notes_modal()
    meeting_notes_modal.enter_title(notes_cfg["title"])
    meeting_notes_modal.enter_notes(notes_cfg["body"])
    meeting_notes_modal.click_add_notes()

    # Verify notes chip is attached to composer
    assert new_run_page.is_context_item_visible(notes_cfg["title"]), (
        f"Context chip '{notes_cfg['title']}' should be attached to the new run composer"
    )
