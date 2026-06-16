from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    conversation_id: str | None = Field(default=None, max_length=100)
    filters: dict[str, Any] = Field(default_factory=dict)
    generation_mode: Literal["local", "openai"] = "local"


class Citation(BaseModel):
    document_id: str
    title: str
    locator: str
    source_url: str | None = None
    snippet: str | None = None
    score: float | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    grounded: bool
    request_id: str
    generation_mode: str = "local"
    retrieval_confidence: float = 0.0
    answer_type: str = "document_grounded"
    safety_notice: str | None = None


class SourceRecord(BaseModel):
    source_id: str
    title: str
    publisher: str
    source_kind: str
    authority_level: str
    url: str
    checked_on: date
    ingestion_status: str
    notes: str


class SourceCatalogResponse(BaseModel):
    topic_id: str
    scope: str
    sources: list[SourceRecord]
