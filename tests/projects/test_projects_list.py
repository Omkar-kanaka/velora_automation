"""Projects List & Project Detail Test Suite (/app/projects) — LIST-01 through LIST-03."""

import uuid
from typing import Any, Callable

import pytest

from config.config import UserCredentials
from pages.auth.sign_up_page import SignUpPage
from pages.components.sidebar_component import SidebarComponent
from pages.dashboard_page import DashboardPage
from pages.projects.project_detail_page import ProjectDetailPage
from pages.projects_page import ProjectsPage


@pytest.mark.regression
@pytest.mark.projects_list
@pytest.mark.ui
@pytest.mark.tc("LIST-01")
@pytest.mark.parametrize("users", ["new_signup_user"], indirect=True)
def test_projects_empty_state_and_start_cta_for_new_account(
    sign_up_page: SignUpPage,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
    dashboard_page: DashboardPage,
    users: UserCredentials,
) -> None:
    """LIST-01: Fresh account with no projects sees empty state and Start a new project CTA navigates to /app."""
    sign_up_page.open()
    sign_up_page.submit_registration(users.email, users.password)
    sign_up_page.wait_for_post_signup_outcome()

    sidebar.wait_for_sidebar_ready()
    sidebar.click_all_projects()
    projects_page.wait_until_loaded()

    assert projects_page.get_heading_text() == "Projects"
    assert projects_page.get_sidebar_project_count() == 0
    assert projects_page.is_empty_state_visible()

    projects_page.click_start_new_project()
    assert "/app" in dashboard_page.get_current_url()
    assert dashboard_page.is_loaded()


@pytest.mark.smoke
@pytest.mark.projects_list
@pytest.mark.tc("LIST-02")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_newly_created_project_appears_in_list_and_increments_sidebar_badge(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
    managed_project: Callable[[str, str | None], dict[str, Any]],
) -> None:
    """LIST-02: Creating a project increments sidebar All projects badge and renders it on /app/projects."""
    sidebar.wait_for_sidebar_ready()
    sidebar.click_all_projects()
    projects_page.wait_until_loaded()

    initial_count = projects_page.get_sidebar_project_count()
    unique_name = f"QA List Smoke {uuid.uuid4().hex[:6]}"
    managed_project(unique_name, "Automated verification project for LIST-02")

    projects_page.reload_page()
    projects_page.wait_until_loaded()

    assert projects_page.get_sidebar_project_count() == initial_count + 1
    assert projects_page.is_project_visible(unique_name)


@pytest.mark.regression
@pytest.mark.projects_list
@pytest.mark.tc("LIST-03")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_opening_existing_project_navigates_to_project_detail(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
    project_detail_page: ProjectDetailPage,
    managed_project: Callable[[str, str | None], dict[str, Any]],
) -> None:
    """LIST-03: Clicking an existing project on /app/projects opens its detail view with saved metadata."""
    sidebar.wait_for_sidebar_ready()
    unique_name = f"QA Detail View {uuid.uuid4().hex[:6]}"
    created = managed_project(unique_name, "Automated verification project for LIST-03")

    sidebar.click_all_projects()
    projects_page.reload_page()
    projects_page.wait_until_loaded()
    assert projects_page.is_project_visible(unique_name)

    projects_page.open_project_by_id(created["id"])
    project_detail_page.wait_until_loaded(expected_project_name=unique_name)

    assert created["id"] in project_detail_page.get_current_url()
    assert project_detail_page.get_heading_text() == unique_name
    assert "Draft" in project_detail_page.get_main_content_text()
    assert project_detail_page.is_new_run_button_visible()
    assert project_detail_page.is_delete_project_button_visible()
