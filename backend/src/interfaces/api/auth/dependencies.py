from typing import Annotated

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.interfaces.api.auth.exceptions import AuthenticationException
from src.interfaces.api.auth.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None:
        raise _unauthorized("Your access token is missing.")
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Your access token has expired.")
    except jwt.InvalidTokenError:
        raise _unauthorized("Your access token is invalid.")
    return payload["sub"]


def _unauthorized(detail: str) -> AuthenticationException:
    exception = AuthenticationException(
        title="Unauthorized",
        detail=detail,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    exception.headers = {"WWW-Authenticate": "Bearer"}
    return exception
