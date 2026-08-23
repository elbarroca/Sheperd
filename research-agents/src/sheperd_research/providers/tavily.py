from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from urllib.parse import urlsplit

import httpx

from ..contracts import SourceCandidate
from ..progress import ProgressSink
from ..validators import normalize_url, url_policy_error
from .errors import ProviderError


class TavilyProvider:
    MAX_EXTRACT_URLS = 20
    ROTATABLE_ERROR_CODES = frozenset(
        {"rate_limit", "plan_usage_limit", "payg_limit", "authentication", "provider_error"}
    )

    def __init__(
        self,
        api_key: str | Sequence[str],
        project_id: str | None = None,
        timeout_seconds: float = 45.0,
        max_retries: int = 0,
        *,
        secondary_api_key: str | None = None,
        progress: ProgressSink | None = None,
    ) -> None:
        configured_keys = [api_key] if isinstance(api_key, str) else list(api_key)
        if secondary_api_key is not None:
            configured_keys.append(secondary_api_key)
        keys = tuple(
            dict.fromkeys(
                key.strip()
                for key in configured_keys
                if isinstance(key, str) and key.strip()
            )
        )
        if not keys:
            raise ValueError("Tavily API key is required")
        self._api_keys = keys
        self._project_id = project_id
        self._timeout = timeout_seconds
        self._max_retries = max(0, max_retries)
        self._progress = progress
        self.call_history: list[dict[str, object]] = []
        self.last_call_metadata: dict[str, object] = {}

    def _headers(self, api_key: str) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {api_key}"}
        if self._project_id:
            headers["X-Project-ID"] = self._project_id
        return headers

    def _record_attempt(
        self,
        *,
        endpoint: str,
        key_slot: int,
        status: str,
        error_code: str | None,
    ) -> dict[str, object]:
        record = {
            "operation": endpoint,
            "key_slot": key_slot,
            "key_count": len(self._api_keys),
            "status": status,
            "error_code": error_code,
        }
        self.last_call_metadata = record
        self.call_history.append(record)
        if self._progress is not None:
            self._progress.emit(
                "route" if key_slot > 1 else "query",
                "Tavily key reroute" if key_slot > 1 else "Tavily request",
                endpoint=endpoint,
                key_slot=key_slot,
                key_count=len(self._api_keys),
                status=status,
                error=error_code or "none",
            )
        return record

    async def _post_once(
        self,
        endpoint: str,
        payload: dict[str, object],
        api_key: str,
    ) -> dict[str, object]:
        if self._max_retries:
            raise ProviderError("Tavily retries are disabled by strict policy")
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"https://api.tavily.com/{endpoint}",
                    headers=self._headers(api_key),
                    json=payload,
                )
                response.raise_for_status()
            data: object = response.json()
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            if status == 429:
                raise ProviderError(
                    "Tavily rate limit reached",
                    error_code="rate_limit",
                ) from error
            if status == 432:
                raise ProviderError(
                    "Tavily plan usage limit reached",
                    error_code="plan_usage_limit",
                ) from error
            if status == 433:
                raise ProviderError(
                    "Tavily pay-as-you-go limit reached",
                    error_code="payg_limit",
                ) from error
            if status in {401, 403}:
                raise ProviderError(
                    "Tavily authentication failed",
                    error_code="authentication",
                ) from error
            if status in {408, 409, 500, 502, 503, 504}:
                raise ProviderError(
                    f"Tavily request failed with status {status}",
                    error_code="provider_unavailable",
                ) from error
            raise ProviderError(
                f"Tavily request failed with status {status}",
                error_code="provider_error",
            ) from error
        except (httpx.TimeoutException, httpx.RequestError, ValueError) as error:
            if isinstance(error, httpx.TimeoutException):
                message = "Tavily request timed out"
                error_code = "timeout"
            elif isinstance(error, ValueError):
                message = "Tavily returned invalid JSON"
                error_code = "malformed_output"
            else:
                message = "Tavily network request failed"
                error_code = "provider_unavailable"
            raise ProviderError(message, error_code=error_code) from error
        if not isinstance(data, dict) or not all(
            isinstance(key, str) for key in data
        ):
            raise ProviderError(
                "Tavily returned an invalid response",
                error_code="malformed_output",
            )
        return {key: value for key, value in data.items() if isinstance(key, str)}

    async def _post(self, endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        errors: list[ProviderError] = []
        for index, api_key in enumerate(self._api_keys):
            key_slot = index + 1
            try:
                data = await self._post_once(endpoint, payload, api_key)
            except ProviderError as error:
                errors.append(error)
                error_code = error.error_code or "provider_error"
                self._record_attempt(
                    endpoint=endpoint,
                    key_slot=key_slot,
                    status="failed",
                    error_code=error_code,
                )
                if (
                    key_slot < len(self._api_keys)
                    and error.error_code in self.ROTATABLE_ERROR_CODES
                ):
                    continue
                if len(errors) > 1:
                    message = "Tavily request failed across configured key slots: " + "; ".join(
                        str(item) for item in errors
                    )
                    raise ProviderError(
                        message,
                        attempts=[dict(item) for item in self.call_history[-len(errors) :]],
                        error_code=error.error_code,
                    ) from error
                raise ProviderError(
                    str(error),
                    attempts=[dict(item) for item in self.call_history[-1:]],
                    error_code=error.error_code,
                ) from error
            self._record_attempt(
                endpoint=endpoint,
                key_slot=key_slot,
                status="succeeded",
                error_code=None,
            )
            return data
        raise ProviderError(
            "Tavily request failed across configured key slots",
            attempts=[dict(item) for item in self.call_history[-len(self._api_keys) :]],
        )

    async def search(
        self,
        query: str,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        max_results: int = 5,
    ) -> list[SourceCandidate]:
        if self._progress is not None:
            self._progress.emit(
                "query",
                "Tavily search",
                query=query,
                max_results=max_results,
            )
        payload: dict[str, object] = {
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        if since:
            payload["start_date"] = since.date().isoformat()
        if until:
            payload["end_date"] = until.date().isoformat()
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        data = await self._post("search", payload)
        results = data.get("results", [])
        if not isinstance(results, list):
            raise ProviderError("Tavily search returned invalid results")
        parsed_sources = [
            self._source_from_result(item, query)
            for item in results
            if isinstance(item, dict)
        ]
        if self._progress is not None:
            self._progress.emit(
                "query",
                "Tavily search returned sources",
                query=query,
                source_count=len(parsed_sources),
            )
        return parsed_sources

    async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
        urls = [normalize_url(source.url) for source in sources]
        if not urls:
            return {}
        if self._progress is not None:
            self._progress.emit("extract", "Tavily extract", url_count=len(urls))
        extracted: dict[str, str] = {}
        for start in range(0, len(urls), self.MAX_EXTRACT_URLS):
            data = await self._post(
                "extract",
                {"urls": urls[start : start + self.MAX_EXTRACT_URLS], "include_images": False},
            )
            results = data.get("results", [])
            if not isinstance(results, list):
                raise ProviderError("Tavily extract returned invalid results")
            for item in results:
                if not isinstance(item, dict):
                    continue
                url = item.get("url")
                content = item.get("raw_content")
                if isinstance(url, str) and isinstance(content, str) and content.strip():
                    extracted[normalize_url(url)] = content.strip()
        missing_urls = [url for url in urls if url not in extracted]
        if missing_urls:
            raise ProviderError(
                "Tavily extract returned incomplete content for: "
                + ", ".join(missing_urls)
            )
        if self._progress is not None:
            self._progress.emit(
                "extract",
                "Tavily extract returned content",
                url_count=len(extracted),
            )
        return extracted

    @staticmethod
    def _source_from_result(item: dict[object, object], query: str) -> SourceCandidate:
        url = item.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ProviderError("Tavily returned a result without a valid URL")
        if url_policy_error(url) is not None:
            raise ProviderError("Tavily returned a source rejected by URL policy")
        published_at = TavilyProvider._parse_datetime(item.get("published_date"))
        host = urlsplit(url).hostname or "unknown"
        return SourceCandidate(
            url=normalize_url(url),
            title=str(item.get("title") or "Untitled source"),
            publisher=host.removeprefix("www."),
            published_at=published_at,
            source_kind="web-discovery",
            snippet=str(item.get("content") or ""),
            topics=[query],
        )

    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
