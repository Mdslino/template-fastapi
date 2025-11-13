"""
API v1 router.

This module combines all v1 API routes into a single router.
"""

from fastapi import APIRouter

from app.auth.routes import router as auth_router

# Create the main API v1 router
router = APIRouter(prefix='/api/v1')

# Include all route modules
router.include_router(auth_router, prefix='/auth', tags=['auth'])

__all__ = ["router"]
