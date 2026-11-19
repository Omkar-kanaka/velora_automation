"""LoginFactory decoupling platform-specific login page creation (Rule 1.2)."""

from playwright.sync_api import Page

from config.config import BaseConfig
from pages.auth.web_login_page import WebLoginPage


class LoginFactory:
    """Factory returning the appropriate login Page Object for the active platform."""

    @classmethod
    def create_login_page(cls, page: Page, config: BaseConfig) -> WebLoginPage:
        platform = config.platform.lower()
        if platform == "web":
            return WebLoginPage(
                page=page,
                base_url=config.base_url,
                default_timeout_ms=config.default_timeout_ms,
                navigation_timeout_ms=config.navigation_timeout_ms,
            )
        raise ValueError(f"No login page registered for platform '{platform}'.")
