from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_session
from app.graph import get_graph
from app.models import Claim, Customer, Policy
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="ok", service="backend", env=settings.app_env)


@router.get("/ready", response_model=ReadyResponse)
async def ready(session: AsyncSession = Depends(get_session)) -> ReadyResponse:
    await session.execute(text("SELECT 1"))
    seed = {
        "customers": await session.scalar(select(func.count()).select_from(Customer)) or 0,
        "policies": await session.scalar(select(func.count()).select_from(Policy)) or 0,
        "claims": await session.scalar(select(func.count()).select_from(Claim)) or 0,
    }
    graph_status = "up"
    try:
        get_graph()
    except RuntimeError:
        graph_status = "down"
    return ReadyResponse(status="ok", database="up", seed=seed, graph=graph_status)
