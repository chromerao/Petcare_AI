from typing import Any

from fastapi.testclient import TestClient

from docqa.api.auth import get_current_user_id
from docqa.api.main import app
from docqa.api.routes.user_data import get_user_store


class FakeUserStore:
    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []
        self.session = {
            "id": "session-1",
            "title": "초기 상담",
            "pet_id": "bella",
            "message_count": 0,
            "created_at": "2026-06-17T00:00:00+00:00",
            "updated_at": "2026-06-17T00:00:00+00:00",
        }

    def list_pets(self, user_id: str) -> list[dict[str, Any]]:
        assert user_id == "user-1"
        return []

    def upsert_pet(self, user_id: str, pet: dict[str, Any]) -> dict[str, Any]:
        assert user_id == "user-1"
        return pet

    def list_messages(self, user_id: str, session_id: str = "default") -> list[dict[str, Any]]:
        assert user_id == "user-1"
        assert session_id in {"default", "session-1"}
        return self.messages

    def replace_messages(
        self,
        user_id: str,
        pet_id: str | None,
        messages: list[dict[str, Any]],
        session_id: str = "default",
    ) -> None:
        assert user_id == "user-1"
        assert pet_id == "bella"
        assert session_id == "session-1"
        self.messages = messages
        self.session["message_count"] = len(messages)

    def list_chat_sessions(self, user_id: str) -> list[dict[str, Any]]:
        assert user_id == "user-1"
        return [self.session]

    def upsert_chat_session(
        self,
        user_id: str,
        session_id: str,
        title: str,
        pet_id: str | None,
    ) -> dict[str, Any]:
        assert user_id == "user-1"
        self.session = {
            **self.session,
            "id": session_id,
            "title": title,
            "pet_id": pet_id,
        }
        return self.session


def test_user_data_chat_session_endpoints() -> None:
    store = FakeUserStore()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_user_store] = lambda: store
    client = TestClient(app)

    try:
        session_response = client.post(
            "/api/v1/me/chat-sessions",
            json={"id": "session-1", "title": "구토 상담", "pet_id": "bella"},
        )
        assert session_response.status_code == 200
        assert session_response.json()["session"]["title"] == "구토 상담"

        list_response = client.get("/api/v1/me/chat-sessions")
        assert list_response.status_code == 200
        assert list_response.json()["sessions"][0]["id"] == "session-1"

        save_response = client.put(
            "/api/v1/me/chat-sessions/session-1/messages",
            json={
                "pet_id": "bella",
                "messages": [{"id": "m1", "role": "user", "content": "구토했어요"}],
            },
        )
        assert save_response.status_code == 200

        messages_response = client.get("/api/v1/me/chat-sessions/session-1/messages")
        assert messages_response.status_code == 200
        assert messages_response.json()["messages"][0]["content"] == "구토했어요"
    finally:
        app.dependency_overrides.clear()
