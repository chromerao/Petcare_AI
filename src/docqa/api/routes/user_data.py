from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from docqa.api.auth import get_current_user_id
from docqa.api.schemas import ChatMessagesPayload, ChatSessionPayload, PetProfilePayload
from docqa.core.config import Settings, get_settings
from docqa.storage.postgres import UserStore

router = APIRouter(tags=["user-data"])


def get_user_store(settings: Annotated[Settings | None, Depends(get_settings)] = None) -> UserStore:
    if settings is None:
        settings = get_settings()
    try:
        store = UserStore(settings)
        store.ensure_schema()
        return store
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "database_not_configured", "message": str(exc)},
        ) from exc


@router.get("/me/pets")
def list_my_pets(
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, list[dict[str, Any]]]:
    if store is None:
        store = get_user_store()
    return {"pets": store.list_pets(user_id)}


@router.post("/me/pets")
def upsert_my_pet(
    payload: PetProfilePayload,
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, dict[str, Any]]:
    if store is None:
        store = get_user_store()
    try:
        pet = store.upsert_pet(user_id, payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "forbidden", "message": str(exc)},
        ) from exc
    return {"pet": pet}


@router.get("/me/messages")
def list_my_messages(
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, list[dict[str, Any]]]:
    if store is None:
        store = get_user_store()
    return {"messages": store.list_messages(user_id)}


@router.put("/me/messages")
def replace_my_messages(
    payload: ChatMessagesPayload,
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, bool]:
    if store is None:
        store = get_user_store()
    store.replace_messages(
        user_id,
        payload.pet_id,
        [message.model_dump() for message in payload.messages],
        payload.session_id or "default",
    )
    return {"ok": True}


@router.get("/me/chat-sessions")
def list_my_chat_sessions(
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, list[dict[str, Any]]]:
    if store is None:
        store = get_user_store()
    return {"sessions": store.list_chat_sessions(user_id)}


@router.post("/me/chat-sessions")
def upsert_my_chat_session(
    payload: ChatSessionPayload,
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, dict[str, Any]]:
    if store is None:
        store = get_user_store()
    session_id = payload.id or "default"
    return {
        "session": store.upsert_chat_session(
            user_id=user_id,
            session_id=session_id,
            title=payload.title,
            pet_id=payload.pet_id,
        )
    }


@router.get("/me/chat-sessions/{session_id}/messages")
def list_my_session_messages(
    session_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, list[dict[str, Any]]]:
    if store is None:
        store = get_user_store()
    return {"messages": store.list_messages(user_id, session_id)}


@router.put("/me/chat-sessions/{session_id}/messages")
def replace_my_session_messages(
    session_id: str,
    payload: ChatMessagesPayload,
    user_id: Annotated[str, Depends(get_current_user_id)] = "",
    store: Annotated[UserStore | None, Depends(get_user_store)] = None,
) -> dict[str, bool]:
    if store is None:
        store = get_user_store()
    store.replace_messages(
        user_id,
        payload.pet_id,
        [message.model_dump() for message in payload.messages],
        session_id,
    )
    return {"ok": True}
