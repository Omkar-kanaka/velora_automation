"""Page Object for Velora Projects List screen (/app/projects)."""

import re

from pages.base_page import BasePage


class ProjectsPage(BasePage):
    """Encapsulates locators and actions for /app/projects (Rule 1.1)."""

    ROUTE: str = "/app/projects"

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    expected_heading_text = "Projects"
    sidebar_count_badge = '[data-slot="sidebar-menu-badge"]'
    main_container = "main"
    start_new_project_link_pattern = re.compile(r"Start a new project", re.IGNORECASE)
    empty_state_text = "No projects yet."

    def wait_until_loaded(self) -> None:
        self.wait_for_loading_settled()
        self.wait_for_visible(
            self.page.get_by_role("heading", name=self.expected_heading_text, level=1)
        )

    def open(self) -> "ProjectsPage":
        self.navigate_to(self.ROUTE)
        self.wait_until_loaded()
        return self

    def get_heading_text(self) -> str:
        self.wait_until_loaded()
        return self.page.locator(self.page_heading).first.inner_text().strip()

    def is_loaded(self) -> bool:
        return self.is_locator_visible(self.page.locator(self.page_heading).first)

    def is_empty_state_visible(self) -> bool:
        return self.is_locator_visible(self.page.get_by_text(self.empty_state_text).first, timeout_ms=3000)

    def click_start_new_project(self) -> None:
        link = self.page.get_by_role("link", name=self.start_new_project_link_pattern).first
        self.click_locator(link, "Start a new project link")
        self.wait_for_url(re.compile(r".*/app($|\?.*)"))

    def get_sidebar_project_count(self) -> int:
        """Read the integer project count shown on the sidebar 'All projects' badge."""
        badge = self.page.locator(self.sidebar_count_badge).first
        self.wait_for_visible(badge)
        raw = badge.inner_text().strip()
        return int(raw) if raw.isdigit() else 0

    def is_project_visible(self, project_name: str, timeout_ms: int = 6000) -> bool:
        return self.is_locator_visible(
            self.page.locator(self.main_container).get_by_text(project_name, exact=False).first,
            timeout_ms=timeout_ms,
        )

    def open_project_by_id(self, project_id: str) -> None:
        link = self.page.locator(f'{self.main_container} a[href="/app/projects/{project_id}"]').first
        self.click_locator(link, f"Project card link ({project_id})")
        self.wait_for_url(re.compile(rf".*/app/projects/{re.escape(project_id)}($|/.*)"))
