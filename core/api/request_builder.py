"""Fluent RequestBuilder for constructing ApiRequest instances (Rule 1.3)."""

from typing import Any

from core.api.api_client_interface import ApiRequest


class RequestBuilder:
    """Builds normalized ApiRequest objects with headers, params, auth, and body."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._method = "GET"
        self._endpoint = ""
        self._headers: dict[str, str] = {}
        self._params: dict[str, Any] = {}
        self._json_body: Any = None
        self._data: Any = None
        self._timeout_ms: int = 10000

    def method(self, method: str) -> "RequestBuilder":
        self._method = method.upper()
        return self

    def endpoint(self, path: str) -> "RequestBuilder":
        self._endpoint = path if path.startswith("/") else f"/{path}"
        return self

    def header(self, key: str, value: str) -> "RequestBuilder":
        self._headers[key] = value
        return self

    def headers(self, headers: dict[str, str]) -> "RequestBuilder":
        self._headers.update(headers)
        return self

    def bearer_token(self, token: str) -> "RequestBuilder":
        self._headers["Authorization"] = f"Bearer {token}"
        return self

    def query_param(self, key: str, value: Any) -> "RequestBuilder":
        self._params[key] = value
        return self

    def query_params(self, params: dict[str, Any]) -> "RequestBuilder":
        self._params.update(params)
        return self

    def json_body(self, payload: Any) -> "RequestBuilder":
        self._json_body = payload
        return self

    def form_data(self, payload: Any) -> "RequestBuilder":
        self._data = payload
        return self

    def timeout(self, timeout_ms: int) -> "RequestBuilder":
        self._timeout_ms = timeout_ms
        return self

    def build(self) -> ApiRequest:
        full_url = f"{self._base_url}{self._endpoint}" if self._endpoint else self._base_url
        return ApiRequest(
            method=self._method,
            url=full_url,
            headers=dict(self._headers),
            params=dict(self._params),
            json_body=self._json_body,
            data=self._data,
            timeout_ms=self._timeout_ms,
        )
