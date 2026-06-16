from fastapi import APIRouter

from docqa.api.schemas import SourceCatalogResponse, SourceRecord
from docqa.domain.t12.source_catalog import list_t12_sources

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=SourceCatalogResponse)
def source_catalog() -> SourceCatalogResponse:
    sources = [
        SourceRecord.model_validate(source, from_attributes=True) for source in list_t12_sources()
    ]
    return SourceCatalogResponse(
        topic_id="T12",
        scope="반려동물 보호자 케어와 반려견·반려묘 호텔/유치원 운영",
        sources=sources,
    )
