from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

import httpx

from ..contracts import PageType, PublicationDateBasis, SourceCandidate
from ..progress import ProgressSink
from ..validators import (
    classify_page_type,
    extract_publication_date,
    normalize_url,
    reconcile_publication_dates,
    url_policy_error,
)
from .errors import ProviderError


class TavilyProvider:
    MAX_EXTRACT_URLS = 20
    DEFAULT_MAX_CONCURRENT_REQUESTS = 2
    DEFAULT_MIN_REQUEST_INTERVAL_SECONDS = 0.0
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
        max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
        min_request_interval_seconds: float = DEFAULT_MIN_REQUEST_INTERVAL_SECONDS,
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
        if max_concurrent_requests < 1:
            raise ValueError("Tavily concurrency must be positive")
        if min_request_interval_seconds < 0:
            raise ValueError("Tavily request interval cannot be negative")
        self._api_keys = keys
        self._project_id = project_id
        self._timeout = timeout_seconds
        self._max_retries = max(0, max_retries)
        self._request_semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._request_pacer = asyncio.Lock()
        self._next_request_at = 0.0
        self._min_request_interval_seconds = min_request_interval_seconds
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

    async def _wait_for_request_slot(self) -> None:
        async with self._request_pacer:
            now = time.monotonic()
            wait_seconds = max(0.0, self._next_request_at - now)
            self._next_request_at = max(now, self._next_request_at) + (
                self._min_request_interval_seconds
            )
        if wait_seconds:
            await asyncio.sleep(wait_seconds)

    async def _post_once(
        self,
        endpoint: str,
        payload: dict[str, object],
        api_key: str,
    ) -> dict[str, object]:
        if self._max_retries:
            raise ProviderError("Tavily retries are disabled by strict policy")
        try:
            await self._wait_for_request_slot()
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
        async with self._request_semaphore:
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
            "search_depth": "advanced" if since is not None or until is not None else "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        if since is not None or until is not None:
            payload["topic"] = "news"
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
            raise ProviderError(
                "Tavily search returned invalid results",
                error_code="malformed_output",
            )
        parsed_sources = []
        for item in results:
            if not isinstance(item, dict):
                raise ProviderError(
                    "Tavily search returned an invalid result entry",
                    error_code="malformed_output",
                )
            parsed_sources.append(self._source_from_result(item, query))
        if self._progress is not None:
            self._progress.emit(
                "query",
                "Tavily search returned sources",
                query=query,
                source_count=len(parsed_sources),
            )
        return parsed_sources

    async def extract(
        self,
        sources: list[SourceCandidate],
        *,
        require_all: bool = True,
    ) -> dict[str, str]:
        urls = [normalize_url(source.url) for source in sources]
        if not urls:
            return {}
        if self._progress is not None:
            self._progress.emit("extract", "Tavily extract", url_count=len(urls))
        extracted: dict[str, str] = {}
        for start in range(0, len(urls), self.MAX_EXTRACT_URLS):
            requested_urls = set(urls[start : start + self.MAX_EXTRACT_URLS])
            data = await self._post(
                "extract",
                {
                    "urls": urls[start : start + self.MAX_EXTRACT_URLS],
                    "extract_depth": "advanced",
                    "format": "markdown",
                    "include_images": False,
                },
            )
            results = data.get("results", [])
            if not isinstance(results, list):
                raise ProviderError(
                    "Tavily extract returned invalid results",
                    error_code="malformed_output",
                )
            for item in results:
                if not isinstance(item, dict):
                    raise ProviderError(
                        "Tavily extract returned an invalid result entry",
                        error_code="malformed_output",
                    )
                url = item.get("url")
                content = item.get("raw_content")
                if not isinstance(url, str) or not isinstance(content, str):
                    raise ProviderError(
                        "Tavily extract returned an invalid result entry",
                        error_code="malformed_output",
                    )
                try:
                    normalized_url = normalize_url(url)
                except ValueError as error:
                    raise ProviderError(
                        "Tavily extract returned a malformed result URL",
                        error_code="malformed_output",
                    ) from error
                if normalized_url not in requested_urls:
                    raise ProviderError(
                        "Tavily extract returned content for an unrequested URL",
                        error_code="malformed_output",
                    )
                if not content.strip():
                    raise ProviderError(
                        "Tavily extract returned blank content",
                        error_code="malformed_output",
                    )
                extracted[normalized_url] = content.strip()
        missing_urls = [url for url in urls if url not in extracted]
        if missing_urls and require_all:
            raise ProviderError(
                f"Tavily extract returned incomplete content for {len(missing_urls)} URL(s)",
                error_code="source_access",
            )
        if self._progress is not None:
            self._progress.emit(
                "extract",
                "Tavily extract returned content",
                url_count=len(extracted),
            )
        return extracted

    async def map(self, url: str) -> list[str]:
        normalized_root = normalize_url(url)
        root_host = (urlsplit(normalized_root).hostname or "").lower().removeprefix("www.")
        data = await self._post(
            "map",
            {
                "url": normalized_root,
                "max_depth": 1,
                "max_breadth": 10,
                "limit": 10,
                "allow_external": False,
            },
        )
        results = data.get("results", [])
        if not isinstance(results, list) or not all(isinstance(item, str) for item in results):
            raise ProviderError(
                "Tavily map returned invalid results",
                error_code="malformed_output",
            )
        mapped: list[str] = []
        for item in results:
            try:
                normalized = normalize_url(item)
            except ValueError:
                continue
            host = (urlsplit(normalized).hostname or "").lower().removeprefix("www.")
            if host != root_host or normalized == normalized_root:
                continue
            if url_policy_error(normalized) is None and normalized not in mapped:
                mapped.append(normalized)
        return mapped[:10]

    async def resolve_sources(
        self,
        sources: list[SourceCandidate],
        content: dict[str, str],
        *,
        since: datetime,
        until: datetime,
    ) -> tuple[list[SourceCandidate], dict[str, str]]:
        """Resolve navigation results to one same-domain direct article each."""
        resolved_sources: list[SourceCandidate] = []
        resolved_content: dict[str, str] = {}
        direct_types = {PageType.ARTICLE, PageType.OFFICIAL_DOCUMENT}
        for source in sources:
            normalized = normalize_url(source.url)
            body = content.get(normalized, "")
            page_type = classify_page_type(source, body)
            page_date, locator = extract_publication_date(body)
            annotated = reconcile_publication_dates(source, page_date, locator).model_copy(
                update={
                    "page_type": page_type,
                    "direct_content": page_type in direct_types,
                }
            )
            if annotated.direct_content:
                resolved_sources.append(annotated)
                resolved_content[normalized] = body
                continue

            mapped_urls = await self.map(normalized)
            if not mapped_urls:
                continue
            child_candidates = [
                source.model_copy(
                    update={
                        "url": child_url,
                        "title": "Resolved article",
                        "publisher": (
                            urlsplit(child_url).hostname or source.publisher
                        ).removeprefix("www."),
                        "published_at": None,
                        "search_published_at": None,
                        "page_published_at": None,
                        "publication_date_basis": PublicationDateBasis.UNKNOWN,
                        "publication_date_locator": None,
                        "page_type": PageType.UNKNOWN,
                        "direct_content": False,
                        "parent_navigation_url": normalized,
                        "source_kind": "resolved-article",
                    }
                )
                for child_url in mapped_urls
            ]
            child_content = await self.extract(child_candidates, require_all=False)
            direct_children: list[tuple[SourceCandidate, str]] = []
            for child in child_candidates:
                child_url = normalize_url(child.url)
                child_body = child_content.get(child_url)
                if child_body is None:
                    continue
                child_page_type = classify_page_type(child, child_body)
                child_page_date, child_locator = extract_publication_date(child_body)
                child = reconcile_publication_dates(
                    child,
                    child_page_date,
                    child_locator,
                ).model_copy(
                    update={
                        "page_type": child_page_type,
                        "direct_content": child_page_type in direct_types,
                    }
                )
                if child.direct_content:
                    direct_children.append((child, child_body))
            if not direct_children:
                continue
            direct_children.sort(
                key=lambda item: (
                    item[0].published_at is not None
                    and since <= item[0].published_at < until,
                    item[0].published_at or datetime.min.replace(tzinfo=UTC),
                    item[0].url,
                ),
                reverse=True,
            )
            selected, selected_body = direct_children[0]
            selected_url = normalize_url(selected.url)
            resolved_sources.append(selected)
            resolved_content[selected_url] = selected_body
        if sources and not resolved_sources:
            raise ProviderError(
                "Tavily map did not resolve a direct article",
                error_code="source_access",
            )
        return resolved_sources, resolved_content

    @staticmethod
    def _source_from_result(item: dict[object, object], query: str) -> SourceCandidate:
        url = item.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ProviderError(
                "Tavily returned an invalid result without a valid URL",
                error_code="malformed_output",
            )
        if url_policy_error(url) is not None:
            raise ProviderError(
                "Tavily returned an invalid result rejected by URL policy",
                error_code="malformed_output",
            )
        try:
            normalized_url = normalize_url(url)
        except ValueError as error:
            raise ProviderError(
                "Tavily returned an invalid result with a malformed URL",
                error_code="malformed_output",
            ) from error
        published_at = TavilyProvider._parse_datetime(item.get("published_date"))
        host = urlsplit(normalized_url).hostname or "unknown"
        return SourceCandidate(
            url=normalized_url,
            title=str(item.get("title") or "Untitled source"),
            publisher=host.removeprefix("www."),
            published_at=published_at,
            search_published_at=published_at,
            publication_date_basis=(
                PublicationDateBasis.SEARCH
                if published_at is not None
                else PublicationDateBasis.UNKNOWN
            ),
            publication_date_locator=(
                "tavily.search.published_date" if published_at is not None else None
            ),
            source_kind="web-discovery",
            snippet=str(item.get("content") or ""),
            topics=[query],
        )

    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            try:
                parsed = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
