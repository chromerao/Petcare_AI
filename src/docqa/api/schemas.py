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


class PetProfilePayload(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=120)
    species: str = Field(default="", max_length=80)
    breed: str = Field(default="", max_length=120)
    age: str = Field(default="", max_length=80)
    weight: str = Field(default="", max_length=80)
    status: str = Field(default="", max_length=120)
    vet: str = Field(default="", max_length=200)
    note: str = Field(default="", max_length=2000)
    photoUrl: str = Field(default="", max_length=200_000)


class StoredChatMessage(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=20_000)
    response: dict[str, Any] | None = None


class ChatMessagesPayload(BaseModel):
    pet_id: str | None = Field(default=None, max_length=120)
    session_id: str | None = Field(default=None, max_length=120)
    messages: list[StoredChatMessage]


class ChatSessionPayload(BaseModel):
    id: str | None = Field(default=None, max_length=120)
    title: str = Field(default="New consultation", min_length=1, max_length=160)
    pet_id: str | None = Field(default=None, max_length=120)


class ChatSessionRecord(BaseModel):
    id: str
    title: str
    pet_id: str | None = None
    message_count: int = 0
    created_at: str
    updated_at: str


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
