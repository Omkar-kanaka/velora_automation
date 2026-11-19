"""Abstract base service wrapping IApiClient, RequestBuilder, and TokenProvider (Rule 1.3)."""

from abc import ABC

from core.api.api_client_interface import ApiResponse, IApiClient
from core.api.request_builder import RequestBuilder
from core.api.token_provider import TokenProvider


class AbstractService(ABC):
    """Base API service handling base URL, common headers, and optional token propagation."""

    def __init__(
        self,
        api_client: IApiClient,
        base_url: str,
        token_provider: TokenProvider | None = None,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self._api_client = api_client
        self._base_url = base_url.rstrip("/")
        self._token_provider = token_provider
        self._default_headers = dict(default_headers or {})

    def _builder(self, endpoint: str = "", method: str = "GET") -> RequestBuilder:
        builder = RequestBuilder(self._base_url).method(method)
        if endpoint:
            builder.endpoint(endpoint)
        if self._default_headers:
            builder.headers(self._default_headers)
        return builder

    def _execute(self, builder: RequestBuilder) -> ApiResponse:
        return self._api_client.send(builder.build())
