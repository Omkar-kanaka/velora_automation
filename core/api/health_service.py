"""Pre-flight environment health service using the interface-driven API layer."""

from core.api.abstract_service import AbstractService
from core.api.api_client_interface import ApiResponse


class HealthService(AbstractService):
    """Checks whether the configured target web application is reachable."""

    def check_app_reachable(self, path: str = "/sign-in", timeout_ms: int = 5000) -> ApiResponse:
        builder = self._builder(endpoint=path, method="GET").timeout(timeout_ms)
        return self._execute(builder)
