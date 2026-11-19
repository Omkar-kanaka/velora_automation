"""Page Object for Velora authenticated Landing / New Project screen (/app)."""

from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Encapsulates locators and queries for /app (Rule 1.1)."""

    ROUTE: str = "/app"

    # Class-level snake_case locators (Rule 7)
    page_heading = "h1"
    start_button_name = "Start"

    def open(self) -> "DashboardPage":
        self.navigate_to(self.ROUTE)
        return self

    def open_protected_route(self, route: str) -> None:
        """Navigate directly to any protected /app/* route (used for access-control checks)."""
        self.navigate_to(route)

    def get_heading_text(self) -> str:
        heading = self.page.locator(self.page_heading).first
        self.wait_for_visible(heading)
        return heading.inner_text().strip()

    def is_loaded(self) -> bool:
        return self.is_locator_visible(
            self.page.get_by_role("button", name=self.start_button_name),
            timeout_ms=self.default_timeout_ms,
        )
