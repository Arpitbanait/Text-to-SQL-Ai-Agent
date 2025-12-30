from fastapi import APIRouter
from app.models.response import HealthResponse
from app.config import settings
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check"
)
async def health_check():
    """
    Check if the API is running.
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now()
    )
