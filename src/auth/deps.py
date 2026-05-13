"""FastAPI dependencies for current-user injection."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from src.auth.firebase import FirebaseUser


async def get_current_user(request: Request) -> FirebaseUser:
    """
    Return the verified Firebase user attached by the auth middleware.

    - 503 if Firebase / network failed (auth_error set by middleware).
    - 401 if no user was attached (bad / missing token).
    - Otherwise: returns the user.
    """
    if getattr(request.state, "auth_error", None) == "service_unavailable":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )
    user: FirebaseUser | None = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


async def get_optional_user(request: Request) -> FirebaseUser | None:
    """
    Return the verified user if present, else None.

    For auth-aware-but-not-required routes. On auth-service outage we still
    return None (graceful) but the caller can inspect request.state.auth_error
    if it wants to react.
    """
    return getattr(request.state, "user", None)


CurrentUser = Annotated[FirebaseUser, Depends(get_current_user)]
OptionalUser = Annotated[FirebaseUser | None, Depends(get_optional_user)]
