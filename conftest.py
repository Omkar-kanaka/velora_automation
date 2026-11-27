"""Root pytest configuration: event loop policy, factories, fixtures, and failure artifacts."""

import asyncio
import base64
import json
import os
import re
import sys
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, Playwright, sync_playwright

from config.config import BaseConfig, ConfigManager, UserCredentials
from core.api.api_client_interface import IApiClient
from core.api.health_service import HealthService
from core.api.playwright_api_client import PlaywrightApiClient
from core.api.project_service import ProjectService
from core.api.token_provider import TokenProvider
from core.factories.driver_factory import BrowserSession, DriverFactory
from core.factories.login_factory import LoginFactory
from pages.auth.forgot_password_page import ForgotPasswordPage
from pages.auth.sign_up_page import SignUpPage
from pages.auth.web_login_page import WebLoginPage
from pages.components.sidebar_component import SidebarComponent
from pages.dashboard_page import DashboardPage
from pages.projects.meeting_notes_modal import MeetingNotesModal
from pages.projects.new_project_page import NewProjectPage
from pages.projects.new_run_page import NewRunPage
from pages.projects.project_detail_page import ProjectDetailPage
from pages.projects.repository_modal import RepositoryModal
from pages.projects.run_questions_page import RunQuestionsPage
from pages.projects.run_specs_page import RunSpecsPage
from pages.projects_page import ProjectsPage
from pages.settings_page import SettingsPage
from utils.artifact_capture import capture_failure_artifacts
from utils.logger import configure_logging, get_logger
from utils.paths import (
    AUTH_DIR,
    AUTH_IDB_FILE,
    AUTH_STATE_FILE,
    AUTH_TOKEN_FILE,
    PROJECT_DATA_FILE,
    SETTINGS_DATA_FILE,
    ensure_artifact_directories,
)

logger = get_logger(__name__)


# ----------------------------------------------------------------------
# Session Bootstrap & CLI Options (Rules 5.2, 6.1, 6.2)
# ----------------------------------------------------------------------
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Target environment: local_qa | qa | staging | prod (overrides TEST_ENV).",
    )
    parser.addoption(
        "--browser-name",
        action="store",
        default=None,
        help="Browser engine: chromium | firefox | webkit (overrides BROWSER).",
    )
    parser.addoption(
        "--browser-channel",
        action="store",
        default=None,
        help="Chromium browser channel: chrome | msedge (overrides BROWSER_CHANNEL).",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in headed mode (overrides HEADLESS=true).",
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        type=int,
        default=None,
        help="Delay in milliseconds between Playwright actions (overrides SLOW_MO_MS).",
    )
    parser.addoption(
        "--no-session-auth",
        action="store_true",
        default=False,
        help="Disable session auth state reuse and force fresh UI login on every test.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Apply Windows Proactor event loop policy (Rule 6.2) and initialize directories/logging."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    ensure_artifact_directories()
    configure_logging()


# ----------------------------------------------------------------------
# Configuration & API Layer Fixtures (Rules 1.3, 4.1, 4.2)
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def app_config(pytestconfig: pytest.Config) -> BaseConfig:
    env_override = pytestconfig.getoption("--env")
    cfg = ConfigManager.get_config(env_override)

    browser_override = pytestconfig.getoption("--browser-name")
    if browser_override:
        cfg.browser = browser_override.strip().lower()

    channel_override = pytestconfig.getoption("--browser-channel")
    if channel_override:
        cfg.browser_channel = channel_override.strip().lower()

    if pytestconfig.getoption("--headed"):
        cfg.headless = False

    slow_mo_override = pytestconfig.getoption("--slow-mo")
    if slow_mo_override is not None:
        cfg.slow_mo_ms = slow_mo_override
    elif not cfg.headless and os.getenv("SLOW_MO_MS") is None and cfg.slow_mo_ms == 0:
        cfg.slow_mo_ms = cfg.DEFAULT_HEADED_SLOW_MO_MS

    logger.info(
        "Loaded config env=%s base_url=%s browser=%s channel=%s headless=%s slow_mo=%dms",
        cfg.ENV_NAME,
        cfg.base_url,
        cfg.browser,
        cfg.browser_channel or "bundled",
        cfg.headless,
        cfg.slow_mo_ms,
    )
    return cfg


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def api_client(
    playwright_instance: Playwright,
    app_config: BaseConfig,
) -> Generator[IApiClient, None, None]:
    request_context = playwright_instance.request.new_context(base_url=app_config.api_base_url)
    client = PlaywrightApiClient(request_context)
    yield client
    client.close()


@pytest.fixture(scope="session")
def backend_api_client(
    playwright_instance: Playwright,
    app_config: BaseConfig,
) -> Generator[IApiClient, None, None]:
    request_context = playwright_instance.request.new_context(base_url=app_config.backend_api_url)
    client = PlaywrightApiClient(request_context)
    yield client
    client.close()


@pytest.fixture(scope="session")
def project_service(
    backend_api_client: IApiClient,
    app_config: BaseConfig,
    token_provider: TokenProvider,
) -> ProjectService:
    return ProjectService(
        api_client=backend_api_client,
        base_url=app_config.backend_api_url,
        token_provider=token_provider,
    )


@pytest.fixture(scope="session")
def token_provider(api_client: IApiClient) -> Generator[TokenProvider, None, None]:
    provider = TokenProvider(api_client=api_client)
    yield provider
    provider.clear_cache()


@pytest.fixture(scope="session")
def health_service(
    api_client: IApiClient,
    app_config: BaseConfig,
    token_provider: TokenProvider,
) -> HealthService:
    return HealthService(
        api_client=api_client,
        base_url=app_config.base_url,
        token_provider=token_provider,
    )


@pytest.fixture(scope="session", autouse=True)
def verify_target_environment_reachable(
    health_service: HealthService,
    app_config: BaseConfig,
) -> None:
    """Pre-flight check ensuring the local QA app is running before UI tests execute."""
    try:
        response = health_service.check_app_reachable(path="/sign-in", timeout_ms=5000)
    except Exception as exc:
        pytest.exit(
            f"Target QA environment at {app_config.base_url} is not reachable. "
            f"Start the Velora app locally and re-run pytest. Error: {exc}",
            returncode=2,
        )
    if not response.ok:
        pytest.exit(
            f"Target QA environment at {app_config.base_url}/sign-in returned HTTP {response.status_code}.",
            returncode=2,
        )
    logger.info("Pre-flight health check passed: %s/sign-in -> HTTP %d", app_config.base_url, response.status_code)


# ----------------------------------------------------------------------
# Browser & Isolated Per-Test Session Fixtures (Rules 1.2, 3.1, 3.2)
# ----------------------------------------------------------------------
def _is_valid_state_file(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def _is_token_fresh(token: str | None, min_ttl_seconds: int = 120) -> bool:
    """Return True if a JWT bearer token is valid and has at least min_ttl_seconds remaining."""
    if not token:
        return False
    parts = token.split(".")
    if len(parts) != 3:
        return False
    try:
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
        exp = payload.get("exp")
        if not isinstance(exp, (int, float)):
            return False
        return float(exp) > (time.time() + min_ttl_seconds)
    except Exception:
        return False


_DUMP_IDB_SCRIPT = """
async () => {
    return new Promise((resolve) => {
        try {
            const req = indexedDB.open('firebaseLocalStorageDb');
            req.onerror = () => resolve([]);
            req.onsuccess = () => {
                const db = req.result;
                if (!db.objectStoreNames.contains('firebaseLocalStorage')) {
                    resolve([]);
                    return;
                }
                const tx = db.transaction('firebaseLocalStorage', 'readonly');
                const store = tx.objectStore('firebaseLocalStorage');
                const getAllReq = store.getAll();
                const getAllKeysReq = store.getAllKeys();
                let keys = null;
                let values = null;
                getAllKeysReq.onsuccess = () => {
                    keys = getAllKeysReq.result;
                    if (values !== null) finish();
                };
                getAllReq.onsuccess = () => {
                    values = getAllReq.result;
                    if (keys !== null) finish();
                };
                function finish() {
                    const items = [];
                    for (let i = 0; i < (keys || []).length; i++) {
                        items.push({ key: keys[i], value: values[i] });
                    }
                    resolve(items);
                }
            };
        } catch {
            resolve([]);
        }
    });
}
"""


@pytest.fixture(scope="session")
def browser(
    playwright_instance: Playwright,
    app_config: BaseConfig,
) -> Generator[Browser, None, None]:
    launched = DriverFactory.launch_browser(playwright_instance, app_config)
    yield launched
    logger.info("Closing browser instance")
    launched.close()


@pytest.fixture(scope="session")
def session_auth_state(
    browser: Browser,
    app_config: BaseConfig,
    pytestconfig: pytest.Config,
) -> tuple[Path | None, list[dict[str, Any]], str | None]:
    """Capture or load session auth storage state & IndexedDB for valid_user (Rule 3.3)."""
    if pytestconfig.getoption("--no-session-auth"):
        logger.info("Session auth state caching disabled via --no-session-auth")
        return None, [], None

    cached_idb: list[dict[str, Any]] = []
    cached_token: str | None = None

    if AUTH_IDB_FILE.is_file() and AUTH_IDB_FILE.stat().st_size > 0:
        try:
            cached_idb = json.loads(AUTH_IDB_FILE.read_text(encoding="utf-8"))
        except Exception:
            cached_idb = []

    if cached_idb and _is_valid_state_file(AUTH_STATE_FILE):
        if AUTH_TOKEN_FILE.is_file():
            cached_token = AUTH_TOKEN_FILE.read_text(encoding="utf-8").strip() or None
        if _is_token_fresh(cached_token):
            logger.info("Reusing existing session auth state (%d IDB items) from %s", len(cached_idb), AUTH_DIR)
            return AUTH_STATE_FILE, cached_idb, cached_token
        logger.info("Cached bearer token is missing or expired; regenerating fresh session auth state")

    user = app_config.get_user("valid_user")
    logger.info("Generating session auth state for user=%s", user.email)

    temp_context = browser.new_context(
        viewport={"width": app_config.viewport_width, "height": app_config.viewport_height},
        accept_downloads=True,
    )
    temp_page = temp_context.new_page()
    captured_tokens: list[str] = []

    def _on_req(req) -> None:
        if app_config.backend_api_url in req.url:
            auth_header = req.headers.get("authorization", "")
            if auth_header.lower().startswith("bearer "):
                captured_tokens.append(auth_header.split(" ", 1)[1].strip())

    temp_page.on("request", _on_req)

    try:
        temp_login = LoginFactory.create_login_page(temp_page, app_config)
        temp_login.open()
        temp_login.login_and_wait_for_app(user.email, user.password)
        temp_page.wait_for_timeout(2000)

        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        temp_context.storage_state(path=str(AUTH_STATE_FILE))
        logger.info("Saved valid_user storage state to %s", AUTH_STATE_FILE)

        idb_items: list[dict[str, Any]] = temp_page.evaluate(_DUMP_IDB_SCRIPT)
        if idb_items:
            AUTH_IDB_FILE.write_text(json.dumps(idb_items, indent=2), encoding="utf-8")
            logger.info("Saved %d Firebase Auth IDB records to %s", len(idb_items), AUTH_IDB_FILE)

        bearer_token = captured_tokens[-1] if captured_tokens else None
        if not bearer_token:
            for item in idb_items:
                val = item.get("value", {})
                if isinstance(val, dict) and "stsTokenManager" in val:
                    bearer_token = val["stsTokenManager"].get("accessToken")
                    break

        if bearer_token:
            AUTH_TOKEN_FILE.write_text(bearer_token, encoding="utf-8")
            logger.info("Saved bearer token to %s", AUTH_TOKEN_FILE)

        return AUTH_STATE_FILE, idb_items, bearer_token
    except Exception as exc:
        logger.warning(
            "Failed to generate session auth state: %s. Falling back to fresh logins.", exc
        )
        return None, [], None
    finally:
        temp_context.close()


@pytest.fixture(scope="function")
def browser_session(
    browser: Browser,
    app_config: BaseConfig,
    request: pytest.FixtureRequest,
    session_auth_state: tuple[Path | None, list[dict[str, Any]], str | None],
) -> Generator[BrowserSession, None, None]:
    """Provide an isolated BrowserContext/Page per test, pre-seeded with session state when requested."""
    state_path, idb_items, bearer_token = session_auth_state

    wants_auth = "authenticated_user" in request.fixturenames
    is_valid_user = True
    if hasattr(request, "node") and hasattr(request.node, "callspec"):
        if "users" in request.node.callspec.params:
            if request.node.callspec.params["users"] != "valid_user":
                is_valid_user = False

    use_session_auth = bool(wants_auth and is_valid_user and (state_path is not None or idb_items))

    session = DriverFactory.create_session(
        browser=browser,
        config=app_config,
        storage_state=state_path if use_session_auth else None,
        idb_items=idb_items if use_session_auth else None,
        preseeded_token=bearer_token if use_session_auth else None,
    )
    request.node._browser_session = session  # type: ignore[attr-defined]
    session._used_session_auth = use_session_auth  # type: ignore[attr-defined]
    yield session

    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call = getattr(request.node, "rep_call", None)
    failed = bool((rep_setup and rep_setup.failed) or (rep_call and rep_call.failed))
    if failed:
        logger.error("Test failed (%s) — capturing diagnostic artifacts", request.node.nodeid)
        capture_failure_artifacts(
            page=session.page,
            test_name=request.node.nodeid,
            console_messages=session.console_logs,
        )

    session.close()


# ----------------------------------------------------------------------
# Indirect User Persona Fixture (Rule 3.3)
# ----------------------------------------------------------------------
@pytest.fixture(scope="function")
def users(request: pytest.FixtureRequest, app_config: BaseConfig) -> UserCredentials:
    """Resolve user persona via indirect parametrization (defaults to 'valid_user')."""
    persona = getattr(request, "param", "valid_user")
    return app_config.get_user(persona)


# ----------------------------------------------------------------------
# Page Object Fixtures — No Direct Instantiation in Tests (Rule 3.2)
# ----------------------------------------------------------------------
@pytest.fixture(scope="function")
def login_page(browser_session: BrowserSession, app_config: BaseConfig) -> WebLoginPage:
    return LoginFactory.create_login_page(browser_session.page, app_config)


@pytest.fixture(scope="function")
def sign_up_page(browser_session: BrowserSession, app_config: BaseConfig) -> SignUpPage:
    return SignUpPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def forgot_password_page(
    browser_session: BrowserSession,
    app_config: BaseConfig,
) -> ForgotPasswordPage:
    return ForgotPasswordPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def sidebar(browser_session: BrowserSession, app_config: BaseConfig) -> SidebarComponent:
    return SidebarComponent(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def dashboard_page(browser_session: BrowserSession, app_config: BaseConfig) -> DashboardPage:
    return DashboardPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def projects_page(browser_session: BrowserSession, app_config: BaseConfig) -> ProjectsPage:
    return ProjectsPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def settings_page(browser_session: BrowserSession, app_config: BaseConfig) -> SettingsPage:
    return SettingsPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def new_project_page(browser_session: BrowserSession, app_config: BaseConfig) -> NewProjectPage:
    return NewProjectPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def meeting_notes_modal(browser_session: BrowserSession, app_config: BaseConfig) -> MeetingNotesModal:
    return MeetingNotesModal(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def repository_modal(browser_session: BrowserSession, app_config: BaseConfig) -> RepositoryModal:
    return RepositoryModal(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def project_detail_page(
    browser_session: BrowserSession,
    app_config: BaseConfig,
) -> ProjectDetailPage:
    return ProjectDetailPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def run_questions_page(
    browser_session: BrowserSession,
    app_config: BaseConfig,
) -> RunQuestionsPage:
    return RunQuestionsPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def run_specs_page(
    browser_session: BrowserSession,
    app_config: BaseConfig,
) -> RunSpecsPage:
    return RunSpecsPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def new_run_page(
    browser_session: BrowserSession,
    app_config: BaseConfig,
) -> NewRunPage:
    return NewRunPage(
        page=browser_session.page,
        base_url=app_config.base_url,
        default_timeout_ms=app_config.default_timeout_ms,
        navigation_timeout_ms=app_config.navigation_timeout_ms,
    )


@pytest.fixture(scope="function")
def managed_project(
    authenticated_user: UserCredentials,
    browser_session: BrowserSession,
    project_service: ProjectService,
):
    """Factory fixture creating projects via API with guaranteed teardown cleanup (Rule 3.2)."""
    created_ids: list[str] = []

    def _create(name: str, description: str | None = None) -> dict[str, Any]:
        if not browser_session.bearer_token:
            browser_session.page.wait_for_timeout(500)
        if not browser_session.bearer_token:
            raise RuntimeError("No authenticated Bearer token was captured for backend API calls.")
        project = project_service.create_project(
            name=name,
            description=description,
            bearer_token=browser_session.bearer_token,
        )
        created_ids.append(project["id"])
        logger.info("Created managed QA project '%s' (id=%s)", name, project["id"])
        return project

    yield _create

    token = browser_session.bearer_token
    if token:
        for project_id in reversed(created_ids):
            try:
                resp = project_service.delete_project(project_id, bearer_token=token)
                logger.info("Cleaned up managed QA project id=%s (HTTP %d)", project_id, resp.status_code)
            except Exception as exc:
                logger.warning("Failed to clean up project id=%s: %s", project_id, exc)


@pytest.fixture(scope="function")
def track_and_cleanup_project(
    browser_session: BrowserSession,
    project_service: ProjectService,
):
    """Tracks project ID created during UI tests and guarantees deletion before test teardown completes."""
    tracked_project_ids: list[str] = []

    def _track(project_id: str | None) -> None:
        if project_id and project_id not in tracked_project_ids:
            tracked_project_ids.append(project_id)
            logger.info("Tracking project id='%s' for guaranteed cleanup", project_id)

    yield _track

    token = browser_session.bearer_token
    if not token and AUTH_TOKEN_FILE.is_file():
        try:
            token = AUTH_TOKEN_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            token = None

    if token:
        for project_id in reversed(tracked_project_ids):
            try:
                resp = project_service.delete_project(project_id, bearer_token=token)
                logger.info("Cleaned up QA project id=%s before test completion (HTTP %d)", project_id, resp.status_code)
            except Exception as exc:
                logger.warning("Failed to clean up project id=%s: %s", project_id, exc)


@pytest.fixture(scope="session")
def project_test_data() -> dict[str, Any]:
    """Load New Project test data from testdata/project.json using pathlib.Path."""
    with PROJECT_DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="session")
def settings_test_data() -> dict[str, Any]:
    """Load Settings test data from testdata/settings.json using pathlib.Path."""
    with SETTINGS_DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="function")
def authenticated_user(
    browser_session: BrowserSession,
    login_page: WebLoginPage,
    users: UserCredentials,
    app_config: BaseConfig,
) -> UserCredentials:
    """Ensure the browser session is authenticated as the requested persona before the test runs."""
    used_session_auth = getattr(browser_session, "_used_session_auth", False)

    if used_session_auth and users.persona == "valid_user":
        target_url = f"{app_config.base_url}/app"
        browser_session.page.goto(target_url, wait_until="domcontentloaded")

        try:
            browser_session.page.wait_for_url(
                re.compile(r".*/app($|/.*)"),
                timeout=app_config.navigation_timeout_ms,
            )
            if not _is_token_fresh(browser_session.bearer_token):
                browser_session.page.wait_for_timeout(1000)
                if not _is_token_fresh(browser_session.bearer_token):
                    idb_items: list[dict[str, Any]] = browser_session.page.evaluate(_DUMP_IDB_SCRIPT)
                    for item in idb_items:
                        val = item.get("value", {})
                        if isinstance(val, dict) and "stsTokenManager" in val:
                            refreshed = val["stsTokenManager"].get("accessToken")
                            if _is_token_fresh(refreshed):
                                browser_session.bearer_token = refreshed
                                break
            logger.info("Session restored successfully for %s at %s", users.email, browser_session.page.url)
        except Exception:
            current_url = browser_session.page.url
            if "/sign-in" in current_url:
                logger.warning("Session auth state invalidated; falling back to interactive UI login")
                login_page.login_and_wait_for_app(users.email, users.password)
                try:
                    AUTH_DIR.mkdir(parents=True, exist_ok=True)
                    browser_session.context.storage_state(path=str(AUTH_STATE_FILE))
                except Exception as exc:
                    logger.warning("Failed to refresh session auth state file: %s", exc)
    else:
        login_page.open()
        login_page.login_and_wait_for_app(users.email, users.password)

    return users


# ----------------------------------------------------------------------
# Failure Reporting Hook (Rule 5.1)
# ----------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator[None, None, None]:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
