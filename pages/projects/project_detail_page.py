"""Page Object for Velora Project Detail screen (/app/projects/<id>)."""

import re

from pages.base_page import BasePage


class ProjectDetailPage(BasePage):
    """Encapsulates locators and queries for /app/projects/<id> (Rule 1.1)."""

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    main_container = "main"
    new_run_link_name = "New run"
    new_run_button = (
        'main a[data-variant="default"][href$="/runs/new"]:has-text("New run"), '
        'main a[href$="/runs/new"]:has-text("New run"), '
        'main button:has-text("New run"), '
        'main [data-slot="button"]:has-text("New run")'
    )
    delete_project_button_name = "Delete project"
    edit_project_name_button_name = "Edit project name"
    empty_runs_state_text = 'main p:has-text("No runs yet.")'
    empty_runs_new_run_button = 'main div:has(p:has-text("No runs yet.")) a[href$="/runs/new"]'
    run_card = 'main a[href*="/runs/"], main div:has(h2:has-text("Run")), main div:has-text("Run 1")'

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
            self.page.locator(self.new_run_button).first,
            timeout_ms=3000,
        )

    def is_empty_runs_state_visible(self) -> bool:
        """Verify 'No runs yet.' label is visible when project has no runs."""
        return self.is_locator_visible(
            self.page.locator(self.empty_runs_state_text).first,
            timeout_ms=3000,
        )

    def is_empty_runs_new_run_button_visible(self) -> bool:
        """Verify the 'New run' button inside the empty runs container is visible."""
        return self.is_locator_visible(
            self.page.locator(self.empty_runs_new_run_button).first,
            timeout_ms=3000,
        )

    def click_empty_state_new_run(self) -> None:
        """Click the 'New run' button displayed inside the empty runs state container."""
        button = self.page.locator(self.empty_runs_new_run_button).first
        self.click_locator(button, "Empty state New run button")
        try:
            self.wait_for_url(re.compile(r".*/app/projects/[^/]+/runs/new($|\?.*)"), timeout_ms=5000)
        except Exception:
            self.logger.debug("wait_for_url did not complete or timed out, continuing...")
        self.wait_for_loading_settled()

    def click_new_run(self) -> None:
        """Click the 'New run' button/link in the project header."""
        button = self.page.locator(self.new_run_button).first
        self.click_locator(button, "New run button")
        try:
            self.wait_for_url(re.compile(r".*/app/projects/[^/]+/runs/new($|\?.*)"), timeout_ms=5000)
        except Exception:
            self.logger.debug("wait_for_url did not complete or timed out, continuing...")
        self.wait_for_loading_settled()

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

    def get_runs_count(self) -> int:
        """Count the number of run cards displayed under the Runs section."""
        cards = self.page.locator('main a[href*="/runs/"]')
        return cards.count()

    def is_run_visible(self, run_text: str) -> bool:
        """Check if a run with the given title or label is visible in the runs list."""
        card = self.page.locator(f'main text="{run_text}"').first
        return self.is_locator_visible(card, timeout_ms=3000)

