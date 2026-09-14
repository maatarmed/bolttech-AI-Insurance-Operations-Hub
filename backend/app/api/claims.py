from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Customer
from app.schemas import ClaimCreateIn, ClaimOut
from app.services.claims import create_claim, get_claim_by_number

router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.get("/{claim_number}", response_model=ClaimOut)
async def read_claim(claim_number: str, session: AsyncSession = Depends(get_session)) -> ClaimOut:
    claim = await get_claim_by_number(session, claim_number)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("", response_model=ClaimOut, status_code=201)
async def submit_claim(payload: ClaimCreateIn, session: AsyncSession = Depends(get_session)) -> ClaimOut:
    customer = await session.scalar(select(Customer).where(Customer.policy_number == payload.policy_number.upper()))
    if customer is None:
        raise HTTPException(status_code=404, detail="Unknown policy number")
    return await create_claim(
        session,
        customer=customer,
        incident_date=payload.incident_date,
        incident_type=payload.incident_type,
        description=payload.description,
        location=payload.location,
        estimated_amount=payload.estimated_amount,
    )
