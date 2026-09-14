from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import IdentityVerifyIn, IdentityVerifyOut
from app.services.identity import verify_identity

router = APIRouter(prefix="/api/identity", tags=["identity"])


@router.post("/verify", response_model=IdentityVerifyOut)
async def verify(payload: IdentityVerifyIn, session: AsyncSession = Depends(get_session)) -> IdentityVerifyOut:
    customer = await verify_identity(
        session,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        policy_number=payload.policy_number,
    )
    if customer is None:
        return IdentityVerifyOut(verified=False, message="Identity details did not match a customer record.")
    return IdentityVerifyOut(verified=True, message="Identity verified.", customer=customer)
