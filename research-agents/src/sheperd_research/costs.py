from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def _token_count(value: object) -> int:
    return int(value) if isinstance(value, (int, float)) else 0

OPENAI_INPUT_USD_PER_MILLION = 0.50
OPENAI_OUTPUT_USD_PER_MILLION = 3.00
TAVILY_SEARCH_CREDITS = 1
TAVILY_EXTRACT_URLS_PER_CREDIT = 5
TAVILY_USD_PER_CREDIT = 0.008
TAVILY_FREE_CREDITS_PER_MONTH = 1_000

# Cost inputs are deliberately explicit and versioned in the generated report.
# These are estimates only; billing must be confirmed against the provider account.
COST_RATE_CARD_RETRIEVED_AT = "2026-08-26"
COST_RATE_CARD: dict[str, object] = {
    "retrieved_at": COST_RATE_CARD_RETRIEVED_AT,
    "openai": {
        "model": "gpt-5.6-luna",
        "input_usd_per_million_tokens": OPENAI_INPUT_USD_PER_MILLION,
        "output_usd_per_million_tokens": OPENAI_OUTPUT_USD_PER_MILLION,
        "source_url": "https://platform.openai.com/pricing",
        "basis": "captured short-context proxy; confirm the configured model rate",
    },
    "tavily": {
        "search_credits_per_call": TAVILY_SEARCH_CREDITS,
        "extract_urls_per_credit": TAVILY_EXTRACT_URLS_PER_CREDIT,
        "usd_per_credit": TAVILY_USD_PER_CREDIT,
        "free_credits_per_month": TAVILY_FREE_CREDITS_PER_MONTH,
        "credits_source_url": "https://docs.tavily.com/documentation/api-credits",
        "pricing_source_url": "https://www.tavily.com/pricing",
    },
    "vercel": {
        "pricing_source_url": "https://vercel.com/pricing",
        "blob_pricing_source_url": "https://vercel.com/docs/vercel-blob/usage-and-pricing",
    },
}


def estimate_llm_cost(
    input_tokens: int,
    output_tokens: int,
    *,
    input_usd_per_million: float = OPENAI_INPUT_USD_PER_MILLION,
    output_usd_per_million: float = OPENAI_OUTPUT_USD_PER_MILLION,
) -> float:
    return round(
        (max(0, input_tokens) / 1_000_000) * input_usd_per_million
        + (max(0, output_tokens) / 1_000_000) * output_usd_per_million,
        6,
    )


def estimate_tavily_cost(
    search_calls: int,
    extracted_urls: int,
    *,
    usd_per_credit: float = TAVILY_USD_PER_CREDIT,
) -> dict[str, int | float]:
    search_credits = max(0, search_calls) * TAVILY_SEARCH_CREDITS
    extract_credits = math.ceil(
        max(0, extracted_urls) / TAVILY_EXTRACT_URLS_PER_CREDIT
    )
    credits = search_credits + extract_credits
    return {
        "search_calls": max(0, search_calls),
        "extracted_urls": max(0, extracted_urls),
        "search_credits": search_credits,
        "extract_credits": extract_credits,
        "credits": credits,
        "estimated_usd": round(credits * usd_per_credit, 6),
        "free_allowance_credits": TAVILY_FREE_CREDITS_PER_MONTH,
    }


def estimate_run_cost(
    steps: Sequence[Mapping[str, object]],
    tool_calls: Sequence[Mapping[str, object]],
    *,
    model: str | None = None,
) -> dict[str, object]:
    input_tokens = sum(
        _token_count(step.get("input_tokens", 0))
        for step in steps
        if isinstance(step.get("input_tokens", 0), (int, float))
    )
    output_tokens = sum(
        _token_count(step.get("output_tokens", 0))
        for step in steps
        if isinstance(step.get("output_tokens", 0), (int, float))
    )
    search_calls = sum(
        _token_count(call.get("calls", 1))
        for call in tool_calls
        if call.get("tool_name") == "tavily_search"
    )
    extracted_urls = sum(
        _token_count(call.get("result_count", call.get("results", 0)))
        for call in tool_calls
        if call.get("tool_name") == "tavily_extract"
        and call.get("status") == "succeeded"
        and isinstance(
            call.get("result_count", call.get("results", 0)), (int, float)
        )
    )
    tavily = estimate_tavily_cost(search_calls, extracted_urls)
    return {
        "model": model or "not recorded",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "llm_estimated_usd": estimate_llm_cost(input_tokens, output_tokens),
        "tavily": tavily,
        "estimated_provider_usd": round(
            estimate_llm_cost(input_tokens, output_tokens)
            + float(tavily["estimated_usd"]),
            6,
        ),
        "rate_card": {
            **COST_RATE_CARD,
        },
    }
