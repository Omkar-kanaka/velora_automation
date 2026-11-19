"""Interface-driven ProjectService wrapping /v1/projects CRUD via IApiClient (Rule 1.3)."""

from typing import Any

from core.api.abstract_service import AbstractService
from core.api.api_client_interface import ApiResponse


class ProjectService(AbstractService):
    """Handles /v1/projects API calls for test setup and deterministic teardown (Rule 3.2)."""

    PROJECTS_ENDPOINT: str = "/v1/projects"

    def list_projects(self, bearer_token: str) -> ApiResponse:
        builder = (
            self._builder(endpoint=self.PROJECTS_ENDPOINT, method="GET")
            .bearer_token(bearer_token)
        )
        return self._execute(builder)

    def create_project(
        self,
        name: str,
        bearer_token: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description

        builder = (
            self._builder(endpoint=self.PROJECTS_ENDPOINT, method="POST")
            .bearer_token(bearer_token)
            .header("Content-Type", "application/json")
            .json_body(payload)
        )
        response = self._execute(builder)
        if not response.ok or not isinstance(response.json_body, dict):
            raise RuntimeError(
                f"Failed to create project '{name}' via API ({response.status_code}): {response.text[:300]}"
            )
        return response.json_body

    def delete_project(self, project_id: str, bearer_token: str) -> ApiResponse:
        builder = (
            self._builder(endpoint=f"{self.PROJECTS_ENDPOINT}/{project_id}", method="DELETE")
            .bearer_token(bearer_token)
        )
        return self._execute(builder)
