from __future__ import annotations

from typing import cast

import httpx

from .errors import ProviderError

NEON_API_BASE = "https://console.neon.tech/api/v2"


class NeonApiClient:
    def __init__(
        self,
        api_key: str,
        *,
        project_id: str | None = None,
        project_name: str = "sheperd-research",
        branch_id: str = "main",
        timeout_seconds: float = 15.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("Neon API key is required")
        self.project_id = project_id
        self.project_name = project_name
        self.branch_id = branch_id
        self._client = httpx.Client(
            base_url=NEON_API_BASE,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            timeout=timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def inspect(self) -> dict[str, object]:
        try:
            response = self._client.get("/projects")
            response.raise_for_status()
            payload = self._json_dict(response)
            projects = payload.get("projects", [])
            if not isinstance(projects, list):
                raise ProviderError("Neon API returned invalid projects")
            project = self._find_project(projects)
            if project is None:
                raise ProviderError("Neon project was not found")
            selected_project_id = self._string(project.get("id"))
            if not selected_project_id:
                raise ProviderError("Neon project response has no ID")
            branches_response = self._client.get(f"/projects/{selected_project_id}/branches")
            branches_response.raise_for_status()
            branches_payload = self._json_dict(branches_response)
            branches = branches_payload.get("branches", [])
            if not isinstance(branches, list):
                raise ProviderError("Neon API returned invalid branches")
            branch = self._find_branch(branches)
            if branch is None:
                raise ProviderError("Neon branch was not found")
            selected_branch_id = self._string(branch.get("id"))
            if not selected_branch_id:
                raise ProviderError("Neon branch response has no ID")
            return {
                "status": "pass",
                "project_id": selected_project_id,
                "project_name": self._string(project.get("name")) or self.project_name,
                "branch_id": selected_branch_id,
                "branch_name": self._string(branch.get("name")) or self.branch_id,
            }
        except ProviderError:
            raise
        except httpx.HTTPStatusError as error:
            if error.response.status_code in {401, 403}:
                raise ProviderError("Neon API authentication failed") from error
            raise ProviderError(
                f"Neon API request failed with status {error.response.status_code}"
            ) from error
        except (httpx.HTTPError, ValueError) as error:
            raise ProviderError("Neon API request failed") from error

    def _find_project(self, projects: list[object]) -> dict[str, object] | None:
        for item in projects:
            if not isinstance(item, dict):
                continue
            project = cast(dict[str, object], item)
            project_id = self._string(project.get("id"))
            project_name = self._string(project.get("name"))
            if self.project_id and project_id == self.project_id:
                return project
            if not self.project_id and project_name == self.project_name:
                return project
        return None

    def _find_branch(self, branches: list[object]) -> dict[str, object] | None:
        for item in branches:
            if not isinstance(item, dict):
                continue
            branch = cast(dict[str, object], item)
            branch_id = self._string(branch.get("id"))
            branch_name = self._string(branch.get("name"))
            if branch_id == self.branch_id or branch_name == self.branch_id:
                return branch
        return None

    @staticmethod
    def _json_dict(response: httpx.Response) -> dict[str, object]:
        payload: object = response.json()
        if not isinstance(payload, dict):
            raise ProviderError("Neon API returned invalid JSON")
        return cast(dict[str, object], payload)

    @staticmethod
    def _string(value: object) -> str | None:
        return value if isinstance(value, str) and value.strip() else None
