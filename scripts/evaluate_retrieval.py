"""Evaluate retrieval recall against the versioned T12 seed questions."""

import json
from pathlib import Path

from docqa.rag.contracts import SearchContext
from docqa.rag.local_search import LocalKeywordRetriever

EVALUATION_PATH = Path("data/evaluation/t12_seed.jsonl")


def main() -> None:
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
    hit_count = 0

    print("ID       HIT   TOP RESULTS")
    for row in rows:
        results = retriever.search(row["question"], context, limit=4)
        result_ids = [result.document_id for result in results]
        expected_ids = row["expected_source_ids"]
        hit = not expected_ids and not results or bool(set(expected_ids).intersection(result_ids))
        hit_count += int(hit)
        top_results = ", ".join(
            f"{result.document_id}({result.score:.2f})" for result in results[:3]
        )
        print(f"{row['id']:<8} {str(hit):<5} {top_results or '-'}")

    recall = hit_count / len(rows) if rows else 0.0
    print(f"\nRecall@4: {hit_count}/{len(rows)} ({recall:.1%})")


if __name__ == "__main__":
    main()
