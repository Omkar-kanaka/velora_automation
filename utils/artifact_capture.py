"""Automatic failure artifact capture: screenshots, console logs, and DOM snapshots (Rule 5.1)."""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from utils.logger import get_logger
from utils.paths import (
    CONSOLE_LOGS_DIR,
    FAILURE_DOM_DIR,
    SCREENSHOTS_DIR,
    ensure_artifact_directories,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class FailureArtifacts:
    """Paths to all artifacts captured on a test failure."""

    screenshot_path: Path | None = None
    console_log_path: Path | None = None
    dom_snapshot_path: Path | None = None
    dom_html_path: Path | None = None


def _sanitize_name(name: str) -> str:
    """Convert pytest node name into a safe cross-platform filename prefix."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_")[:120]


def capture_failure_artifacts(
    page: Page,
    test_name: str,
    console_messages: list[str],
) -> FailureArtifacts:
    """Capture full-page screenshot, console errors/warnings, and structural DOM snapshot."""
    ensure_artifact_directories()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    prefix = f"{_sanitize_name(test_name)}_{timestamp}"

    screenshot_path: Path | None = None
    console_log_path: Path | None = None
    dom_snapshot_path: Path | None = None
    dom_html_path: Path | None = None

    # 1. Full-page screenshot
    try:
        screenshot_path = SCREENSHOTS_DIR / f"{prefix}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info("Captured failure screenshot: %s", screenshot_path)
    except Exception as exc:
        logger.warning("Unable to capture failure screenshot: %s", exc)
        screenshot_path = None

    # 2. Browser console errors & warnings
    try:
        console_log_path = CONSOLE_LOGS_DIR / f"{prefix}.log"
        content = "\n".join(console_messages) if console_messages else "(no console errors or warnings recorded)"
        console_log_path.write_text(content, encoding="utf-8")
        logger.info("Saved browser console log: %s", console_log_path)
    except Exception as exc:
        logger.warning("Unable to write console log artifact: %s", exc)
        console_log_path = None

    # 3. Structural DOM snapshot (URL, title, visible modals/dialogs, and full HTML)
    try:
        active_url = page.url
        page_title = page.title()
        visible_dialogs: list[dict[str, Any]] = page.evaluate(
            """() => {
                const dialogs = Array.from(document.querySelectorAll('[role="dialog"], [role="alertdialog"], dialog[open]'));
                return dialogs
                    .filter(el => {
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    })
                    .map(el => ({
                        role: el.getAttribute('role') || el.tagName.toLowerCase(),
                        ariaLabel: el.getAttribute('aria-label') || '',
                        textPreview: (el.innerText || '').trim().slice(0, 500)
                    }));
            }"""
        )
        dom_html = page.content()

        dom_html_path = FAILURE_DOM_DIR / f"{prefix}.html"
        dom_html_path.write_text(dom_html, encoding="utf-8")

        dom_snapshot_path = FAILURE_DOM_DIR / f"{prefix}.json"
        snapshot_payload = {
            "test_name": test_name,
            "captured_at_utc": timestamp,
            "active_url": active_url,
            "page_title": page_title,
            "visible_modals": visible_dialogs,
            "console_entry_count": len(console_messages),
            "html_snapshot_file": dom_html_path.name,
        }
        dom_snapshot_path.write_text(
            json.dumps(snapshot_payload, indent=2),
            encoding="utf-8",
        )
        logger.info("Captured failure DOM snapshot: %s", dom_snapshot_path)
    except Exception as exc:
        logger.warning("Unable to capture DOM snapshot artifact: %s", exc)
        dom_snapshot_path = None
        dom_html_path = None

    return FailureArtifacts(
        screenshot_path=screenshot_path,
        console_log_path=console_log_path,
        dom_snapshot_path=dom_snapshot_path,
        dom_html_path=dom_html_path,
    )
