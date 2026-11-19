"""Navigation & Application Shell Test Suite (NAV-01, NAV-02)."""

import pytest

from config.config import UserCredentials
from core.factories.driver_factory import BrowserSession
from pages.components.sidebar_component import SidebarComponent
from pages.dashboard_page import DashboardPage
from pages.projects_page import ProjectsPage
from pages.settings_page import SettingsPage


@pytest.mark.smoke
@pytest.mark.nav
@pytest.mark.tc("NAV-01")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_sidebar_navigates_across_primary_sections_without_errors(
    authenticated_user: UserCredentials,
    browser_session: BrowserSession,
    sidebar: SidebarComponent,
    dashboard_page: DashboardPage,
    projects_page: ProjectsPage,
    settings_page: SettingsPage,
) -> None:
    """NAV-01: Navigate /app -> /app/projects -> /app/settings -> /app via sidebar cleanly."""
    sidebar.wait_for_sidebar_ready()
    assert "What are you building?" in dashboard_page.get_heading_text()

    sidebar.click_all_projects()
    assert "/app/projects" in projects_page.get_current_url()
    assert projects_page.get_heading_text() == "Projects"

    sidebar.click_settings(email=authenticated_user.email)
    assert "/app/settings" in settings_page.get_current_url()
    assert settings_page.get_heading_text() == "Settings"

    sidebar.click_new_project()
    assert "/app" in dashboard_page.get_current_url()
    assert dashboard_page.is_loaded()
    assert "What are you building?" in dashboard_page.get_heading_text()

    page_errors = [entry for entry in browser_session.console_logs if entry.startswith("[pageerror]")]
    assert page_errors == []


@pytest.mark.regression
@pytest.mark.nav
@pytest.mark.ui
@pytest.mark.tc("NAV-02")
@pytest.mark.parametrize("users", ["valid_user"], indirect=True)
def test_sidebar_collapse_and_expand_via_button_and_shortcut(
    authenticated_user: UserCredentials,
    sidebar: SidebarComponent,
    projects_page: ProjectsPage,
) -> None:
    """NAV-02: Sidebar collapses and expands via toggle buttons and Ctrl+B, keeping nav usable."""
    sidebar.wait_for_sidebar_ready()
    assert sidebar.get_sidebar_state() == "expanded"

    # Toggle via UI buttons
    sidebar.collapse_sidebar_via_button()
    assert sidebar.get_sidebar_state() == "collapsed"

    sidebar.expand_sidebar_via_button()
    assert sidebar.get_sidebar_state() == "expanded"

    # Toggle via keyboard shortcut (Ctrl+B)
    assert sidebar.toggle_sidebar_via_shortcut() == "collapsed"
    assert sidebar.get_sidebar_state() == "collapsed"

    assert sidebar.toggle_sidebar_via_shortcut() == "expanded"
    assert sidebar.get_sidebar_state() == "expanded"

    # Confirm navigation still works cleanly after toggling
    sidebar.click_all_projects()
    assert projects_page.get_heading_text() == "Projects"
