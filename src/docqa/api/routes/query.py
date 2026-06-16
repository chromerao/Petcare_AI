from fastapi import APIRouter, HTTPException, status

from docqa.api.schemas import QueryRequest, QueryResponse
from docqa.core.config import get_settings
from docqa.providers.contracts import (
    ProviderConfigurationError,
    ProviderResponseError,
    ProviderTimeoutError,
)
from docqa.rag.query_service import QueryService

router = APIRouter(tags=["query"])
query_service = QueryService(get_settings())


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest) -> QueryResponse:
    try:
        return await query_service.answer(
            request.question,
            generation_mode=request.generation_mode,
        )
    except ProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "provider_not_configured", "message": str(exc)},
        ) from exc
    except ProviderTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"code": "provider_timeout", "message": str(exc)},
        ) from exc
    except ProviderResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "provider_response_error", "message": str(exc)},
        ) from exc
