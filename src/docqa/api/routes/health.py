from fastapi import APIRouter

from docqa.api.schemas import HealthResponse
from docqa.core.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )
