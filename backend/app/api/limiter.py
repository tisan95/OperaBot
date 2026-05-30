"""Rate limiter instance shared across routes."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from app.utils.security import decode_token


def _get_user_id(request: Request) -> str:
    """Use JWT user_id as rate limit key; fall back to IP if unauthenticated."""
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        token = request.cookies.get("access_token")

    if token:
        payload = decode_token(token)
        if payload and payload.get("sub"):
            return payload["sub"]

    return get_remote_address(request)


limiter = Limiter(key_func=_get_user_id)
