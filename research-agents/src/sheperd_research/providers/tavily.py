from __future__ import annotations

from datetime import datetime
from urllib.parse import urlsplit

import httpx

from ..contracts import SourceCandidate
from ..validators import normalize_url
from .errors import ProviderError


class TavilyProvider:
    MAX_EXTRACT_URLS = 20

    def __init__(
        self,
        api_key: str,
        project_id: str | None = None,
        timeout_seconds: float = 45.0,
        max_retries: int = 0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("Tavily API key is required")
        self._api_key = api_key
        self._project_id = project_id
        self._timeout = timeout_seconds
        self._max_retries = max(0, max_retries)

    def _headers(self) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if self._project_id:
            headers["X-Project-ID"] = self._project_id
        return headers

    async def _post(self, endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        if self._max_retries:
            raise ProviderError("Tavily retries are disabled by strict policy")
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"https://api.tavily.com/{endpoint}",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
            data: object = response.json()
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            if status == 429:
                raise ProviderError("Tavily rate limit reached") from error
            raise ProviderError(f"Tavily request failed with status {status}") from error
        except (httpx.TimeoutException, httpx.RequestError, ValueError) as error:
            if isinstance(error, httpx.TimeoutException):
                message = "Tavily request timed out"
            elif isinstance(error, ValueError):
                message = "Tavily returned invalid JSON"
            else:
                message = "Tavily network request failed"
            raise ProviderError(message) from error
        if not isinstance(data, dict) or not all(
            isinstance(key, str) for key in data
        ):
            raise ProviderError("Tavily returned an invalid response")
        return {key: value for key, value in data.items() if isinstance(key, str)}

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
        payload: dict[str, object] = {
            "query": query,
            "search_depth": "advanced",
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
        return [
            self._source_from_result(item, query)
            for item in results
            if isinstance(item, dict)
        ]

    async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
        urls = [normalize_url(source.url) for source in sources]
        if not urls:
            return {}
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
        return extracted

    @staticmethod
    def _source_from_result(item: dict[object, object], query: str) -> SourceCandidate:
        url = item.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ProviderError("Tavily returned a result without a valid URL")
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
