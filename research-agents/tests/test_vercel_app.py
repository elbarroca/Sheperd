from __future__ import annotations

from fastapi.testclient import TestClient

import app as vercel_app


def test_vercel_app_fails_closed_without_runtime_database(monkeypatch) -> None:
    monkeypatch.setattr(vercel_app, "_runtime_database_config", lambda: (None, "main"))
    client = TestClient(vercel_app.app)

    response = client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "blocked", "error": "RuntimeError"}
