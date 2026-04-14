"""Health routes."""

from fastapi import APIRouter

from app.db.session import SessionDep
from app.health.services.healthcheck import check_health

router = APIRouter(tags=['health'])


@router.get('/healthcheck')
def healthcheck(db: SessionDep) -> dict[str, str]:
    """Application liveness and DB readiness endpoint."""
    return check_health(db)
