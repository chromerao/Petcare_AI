from docqa.ingestion.contracts import NormalizedChunk, SourceDocument
from docqa.rag.contracts import GroundedAnswer, RetrievedChunk, SearchContext


def test_source_document_preserves_security_metadata() -> None:
    document = SourceDocument(
        document_id="doc-1",
        title="Synthetic safety guide",
        source_type="internal",
        content=b"safe synthetic content",
        media_type="text/plain",
        acl=("team-a",),
        version="v1",
    )

    assert document.acl == ("team-a",)
    assert document.version == "v1"


def test_normalized_chunk_keeps_citation_and_version_fields() -> None:
    chunk = NormalizedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="Use protective equipment.",
        title="Synthetic safety guide",
        locator="page:1",
        source_type="internal",
        acl=("team-a",),
        version="v1",
        content_hash="hash-1",
    )

    assert chunk.locator == "page:1"
    assert chunk.content_hash == "hash-1"


def test_grounded_answer_links_evidence_to_search_context() -> None:
    context = SearchContext(
        user_id="user-1",
        tenant_id="tenant-1",
        allowed_acl=("team-a",),
    )
    evidence = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        title="Synthetic safety guide",
        locator="page:1",
        text="Use protective equipment.",
        score=0.95,
    )
    answer = GroundedAnswer(
        answer="Protective equipment is required.",
        citations=(evidence,),
        grounded=True,
    )

    assert context.allowed_acl == ("team-a",)
    assert answer.citations[0].document_id == "doc-1"
    assert answer.grounded is True
