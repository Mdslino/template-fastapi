"""
API v1 router.

This module combines all v1 API routes into a single router.
"""

from fastapi import APIRouter

# Create the main API v1 router
router = APIRouter(prefix='/api/v1')

# Include all route modules
# TODO: Add your routes here

__all__ = ["router"]
