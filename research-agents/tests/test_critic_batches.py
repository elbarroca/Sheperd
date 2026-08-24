from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sheperd_research.contracts import ClaimDraft, ResearchRunRequest, SourceCandidate
from sheperd_research.db import InMemoryRepository
from sheperd_research.workflow import CRITIC_CLAIM_BATCH_SIZE, ResearchWorkflow


class BatchCritic:
    provider_name = "openai"

    def __init__(self) -> None:
        self.batches: list[list[ClaimDraft]] = []

    async def critic(
        self,
        claims: list[ClaimDraft],
        source_urls: set[str],
        **_: object,
    ) -> list[ClaimDraft]:
        del source_urls
        self.batches.append(list(claims))
        return claims


def test_critic_batches_large_claim_sets_without_dropping_claims() -> None:
    llm = BatchCritic()
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, object(), llm, max_llm_calls=8)
    source = SourceCandidate(url="https://example.com/article")
    claims = [
        ClaimDraft(claim=f"Claim {index}", source_urls=[source.url])
        for index in range(CRITIC_CLAIM_BATCH_SIZE + 1)
    ]
    state = {
        "run_id": "critic-batch-run",
        "request": ResearchRunRequest(
            topic_set="dnd-port",
            as_of=datetime(2026, 8, 20, tzinfo=UTC),
            validation_profile="canary",
        ),
        "topic": ResearchWorkflow(repository, object(), llm).topic_configs["dnd-port"],
        "sources": [source],
        "claims": claims,
        "distillations": [],
        "retained_sources": [],
        "retained_distillations": [],
    }

    result = asyncio.run(workflow._critic(state))

    assert [len(batch) for batch in llm.batches] == [CRITIC_CLAIM_BATCH_SIZE, 1]
    assert len(result["claims"]) == len(claims)
