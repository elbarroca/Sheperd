from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest

import sheperd_research.blob as blob_module
from sheperd_research.blob import download_private_pdf, upload_private_pdf


def test_upload_private_pdf_uses_existing_http_client(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "report.pdf"
    path.write_bytes(b"%PDF-1.4\n")

    def fake_put(url: str, **kwargs: object) -> httpx.Response:
        assert url == "https://vercel.com/api/blob"
        assert kwargs["params"] == {"pathname": "reports/run.pdf"}
        headers = kwargs["headers"]
        assert isinstance(headers, dict)
        assert headers["authorization"] == "Bearer secret-token"
        assert headers["x-vercel-blob-access"] == "private"
        request = httpx.Request("PUT", url)
        return httpx.Response(
            200,
            request=request,
            json={
                "url": "https://store.private.blob.vercel-storage.com/reports/run.pdf",
                "pathname": "reports/run.pdf",
            },
        )

    monkeypatch.setattr(blob_module.httpx, "put", fake_put)

    assert upload_private_pdf(path, "reports/run.pdf", "secret-token") == {
        "url": "https://store.private.blob.vercel-storage.com/reports/run.pdf",
        "pathname": "reports/run.pdf",
    }


def test_download_private_pdf_requires_private_blob_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    class FakeClient:
        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def get(self, url: str, **kwargs: object) -> httpx.Response:
            nonlocal called
            called = True
            assert kwargs["headers"] == {"authorization": "Bearer secret-token"}
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                content=b"%PDF-1.4\n",
                headers={"etag": '"pdf-etag"'},
            )

    monkeypatch.setattr(blob_module.httpx, "AsyncClient", FakeClient)

    content, etag = asyncio.run(
        download_private_pdf(
            "https://store.private.blob.vercel-storage.com/reports/run.pdf",
            "secret-token",
        )
    )
    assert content == b"%PDF-1.4\n"
    assert etag == '"pdf-etag"'
    assert called

    with pytest.raises(RuntimeError, match="blob_url_invalid"):
        asyncio.run(download_private_pdf("https://example.com/report.pdf", "secret-token"))
