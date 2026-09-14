from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Claim, ClaimEvent, Customer, Policy


async def next_claim_number(session: AsyncSession, year: int = 2026) -> str:
    prefix = f"CLM-{year}-"
    latest = await session.scalar(
        select(func.max(Claim.claim_number)).where(Claim.claim_number.like(f"{prefix}%"))
    )
    if not latest:
        return f"{prefix}0001"
    return f"{prefix}{int(latest.rsplit('-', 1)[1]) + 1:04d}"


async def get_claim_by_number(session: AsyncSession, claim_number: str) -> Claim | None:
    return await session.scalar(
        select(Claim)
        .options(selectinload(Claim.customer), selectinload(Claim.policy), selectinload(Claim.events))
        .where(func.upper(Claim.claim_number) == claim_number.strip().upper())
    )


async def list_claims_for_customer(session: AsyncSession, customer_id: str) -> list[Claim]:
    result = await session.scalars(
        select(Claim)
        .options(selectinload(Claim.customer), selectinload(Claim.policy), selectinload(Claim.events))
        .where(Claim.customer_id == customer_id)
        .order_by(Claim.claim_number.desc())
    )
    return list(result)


async def create_claim(
    session: AsyncSession,
    *,
    customer: Customer,
    incident_date: date,
    incident_type: str,
    description: str,
    location: str,
    estimated_amount: Decimal,
) -> Claim:
    policy = await session.scalar(select(Policy).where(Policy.product_code == customer.product_code))
    if policy is None:
        raise ValueError(f"No product registered for {customer.product_code}")
    claim_number = await next_claim_number(session)
    summary = (
        f"Claim {claim_number} submitted for {customer.full_name} ({customer.policy_number}). "
        f"{incident_type.replace('_', ' ')} on {incident_date.isoformat()} at {location}. "
        f"Estimate ${estimated_amount}. Status: submitted."
    )
    claim = Claim(
        claim_number=claim_number,
        customer_id=customer.id,
        policy_id=policy.id,
        incident_date=incident_date,
        incident_type=incident_type,
        description=description,
        location=location,
        estimated_amount=estimated_amount,
        status="submitted",
        summary=summary,
    )
    session.add(claim)
    await session.flush()
    session.add(ClaimEvent(claim_id=claim.id, status="submitted", note="Claim lodged via Operations Hub."))
    await session.commit()
    return await get_claim_by_number(session, claim_number)
