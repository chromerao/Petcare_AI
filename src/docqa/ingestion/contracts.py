from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    title: str
    source_type: str
    content: bytes
    media_type: str
    acl: tuple[str, ...]
    version: str


@dataclass(frozen=True)
class NormalizedChunk:
    chunk_id: str
    document_id: str
    text: str
    title: str
    locator: str
    source_type: str
    acl: tuple[str, ...]
    version: str
    content_hash: str


class DocumentSource(Protocol):
    def fetch(self) -> Iterable[SourceDocument]: ...


class DocumentNormalizer(Protocol):
    def normalize(self, document: SourceDocument) -> Iterable[NormalizedChunk]: ...
