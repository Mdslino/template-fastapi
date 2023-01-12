from fastapi import APIRouter

from app.auth.endpoints import router as auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
