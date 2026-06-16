from docqa.rag.contracts import SearchContext
from docqa.rag.local_search import LocalKeywordRetriever, load_markdown_chunks


def test_markdown_loader_preserves_document_metadata() -> None:
    chunks = load_markdown_chunks()
    document_ids = {chunk.document_id for chunk in chunks}

    assert len(chunks) >= 10
    assert any(document_id.startswith("internal.") for document_id in document_ids)
    assert any(document_id.startswith("care.") for document_id in document_ids)
    assert all(chunk.locator for chunk in chunks)
    assert {"staff", "manager"}.intersection({acl for chunk in chunks for acl in chunk.acl})


def test_retriever_finds_incident_response_for_escape_query() -> None:
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="test-user",
        tenant_id="test-tenant",
        allowed_acl=("staff", "manager"),
    )

    results = retriever.search("동물이 시설에서 탈출했을 때 조치", context, limit=3)

    assert results
    assert results[0].document_id == "internal.04_incident_response"


def test_retriever_applies_acl_filter() -> None:
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="test-user",
        tenant_id="test-tenant",
        allowed_acl=("public",),
    )

    results = retriever.search("입실 확인", context, limit=3)

    assert all(not result.document_id.startswith("internal.") for result in results)
