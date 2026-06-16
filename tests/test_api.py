from fastapi.testclient import TestClient

from docqa.api.main import app

client = TestClient(app)


def test_health_returns_service_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "DocQA Lab API"


def test_query_returns_grounded_local_answer() -> None:
    response = client.post(
        "/api/v1/query",
        json={"question": "동물이 시설에서 탈출하면 무엇을 해야 하나요?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is True
    assert payload["answer_type"] == "document_grounded"
    assert payload["citations"]
    assert payload["citations"][0]["document_id"] == "internal.04_incident_response"
    assert 0.0 < payload["retrieval_confidence"] < 0.98


def test_query_abstains_when_no_document_matches() -> None:
    response = client.post(
        "/api/v1/query",
        json={"question": "강아지 전용 수영장의 염소 농도는 얼마가 안전한가요?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is False
    assert payload["citations"] == []
    assert payload["answer_type"] == "no_evidence"
    assert payload["retrieval_confidence"] == 0.0
    assert "문서 자료" in payload["answer"]


def test_query_rejects_non_pet_question_even_with_pet_context() -> None:
    response = client.post(
        "/api/v1/query",
        json={
            "question": (
                "오늘 서울 날씨가 어때?\n\n"
                "[상담 대상]\n이름: Bella\n종: 강아지\n품종: 골든 리트리버"
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is False
    assert payload["citations"] == []
    assert payload["answer_type"] == "no_evidence"
    assert payload["retrieval_confidence"] == 0.0
    assert "반려동물과 관련된 증상" in payload["answer"]


def test_query_accepts_ambiguous_symptom_with_pet_context() -> None:
    response = client.post(
        "/api/v1/query",
        json={
            "question": (
                "밥을 안 먹고 계속 토해요\n\n"
                "[상담 대상]\n이름: Bella\n종: 강아지\n품종: 골든 리트리버"
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert (
        payload["answer_type"] != "no_evidence"
        or "반려동물과 관련된 질문" not in payload["answer"]
    )
    assert "반려동물과 관련된 증상" not in payload["answer"]


def test_query_refuses_medication_dosage() -> None:
    response = client.post(
        "/api/v1/query",
        json={"question": "고열이 있는 강아지에게 약을 몇 mg 먹여야 하나요?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is False
    assert payload["generation_mode"] == "safety"
    assert payload["retrieval_confidence"] == 0.0
    assert "수의사" in payload["answer"]


def test_source_catalog_exposes_t12_official_sources() -> None:
    response = client.get("/api/v1/sources")

    assert response.status_code == 200
    payload = response.json()
    assert payload["topic_id"] == "T12"
    assert len(payload["sources"]) >= 7
    assert "law.animal_protection_rule" in {source["source_id"] for source in payload["sources"]}
