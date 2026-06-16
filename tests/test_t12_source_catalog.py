from docqa.domain.t12.source_catalog import list_t12_sources


def test_t12_source_ids_are_unique_and_urls_are_official_https() -> None:
    sources = list_t12_sources()
    source_ids = [source.source_id for source in sources]

    assert len(source_ids) == len(set(source_ids))
    assert all(source.url.startswith("https://") for source in sources)
    assert all(source.checked_on.isoformat() >= "2026-06-15" for source in sources)
    assert any(source.source_id == "guide.avma_petcare" for source in sources)
    assert any(source.source_id == "guide.aspca_poison" for source in sources)


def test_primary_law_sources_are_ready_for_metadata_collection() -> None:
    primary_sources = [
        source for source in list_t12_sources() if source.authority_level == "primary_law"
    ]

    assert len(primary_sources) == 3
    assert all(source.ingestion_status == "metadata_verified" for source in primary_sources)
