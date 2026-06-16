import json
from pathlib import Path

from docqa.rag.contracts import SearchContext
from docqa.rag.local_search import LocalKeywordRetriever

EVALUATION_PATH = Path("data/evaluation/t12_seed.jsonl")


def test_seed_questions_return_expected_top_source_or_abstain() -> None:
    rows = [
        json.loads(line)
        for line in EVALUATION_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    retriever = LocalKeywordRetriever()
    context = SearchContext(
        user_id="evaluation-user",
        tenant_id="evaluation",
        allowed_acl=("staff", "manager", "public"),
    )

    for row in rows:
        results = retriever.search(row["question"], context, limit=4)
        expected_ids = row["expected_source_ids"]
        if not expected_ids:
            assert results == [], row["id"]
            continue

        assert results, row["id"]
        assert results[0].document_id in expected_ids, row["id"]
