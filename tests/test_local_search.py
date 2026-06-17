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


def test_retriever_finds_cat_urinary_care_document() -> None:
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="test-user",
        tenant_id="test-tenant",
        allowed_acl=("public",),
    )

    results = retriever.search(
        "고양이가 화장실을 자주 가는데 소변이 거의 안 나와요",
        context,
        limit=3,
    )

    assert results
    assert results[0].document_id == "care.08_cat_urinary_litterbox"
    assert results[0].source_url is not None


def test_retriever_finds_vet_visit_preparation_document() -> None:
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="test-user",
        tenant_id="test-tenant",
        allowed_acl=("public",),
    )

    results = retriever.search("동물병원 가기 전에 어떤 증상을 기록해야 해?", context, limit=3)

    assert results
    assert results[0].document_id == "care.10_vet_visit_preparation"


def test_retriever_finds_toxic_food_document() -> None:
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="test-user",
        tenant_id="test-tenant",
        allowed_acl=("public",),
    )

    results = retriever.search("dog ate xylitol chocolate grapes", context, limit=3)

    assert results
    assert results[0].document_id == "care.11_aspca_toxic_foods"


def test_retriever_finds_pet_travel_safety_document() -> None:
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="test-user",
        tenant_id="test-tenant",
        allowed_acl=("public",),
    )

    results = retriever.search("pet travel car airplane vaccination documents", context, limit=3)

    assert results
    assert results[0].document_id == "care.15_cdc_pet_travel_safety"


def test_retriever_finds_cat_urinary_obstruction_document() -> None:
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="test-user",
        tenant_id="test-tenant",
        allowed_acl=("public",),
    )

    results = retriever.search("cat cannot pee urinary obstruction emergency", context, limit=3)

    assert results
    assert results[0].document_id == "care.16_cornell_cat_urinary_obstruction"
