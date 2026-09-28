from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlparse

import httpx

_BLOB_API_URL = "https://vercel.com/api/blob"
_BLOB_API_VERSION = "11"
_BLOB_TIMEOUT_SECONDS = 30.0
_MAX_PATHNAME_LENGTH = 950


def _validate_token(token: str) -> None:
    if not token.strip():
        raise RuntimeError("blob_token_missing")


def _validate_pathname(pathname: str) -> None:
    if (
        not pathname
        or pathname.startswith("/")
        or "\\" in pathname
        or "//" in pathname
        or len(pathname) > _MAX_PATHNAME_LENGTH
    ):
        raise RuntimeError("blob_path_invalid")


def _validate_private_url(url: str) -> None:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if (
        parsed.scheme != "https"
        or not hostname.endswith(".private.blob.vercel-storage.com")
        or not parsed.path.startswith("/")
    ):
        raise RuntimeError("blob_url_invalid")


def upload_private_pdf(path: Path, pathname: str, token: str) -> dict[str, str]:
    _validate_token(token)
    _validate_pathname(pathname)
    content = path.read_bytes() if path.is_file() else b""
    if not content.startswith(b"%PDF"):
        raise RuntimeError("blob_pdf_invalid")
    try:
        response = httpx.put(
            _BLOB_API_URL,
            params={"pathname": pathname},
            headers={
                "authorization": f"Bearer {token}",
                "x-api-version": _BLOB_API_VERSION,
                "x-content-type": "application/pdf",
                "x-add-random-suffix": "0",
                "x-allow-overwrite": "1",
                "x-vercel-blob-access": "private",
            },
            content=content,
            timeout=_BLOB_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError, OSError) as error:
        raise RuntimeError("blob_upload_failed") from error
    if not isinstance(payload, Mapping):
        raise RuntimeError("blob_upload_invalid_response")
    url = payload.get("url")
    stored_pathname = payload.get("pathname")
    if not isinstance(url, str) or not isinstance(stored_pathname, str):
        raise RuntimeError("blob_upload_invalid_response")
    _validate_private_url(url)
    if stored_pathname != pathname:
        raise RuntimeError("blob_upload_invalid_response")
    return {"url": url, "pathname": stored_pathname}


async def download_private_pdf(url: str, token: str) -> tuple[bytes, str | None]:
    _validate_token(token)
    _validate_private_url(url)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"authorization": f"Bearer {token}"},
                follow_redirects=True,
                timeout=_BLOB_TIMEOUT_SECONDS,
            )
        if response.status_code == 404:
            raise FileNotFoundError("blob_not_found")
        response.raise_for_status()
    except FileNotFoundError:
        raise
    except httpx.HTTPError as error:
        raise RuntimeError("blob_download_failed") from error
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("blob_pdf_invalid")
    return response.content, response.headers.get("etag")
