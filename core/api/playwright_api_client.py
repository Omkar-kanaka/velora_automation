"""Playwright APIRequestContext implementation of IApiClient (Rule 1.3)."""

from typing import Any

from playwright.sync_api import APIRequestContext

from core.api.api_client_interface import ApiRequest, ApiResponse, IApiClient
from utils.logger import get_logger

logger = get_logger(__name__)


class PlaywrightApiClient(IApiClient):
    """Concrete IApiClient backed by Playwright's APIRequestContext."""

    def __init__(self, request_context: APIRequestContext) -> None:
        self._context = request_context

    def send(self, request: ApiRequest) -> ApiResponse:
        logger.info("API %s %s", request.method, request.url)
        kwargs: dict[str, Any] = {
            "method": request.method,
            "headers": request.headers or None,
            "params": request.params or None,
            "timeout": request.timeout_ms,
        }
        if request.json_body is not None:
            kwargs["data"] = request.json_body
        elif request.data is not None:
            kwargs["form"] = request.data

        response = self._context.fetch(request.url, **kwargs)
        raw_text = response.text()
        parsed_json: Any = None
        try:
            parsed_json = response.json()
        except Exception:
            parsed_json = None

        return ApiResponse(
            status_code=response.status,
            headers=dict(response.headers),
            text=raw_text,
            json_body=parsed_json,
        )

    def close(self) -> None:
        logger.debug("Disposing PlaywrightApiClient request context")
        self._context.dispose()
