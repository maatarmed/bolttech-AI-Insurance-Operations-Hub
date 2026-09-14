from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.config import get_settings
from app.db import Base, engine
from app.models import Claim, ClaimEvent, Customer, Policy  # noqa: F401
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if settings.seed_on_startup:
        await seed_database()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(api_router)
    return app


app = create_app()
