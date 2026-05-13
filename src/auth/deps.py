"""FastAPI dependencies for current-user injection."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from src.auth.firebase import FirebaseUser


async def get_current_user(request: Request) -> FirebaseUser:
    """
    Return the verified Firebase user attached by the auth middleware.

    Raises 401 if no user was attached (middleware found no valid token).
    """
    user: FirebaseUser | None = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


async def get_optional_user(request: Request) -> FirebaseUser | None:
    """Return the verified user if present, else None (for public + auth-aware routes)."""
    return getattr(request.state, "user", None)


CurrentUser = Annotated[FirebaseUser, Depends(get_current_user)]
OptionalUser = Annotated[FirebaseUser | None, Depends(get_optional_user)]
