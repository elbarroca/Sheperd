from __future__ import annotations

import httpx

from sheperd_research.providers.neon import NeonApiClient


def test_neon_inspect_is_read_only_and_redacted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v2/projects":
            return httpx.Response(
                200,
                json={"projects": [{"id": "project-1", "name": "sheperd-research"}]},
            )
        if request.url.path == "/api/v2/projects/project-1/branches":
            return httpx.Response(200, json={"branches": [{"id": "branch-1", "name": "main"}]})
        return httpx.Response(404)

    client = NeonApiClient("not-printed", transport=httpx.MockTransport(handler))
    try:
        result = client.inspect()
    finally:
        client.close()

    assert result == {
        "status": "pass",
        "project_id": "project-1",
        "project_name": "sheperd-research",
        "branch_id": "branch-1",
        "branch_name": "main",
    }
