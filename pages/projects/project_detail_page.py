"""Page Object for Velora Project Detail screen (/app/projects/<id>)."""

import re

from pages.base_page import BasePage


class ProjectDetailPage(BasePage):
    """Encapsulates locators and queries for /app/projects/<id> (Rule 1.1)."""

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    main_container = "main"
    new_run_link_name = "New run"
    delete_project_button_name = "Delete project"
    edit_project_name_button_name = "Edit project name"

    def wait_until_loaded(self, expected_project_name: str | None = None) -> None:
        self.wait_for_url(re.compile(r".*/app/projects/[^/]+"))
        if expected_project_name:
            self.wait_for_visible(
                self.page.get_by_role("heading", name=expected_project_name, level=1)
            )
        else:
            self.wait_for_visible(self.page.locator(self.page_heading).first)

    def get_heading_text(self) -> str:
        heading = self.page.locator(self.page_heading).first
        self.wait_for_visible(heading)
        return heading.inner_text().strip()

    def get_main_content_text(self) -> str:
        container = self.page.locator(self.main_container).first
        self.wait_for_visible(container)
        return container.inner_text().strip()

    def is_new_run_button_visible(self) -> bool:
        return self.is_locator_visible(
            self.page.get_by_role("link", name=self.new_run_link_name).first,
            timeout_ms=3000,
        )

    def is_delete_project_button_visible(self) -> bool:
        return self.is_locator_visible(
            self.page.get_by_role("button", name=self.delete_project_button_name).first,
            timeout_ms=3000,
        )

    def delete_current_project(self) -> bool:
        """Click Delete project on project detail page and confirm deletion."""
        button = self.page.get_by_role("button", name=self.delete_project_button_name).first
        if self.is_locator_visible(button, timeout_ms=3000):
            self.click_locator(button, "Delete project button")
            confirm_btn = self.page.locator(
                'button:has-text("Delete"), button:has-text("Confirm"), [role="dialog"] button:has-text("Delete")'
            ).last
            if self.is_locator_visible(confirm_btn, timeout_ms=3000):
                self.click_locator(confirm_btn, "Confirm delete button")
            self.wait_for_loading_settled()
            return True
        return False
