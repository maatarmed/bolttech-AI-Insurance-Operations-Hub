from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Policy

SECTION_WEIGHTS = {
    "coverage_text": 3,
    "exclusions": 3,
    "limitations": 2,
    "name": 2,
}


@dataclass
class PolicyMatch:
    policy: Policy
    score: int
    section: str
    snippet: str


def score_policy(policy: Policy, query: str) -> PolicyMatch | None:
    terms = [term for term in query.lower().split() if len(term) > 2]
    if not terms:
        return None
    best = PolicyMatch(policy=policy, score=0, section="coverage_text", snippet=policy.coverage_text[:280])
    for field, weight in SECTION_WEIGHTS.items():
        text = getattr(policy, field)
        lowered = text.lower()
        hits = sum(1 for term in terms if term in lowered)
        score = hits * weight
        if policy.product_code.lower() in query.lower():
            score += 5
        if f"product {policy.product_code.lower()}" in query.lower():
            score += 8
        if score > best.score:
            best = PolicyMatch(policy=policy, score=score, section=field, snippet=text[:320])
    return best if best.score else None


async def search_policies(session: AsyncSession, query: str, limit: int = 3) -> list[PolicyMatch]:
    policies = list(await session.scalars(select(Policy)))
    ranked = [match for policy in policies if (match := score_policy(policy, query))]
    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:limit]
