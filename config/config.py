"""Hierarchical environment configuration with testdata/user.json personas & env overrides (Rule 4.1)."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from utils.data_generator import generate_unique_email
from utils.paths import USER_DATA_FILE


def _get_bool(env_var: str, default: bool) -> bool:
    raw = os.getenv(env_var)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(env_var: str, default: int) -> int:
    raw = os.getenv(env_var)
    if raw is None or not raw.strip():
        return default
    return int(raw.strip())


@dataclass(frozen=True)
class UserCredentials:
    """Immutable credential persona injected into tests via fixtures (Rule 3.3)."""

    persona: str
    email: str
    password: str
    org: str = "default"


class BaseConfig:
    """Base configuration shared across all target environments."""

    ENV_NAME: str = "base"
    DEFAULT_BASE_URL: str = "http://localhost:5173"
    DEFAULT_API_BASE_URL: str = "http://localhost:5173"
    DEFAULT_BACKEND_API_URL: str = "http://localhost:8000"
    DEFAULT_TIMEOUT: int = 10000
    DEFAULT_NAVIGATION_TIMEOUT: int = 20000
    DEFAULT_VIEWPORT_WIDTH: int = 1920
    DEFAULT_VIEWPORT_HEIGHT: int = 1080
    DEFAULT_SLOW_MO_MS: int = 0
    DEFAULT_HEADED_SLOW_MO_MS: int = 1000

    def __init__(self, user_data_path: Path | None = None) -> None:
        self.base_url: str = os.getenv("BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")
        self.api_base_url: str = os.getenv("API_BASE_URL", self.DEFAULT_API_BASE_URL).rstrip("/")
        self.backend_api_url: str = os.getenv("BACKEND_API_URL", self.DEFAULT_BACKEND_API_URL).rstrip("/")
        self.platform: str = os.getenv("PLATFORM", "web").strip().lower()
        self.browser: str = os.getenv("BROWSER", "chromium").strip().lower()
        self.browser_channel: str | None = (os.getenv("BROWSER_CHANNEL") or "").strip().lower() or None
        self.headless: bool = _get_bool("HEADLESS", True)
        default_slow_mo = self.DEFAULT_SLOW_MO_MS if self.headless else self.DEFAULT_HEADED_SLOW_MO_MS
        self.slow_mo_ms: int = _get_int("SLOW_MO_MS", default_slow_mo)
        self.viewport_width: int = _get_int("VIEWPORT_WIDTH", self.DEFAULT_VIEWPORT_WIDTH)
        self.viewport_height: int = _get_int("VIEWPORT_HEIGHT", self.DEFAULT_VIEWPORT_HEIGHT)
        self.default_timeout_ms: int = _get_int("DEFAULT_TIMEOUT_MS", self.DEFAULT_TIMEOUT)
        self.navigation_timeout_ms: int = _get_int(
            "NAVIGATION_TIMEOUT_MS",
            self.DEFAULT_NAVIGATION_TIMEOUT,
        )
        self.user_data_path: Path = user_data_path or USER_DATA_FILE
        self._user_data_cache: dict[str, Any] | None = None

    def _load_user_data(self) -> dict[str, Any]:
        if self._user_data_cache is None:
            if not self.user_data_path.exists():
                raise FileNotFoundError(
                    f"User test data file not found at: {self.user_data_path}"
                )
            with self.user_data_path.open("r", encoding="utf-8") as handle:
                self._user_data_cache = json.load(handle)
        return self._user_data_cache

    def get_user(self, persona: str) -> UserCredentials:
        """Resolve a named user persona from testdata/user.json for the active environment."""
        all_data = self._load_user_data()
        env_users: dict[str, Any] = (
            all_data.get(self.ENV_NAME)
            or all_data.get("default")
            or all_data.get("local_qa")
            or {}
        )

        if persona not in env_users:
            available = ", ".join(sorted(env_users.keys()))
            raise ValueError(
                f"Unknown user persona '{persona}' for env '{self.ENV_NAME}' in "
                f"{self.user_data_path.name}. Available: {available}"
            )

        raw = env_users[persona]
        if "email" in raw and raw["email"]:
            email = str(raw["email"])
        elif "email_prefix" in raw:
            email = generate_unique_email(
                prefix=str(raw["email_prefix"]),
                domain=str(raw.get("email_domain", "example.com")),
            )
        else:
            raise ValueError(f"Persona '{persona}' must define 'email' or 'email_prefix'.")

        password = str(raw.get("password", ""))
        org = str(raw.get("org", "default"))

        return UserCredentials(
            persona=persona,
            email=email,
            password=password,
            org=org,
        )


class LocalQAConfig(BaseConfig):
    """Default local deployment treated as QA environment."""

    ENV_NAME = "local_qa"
    DEFAULT_BASE_URL = "http://localhost:5173"
    DEFAULT_API_BASE_URL = "http://localhost:5173"


class QAConfig(BaseConfig):
    """Dedicated remote QA environment."""

    ENV_NAME = "qa"
    DEFAULT_BASE_URL = "https://qa.velora.internal"
    DEFAULT_API_BASE_URL = "https://qa.velora.internal"


class StagingConfig(BaseConfig):
    """Staging / Pre-production environment."""

    ENV_NAME = "staging"
    DEFAULT_BASE_URL = "https://staging.velora.internal"
    DEFAULT_API_BASE_URL = "https://staging.velora.internal"


class ProdConfig(BaseConfig):
    """Production smoke environment (read-only checks only)."""

    ENV_NAME = "prod"
    DEFAULT_BASE_URL = "https://app.velora.internal"
    DEFAULT_API_BASE_URL = "https://app.velora.internal"


class ConfigManager:
    """Factory resolving the active environment configuration."""

    _ENV_MAP: dict[str, type[BaseConfig]] = {
        "local": LocalQAConfig,
        "local_qa": LocalQAConfig,
        "qa": QAConfig,
        "staging": StagingConfig,
        "prod": ProdConfig,
    }

    @classmethod
    def get_config(cls, env_name: str | None = None) -> BaseConfig:
        selected = (env_name or os.getenv("TEST_ENV", "local_qa")).strip().lower()
        config_cls = cls._ENV_MAP.get(selected)
        if config_cls is None:
            valid = ", ".join(sorted(cls._ENV_MAP.keys()))
            raise ValueError(f"Unsupported TEST_ENV '{selected}'. Choose from: {valid}")
        return config_cls()
