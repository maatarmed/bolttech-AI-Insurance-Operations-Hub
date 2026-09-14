from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.models import Claim, ClaimEvent, Customer, Policy
from app.seed.data import CLAIMS, CUSTOMERS, POLICIES


async def seed_database() -> dict[str, int]:
    async with SessionLocal() as session:
        existing = await session.scalar(select(func.count()).select_from(Customer))
        if existing:
            return {
                "customers": existing,
                "policies": await session.scalar(select(func.count()).select_from(Policy)) or 0,
                "claims": await session.scalar(select(func.count()).select_from(Claim)) or 0,
                "seeded": 0,
            }

        counts = await _insert_seed(session)
        await session.commit()
        return counts


async def _insert_seed(session: AsyncSession) -> dict[str, int]:
    policies: dict[str, Policy] = {}
    for row in POLICIES:
        policy = Policy(**row)
        session.add(policy)
        policies[policy.product_code] = policy
    await session.flush()

    customers: dict[str, Customer] = {}
    for row in CUSTOMERS:
        customer = Customer(**row)
        session.add(customer)
        customers[customer.policy_number] = customer
    await session.flush()

    for row in CLAIMS:
        customer = customers[row["policy_number"]]
        policy = policies[customer.product_code]
        claim = Claim(
            claim_number=row["claim_number"],
            customer_id=customer.id,
            policy_id=policy.id,
            incident_date=row["incident_date"],
            incident_type=row["incident_type"],
            description=row["description"],
            location=row["location"],
            estimated_amount=row["estimated_amount"],
            status=row["status"],
            summary=row["summary"],
        )
        session.add(claim)
        await session.flush()
        for status, note in row["events"]:
            session.add(ClaimEvent(claim_id=claim.id, status=status, note=note))

    return {
        "customers": len(CUSTOMERS),
        "policies": len(POLICIES),
        "claims": len(CLAIMS),
        "seeded": 1,
    }
