from typing import Annotated

from fastapi import APIRouter, Body, status
from passlib.hash import bcrypt

from src.infrastructure.config.settings import settings
from src.interfaces.api.auth.exceptions import AuthenticationException
from src.interfaces.api.auth.schemas import LoginRequest, TokenResponse
from src.interfaces.api.auth.security import create_access_token

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# Fake user for demonstration
fake_user = {
    "email": "user@example.com",
    "hashed_password": bcrypt.hash("senha123"),
    "user_id": 1,
}


@auth_router.post(
    "/login",
    description="User login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
)
async def login(
    data: Annotated[LoginRequest, Body(..., description="Login Data")],
) -> TokenResponse:
    # Always verify the password so the response time does not reveal
    # whether the email exists.
    password_matches = bcrypt.verify(data.password, fake_user["hashed_password"])
    if data.email != fake_user["email"] or not password_matches:
        raise AuthenticationException(
            title="Invalid credentials",
            detail="The provided email or password is incorrect.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    token = create_access_token(str(fake_user["user_id"]))
    return TokenResponse(
        access_token=token, expires_in=settings.JWT_EXPIRES_MINUTES * 60
    )
