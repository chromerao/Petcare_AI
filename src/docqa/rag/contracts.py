from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SearchContext:
    user_id: str
    tenant_id: str
    allowed_acl: tuple[str, ...]


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    title: str
    locator: str
    text: str
    score: float
    source_url: str | None = None


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: tuple[RetrievedChunk, ...]
    grounded: bool


class Retriever(Protocol):
    def search(
        self,
        query: str,
        context: SearchContext,
        *,
        limit: int,
    ) -> list[RetrievedChunk]: ...


class AnswerGenerator(Protocol):
    def generate(self, question: str, evidence: list[RetrievedChunk]) -> GroundedAnswer: ...
