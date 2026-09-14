from fastapi import APIRouter

from app.api.catalog import router as catalog_router
from app.api.chat import router as chat_router
from app.api.claims import router as claims_router
from app.api.health import router as health_router
from app.api.identity import router as identity_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(catalog_router)
api_router.include_router(identity_router)
api_router.include_router(claims_router)
api_router.include_router(chat_router)
