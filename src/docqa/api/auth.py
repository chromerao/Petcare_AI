from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status

from docqa.core.config import Settings, get_settings


def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    settings: Annotated[Settings | None, Depends(get_settings)] = None,
) -> str:
    if settings is None:
        settings = get_settings()
    if not settings.supabase_auth_configured or settings.supabase_jwt_secret is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "auth_not_configured",
                "message": "Supabase JWT secret is not configured.",
            },
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "missing_token", "message": "Missing bearer token."},
        )

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_token", "message": "Invalid authentication token."},
        ) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_token", "message": "Authentication token has no subject."},
        )
    return subject
