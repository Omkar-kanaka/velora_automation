"""Interface-driven API client contract (Rule 1.3)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ApiRequest:
    """Library-agnostic HTTP request representation."""

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    json_body: Any = None
    data: Any = None
    timeout_ms: int = 10000


@dataclass(frozen=True)
class ApiResponse:
    """Library-agnostic HTTP response representation."""

    status_code: int
    headers: dict[str, str]
    text: str
    json_body: Any = None

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


class IApiClient(ABC):
    """Abstract interface decoupling test services from any concrete HTTP library."""

    @abstractmethod
    def send(self, request: ApiRequest) -> ApiResponse:
        """Execute an HTTP request and return a normalized ApiResponse."""

    @abstractmethod
    def close(self) -> None:
        """Release underlying HTTP client resources."""
