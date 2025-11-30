"""
Health Check Router
GET /health endpoint for monitoring
"""

from datetime import datetime

from fastapi import APIRouter

from app.models.chat import HealthResponse

router = APIRouter(
    prefix="",
    tags=["health"],
)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Used by Render/Railway and monitoring tools to verify API is running

    Returns:
        HealthResponse with status and version
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
