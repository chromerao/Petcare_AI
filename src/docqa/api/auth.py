from typing import Annotated

import httpx
import jwt
from fastapi import Depends, Header, HTTPException, status

from docqa.core.config import Settings, get_settings


def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    settings: Annotated[Settings | None, Depends(get_settings)] = None,
) -> str:
    if settings is None:
        settings = get_settings()
    if not settings.supabase_auth_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "auth_not_configured",
                "message": "Supabase authentication is not configured.",
            },
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "missing_token", "message": "Missing bearer token."},
        )

    token = authorization.removeprefix("Bearer ").strip()
    subject = _decode_subject_with_jwt_secret(token, settings)
    if subject is None:
        subject = _fetch_subject_from_supabase(token, settings)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_token", "message": "Invalid authentication token."},
        )
    return subject


def _decode_subject_with_jwt_secret(token: str, settings: Settings) -> str | None:
    if settings.supabase_jwt_secret is None:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        return None

    subject = payload.get("sub")
    return subject if isinstance(subject, str) and subject else None


def _fetch_subject_from_supabase(token: str, settings: Settings) -> str | None:
    if settings.supabase_url is None or settings.supabase_publishable_key is None:
        return None

    base_url = settings.supabase_url.rstrip("/")
    try:
        response = httpx.get(
            f"{base_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_publishable_key.get_secret_value(),
            },
            timeout=5.0,
        )
    except httpx.HTTPError:
        return None

    if response.status_code != status.HTTP_200_OK:
        return None

    payload = response.json()
    subject = payload.get("id")
    return subject if isinstance(subject, str) and subject else None
