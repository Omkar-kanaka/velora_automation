"""Page Object for Velora authenticated Sidebar navigation & user profile menu."""

import re

from pages.base_page import BasePage


class SidebarComponent(BasePage):
    """Encapsulates global sidebar navigation and user profile menu actions (Rule 1.1)."""

    # Class-level snake_case locators (Rule 7)
    new_project_link_name = "New project"
    all_projects_link_name = "All projects"
    settings_menu_item_name = "Settings"
    sign_out_menu_item_name = "Sign out"
    user_menu_email_pattern = re.compile(r"@")
    sidebar_root = '[data-slot="sidebar"]'
    collapse_sidebar_button = 'button[aria-label="Collapse sidebar"]'
    expand_sidebar_button = 'button[aria-label="Expand sidebar"]'

    def open_user_menu(self, email: str | None = None) -> "SidebarComponent":
        if email:
            trigger = self.page.get_by_role("button", name=re.compile(re.escape(email), re.IGNORECASE)).first
        else:
            trigger = self.page.get_by_role("button", name=self.user_menu_email_pattern).first
        self.click_locator(trigger, "Sidebar user profile menu button")
        return self

    def click_sign_out(self, email: str | None = None) -> None:
        self.open_user_menu(email=email)
        sign_out_item = self.page.get_by_role("menuitem", name=self.sign_out_menu_item_name)
        self.click_locator(sign_out_item, "Sign out menu item")
        self.wait_for_url(re.compile(r".*/sign-in($|\?.*)"))

    def click_settings(self, email: str | None = None) -> None:
        self.open_user_menu(email=email)
        settings_item = self.page.get_by_role("menuitem", name=self.settings_menu_item_name)
        self.click_locator(settings_item, "Settings menu item")
        self.wait_for_url(re.compile(r".*/app/settings($|\?.*)"))

    def click_new_project(self) -> None:
        link = self.page.get_by_role("link", name=self.new_project_link_name)
        self.click_locator(link, "New project sidebar link")
        self.wait_for_url(re.compile(r".*/app($|\?.*)"))

    def click_all_projects(self) -> None:
        link = self.page.get_by_role("link", name=self.all_projects_link_name)
        self.click_locator(link, "All projects sidebar link")
        self.wait_for_url(re.compile(r".*/app/projects($|\?.*)"))

    def is_user_menu_visible(self, email: str | None = None) -> bool:
        if email:
            trigger = self.page.get_by_role("button", name=re.compile(re.escape(email), re.IGNORECASE)).first
        else:
            trigger = self.page.get_by_role("button", name=self.user_menu_email_pattern).first
        return self.is_locator_visible(trigger)

    def wait_for_sidebar_ready(self) -> None:
        self.wait_for_loading_settled()
        self.wait_for_visible(self.page.locator(self.sidebar_root).first)

    def get_sidebar_state(self) -> str:
        sidebar = self.page.locator(self.sidebar_root).first
        self.wait_for_visible(sidebar)
        return sidebar.get_attribute("data-state") or ""

    def wait_for_sidebar_state(self, expected_state: str, timeout_ms: int | None = None) -> None:
        """Dynamically wait until [data-slot='sidebar'] reflects the expected data-state."""
        target = self.page.locator(f'{self.sidebar_root}[data-state="{expected_state}"]').first
        self.wait_for_visible(target, timeout_ms=timeout_ms or self.default_timeout_ms)

    def collapse_sidebar_via_button(self) -> None:
        button = self.page.locator(self.collapse_sidebar_button).first
        self.click_locator(button, "Collapse sidebar button")
        self.wait_for_sidebar_state("collapsed")

    def expand_sidebar_via_button(self) -> None:
        button = self.page.locator(self.expand_sidebar_button).first
        self.click_locator(button, "Expand sidebar button")
        self.wait_for_sidebar_state("expanded")

    def toggle_sidebar_via_shortcut(self) -> str:
        """Toggle sidebar with Ctrl+B and wait dynamically for data-state to flip."""
        current_state = self.get_sidebar_state()
        expected_state = "collapsed" if current_state == "expanded" else "expanded"
        self.logger.info("Toggling sidebar via Control+b (%s -> %s)", current_state, expected_state)
        self.page.keyboard.press("Control+b")
        self.wait_for_sidebar_state(expected_state)
        return expected_state
