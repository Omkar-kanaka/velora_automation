"""Centralized OAuth2 / Bearer TokenProvider with in-memory caching (Rule 4.2)."""

import time
from dataclasses import dataclass

from core.api.api_client_interface import IApiClient
from core.api.request_builder import RequestBuilder
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class _CachedToken:
    access_token: str
    expires_at_epoch: float


class TokenProvider:
    """Retrieves and caches auth tokens keyed by (token_url, username, org)."""

    DEFAULT_TTL_SECONDS = 3000
    EXPIRY_SAFETY_BUFFER_SECONDS = 30

    def __init__(self, api_client: IApiClient) -> None:
        self._api_client = api_client
        self._cache: dict[tuple[str, str, str], _CachedToken] = {}

    def get_token(
        self,
        token_url: str,
        username: str,
        password: str,
        org: str = "default",
        extra_payload: dict[str, str] | None = None,
    ) -> str:
        """Return a cached bearer token or fetch a fresh one if expired/absent."""
        cache_key = (token_url.rstrip("/"), username, org)
        now = time.monotonic()

        cached = self._cache.get(cache_key)
        if cached and now < (cached.expires_at_epoch - self.EXPIRY_SAFETY_BUFFER_SECONDS):
            logger.debug("Using cached auth token for (%s, %s)", username, org)
            return cached.access_token

        logger.info("Fetching new auth token from %s for user '%s' (org='%s')", token_url, username, org)
        payload: dict[str, str] = {"email": username, "password": password}
        if extra_payload:
            payload.update(extra_payload)

        request = (
            RequestBuilder(token_url)
            .method("POST")
            .header("Content-Type", "application/json")
            .json_body(payload)
            .build()
        )
        response = self._api_client.send(request)
        if not response.ok or not isinstance(response.json_body, dict):
            raise RuntimeError(
                f"Token retrieval failed ({response.status_code}) from {token_url}: {response.text[:200]}"
            )

        token = (
            response.json_body.get("access_token")
            or response.json_body.get("token")
            or ""
        )
        if not token:
            raise RuntimeError(f"Token response from {token_url} did not contain an access token.")

        expires_in = int(response.json_body.get("expires_in", self.DEFAULT_TTL_SECONDS))
        self._cache[cache_key] = _CachedToken(
            access_token=token,
            expires_at_epoch=now + expires_in,
        )
        return token

    def clear_cache(self) -> None:
        """Clear all cached tokens."""
        self._cache.clear()
