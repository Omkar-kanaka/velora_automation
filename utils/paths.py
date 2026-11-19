"""Cross-platform path definitions using pathlib.Path (Rule 6.1)."""

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
TESTDATA_DIR: Path = PROJECT_ROOT / "testdata"
TESTDATA_FRD_DIR: Path = TESTDATA_DIR / "Test_FRD"
TESTDATA_FILES_DIR: Path = TESTDATA_DIR / "files"
USER_DATA_FILE: Path = TESTDATA_DIR / "user.json"
PROJECT_DATA_FILE: Path = TESTDATA_DIR / "project.json"
SETTINGS_DATA_FILE: Path = TESTDATA_DIR / "settings.json"
ARTIFACTS_DIR: Path = PROJECT_ROOT / "artifacts"
AUTH_DIR: Path = ARTIFACTS_DIR / "auth"
AUTH_STATE_FILE: Path = AUTH_DIR / "valid_user_state.json"
AUTH_IDB_FILE: Path = AUTH_DIR / "valid_user_idb.json"
AUTH_TOKEN_FILE: Path = AUTH_DIR / "bearer_token.txt"
SCREENSHOTS_DIR: Path = ARTIFACTS_DIR / "screenshots"
CONSOLE_LOGS_DIR: Path = ARTIFACTS_DIR / "console_logs"
FAILURE_DOM_DIR: Path = ARTIFACTS_DIR / "failure_dom"
LOGS_DIR: Path = ARTIFACTS_DIR / "logs"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"


def ensure_artifact_directories() -> None:
    """Create all required artifact and report directories if missing."""
    for directory in (
        ARTIFACTS_DIR,
        AUTH_DIR,
        SCREENSHOTS_DIR,
        CONSOLE_LOGS_DIR,
        FAILURE_DOM_DIR,
        LOGS_DIR,
        REPORTS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
