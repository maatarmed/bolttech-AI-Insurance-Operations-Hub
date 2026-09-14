from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer


async def verify_identity(
    session: AsyncSession,
    *,
    full_name: str,
    date_of_birth: date,
    policy_number: str,
) -> Customer | None:
    result = await session.scalar(
        select(Customer).where(
            func.lower(Customer.full_name) == full_name.strip().lower(),
            Customer.date_of_birth == date_of_birth,
            func.upper(Customer.policy_number) == policy_number.strip().upper(),
        )
    )
    return result
