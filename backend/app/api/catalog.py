from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Claim, Customer, Policy
from app.schemas import CatalogSummary, ClaimOut, CustomerOut, PolicyOut, PolicySearchHit
from app.services.policies import search_policies

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/catalog", response_model=CatalogSummary)
async def catalog_summary(session: AsyncSession = Depends(get_session)) -> CatalogSummary:
    return CatalogSummary(
        customers=await session.scalar(select(func.count()).select_from(Customer)) or 0,
        policies=await session.scalar(select(func.count()).select_from(Policy)) or 0,
        claims=await session.scalar(select(func.count()).select_from(Claim)) or 0,
    )


@router.get("/policies/search", response_model=list[PolicySearchHit])
async def search_policy_docs(q: str, session: AsyncSession = Depends(get_session)) -> list[PolicySearchHit]:
    matches = await search_policies(session, q)
    return [
        PolicySearchHit(
            product_code=match.policy.product_code,
            name=match.policy.name,
            section=match.section,
            snippet=match.snippet,
            score=match.score,
        )
        for match in matches
    ]


@router.get("/policies", response_model=list[PolicyOut])
async def list_policies(session: AsyncSession = Depends(get_session)) -> list[Policy]:
    result = await session.scalars(select(Policy).order_by(Policy.product_code))
    return list(result)


@router.get("/customers", response_model=list[CustomerOut])
async def list_customers(session: AsyncSession = Depends(get_session)) -> list[Customer]:
    result = await session.scalars(select(Customer).order_by(Customer.full_name))
    return list(result)


@router.get("/claims", response_model=list[ClaimOut])
async def list_claims(session: AsyncSession = Depends(get_session)) -> list[Claim]:
    result = await session.scalars(
        select(Claim)
        .options(
            selectinload(Claim.customer),
            selectinload(Claim.policy),
            selectinload(Claim.events),
        )
        .order_by(Claim.claim_number)
    )
    return list(result)
