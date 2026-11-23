"""DriverFactory decoupling browser & platform creation from tests (Rule 1.2)."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from playwright.sync_api import (
    Browser,
    BrowserContext,
    ConsoleMessage,
    Error as PlaywrightError,
    Page,
    Playwright,
)

from config.config import BaseConfig
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BrowserSession:
    """Encapsulates an isolated per-test browser context, page, console logs, and session token."""

    context: BrowserContext
    page: Page
    console_logs: list[str] = field(default_factory=list)
    bearer_token: str | None = None

    def close(self) -> None:
        self.context.close()


class DriverFactory:
    """Factory creating Playwright browser instances and isolated test sessions."""

    SUPPORTED_BROWSERS = ("chromium", "firefox", "webkit")
    SUPPORTED_PLATFORMS = ("web",)
    CHROMIUM_FALLBACK_CHANNELS = ("chrome", "msedge")

    @classmethod
    def launch_browser(cls, playwright: Playwright, config: BaseConfig) -> Browser:
        """Launch a browser according to configured platform and browser type."""
        if config.platform not in cls.SUPPORTED_PLATFORMS:
            raise ValueError(
                f"Unsupported platform '{config.platform}'. Supported: {cls.SUPPORTED_PLATFORMS}"
            )
        if config.browser not in cls.SUPPORTED_BROWSERS:
            raise ValueError(
                f"Unsupported browser '{config.browser}'. Supported: {cls.SUPPORTED_BROWSERS}"
            )

        logger.info(
            "Launching %s browser (platform=%s, channel=%s, headless=%s, slow_mo=%dms)",
            config.browser,
            config.platform,
            config.browser_channel or "bundled",
            config.headless,
            config.slow_mo_ms,
        )
        browser_type = getattr(playwright, config.browser)
        launch_args: list[str] = []
        if config.browser == "chromium":
            launch_args.append("--start-maximized")

        launch_kwargs: dict[str, object] = {
            "headless": config.headless,
            "slow_mo": config.slow_mo_ms,
            "args": launch_args,
        }
        if config.browser == "chromium" and config.browser_channel:
            launch_kwargs["channel"] = config.browser_channel

        try:
            return browser_type.launch(**launch_kwargs)
        except PlaywrightError as exc:
            if (
                config.browser != "chromium"
                or config.browser_channel is not None
                or "spawn UNKNOWN" not in str(exc)
            ):
                raise

            logger.warning(
                "Bundled Chromium launch blocked (%s). Falling back to a signed system browser channel.",
                exc.message.splitlines()[0] if hasattr(exc, "message") else exc,
            )
            last_error: Exception = exc
            for channel in cls.CHROMIUM_FALLBACK_CHANNELS:
                try:
                    logger.info("Retrying chromium launch with channel='%s'", channel)
                    return browser_type.launch(
                        headless=config.headless,
                        slow_mo=config.slow_mo_ms,
                        channel=channel,
                        args=launch_args,
                    )
                except PlaywrightError as channel_exc:
                    logger.warning("Channel '%s' unavailable: %s", channel, channel_exc)
                    last_error = channel_exc
            raise last_error

    _INIT_IDB_SCRIPT = """
    (() => {
        const items = __IDB_ITEMS__;
        if (!items || items.length === 0) return;
        const req = indexedDB.open('firebaseLocalStorageDb', 1);
        req.onupgradeneeded = (e) => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains('firebaseLocalStorage')) {
                db.createObjectStore('firebaseLocalStorage', { keyPath: 'fbase_key' });
            }
        };
        req.onsuccess = (e) => {
            const db = e.target.result;
            const tx = db.transaction('firebaseLocalStorage', 'readwrite');
            const store = tx.objectStore('firebaseLocalStorage');
            for (const item of items) {
                store.put(item.value);
            }
        };
    })();
    """

    @classmethod
    def create_session(
        cls,
        browser: Browser,
        config: BaseConfig,
        storage_state: Path | str | None = None,
        idb_items: list[dict[str, Any]] | None = None,
        preseeded_token: str | None = None,
    ) -> BrowserSession:
        """Create an isolated BrowserContext and Page, optionally pre-seeded with auth state."""
        context_kwargs: dict[str, object] = {
            "accept_downloads": True,
        }
        if not config.headless and config.browser == "chromium":
            # Allow browser window and web layout to fit the full monitor screen
            context_kwargs["no_viewport"] = True
        else:
            context_kwargs["viewport"] = {
                "width": config.viewport_width,
                "height": config.viewport_height,
            }
        if storage_state is not None:
            state_path = Path(storage_state)
            if state_path.is_file() and state_path.stat().st_size > 0:
                context_kwargs["storage_state"] = str(state_path)
                logger.debug("Reusing session storage state from %s", state_path)

        context = browser.new_context(**context_kwargs)
        context.set_default_timeout(config.default_timeout_ms)
        context.set_default_navigation_timeout(config.navigation_timeout_ms)

        if idb_items:
            injected_script = cls._INIT_IDB_SCRIPT.replace("__IDB_ITEMS__", json.dumps(idb_items))
            context.add_init_script(injected_script)
            logger.debug("Injected %d Firebase Auth IndexedDB records into context", len(idb_items))

        page = context.new_page()
        console_logs: list[str] = []

        def _on_console(message: ConsoleMessage) -> None:
            if message.type in {"error", "warning"}:
                entry = f"[console.{message.type}] {message.text}"
                console_logs.append(entry)
                logger.warning("Browser %s", entry)

        def _on_page_error(error: Exception) -> None:
            entry = f"[pageerror] {error}"
            console_logs.append(entry)
            logger.error("Browser %s", entry)

        page.on("console", _on_console)
        page.on("pageerror", _on_page_error)

        session = BrowserSession(
            context=context,
            page=page,
            console_logs=console_logs,
            bearer_token=preseeded_token,
        )

        def _on_request(request) -> None:
            if config.backend_api_url in request.url:
                auth_header = request.headers.get("authorization", "")
                if auth_header.lower().startswith("bearer "):
                    session.bearer_token = auth_header.split(" ", 1)[1].strip()

        page.on("request", _on_request)
        return session
