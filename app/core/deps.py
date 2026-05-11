from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.crud.users import get_user
from app.models.user import User


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user_optional(
    db: DbSession,
    access_token: Annotated[str | None, Cookie()] = None,
) -> User | None:
    if not access_token:
        return None
    payload = decode_access_token(access_token)
    if not payload or "sub" not in payload:
        return None
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        return None
    return get_user(db, user_id)


def get_current_user(user: Annotated[User | None, Depends(get_current_user_optional)]) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
