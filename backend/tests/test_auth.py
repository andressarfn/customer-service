from datetime import datetime, timedelta, timezone

import jwt
import pytest

from src.application.use_cases.customer.get import GetCustomerUseCase
from src.domain.entities.customer_entity import CustomerOutputEntity
from src.infrastructure.config.settings import settings
from src.infrastructure.database.postgres_client import PostgresConnectionClient
from src.interfaces.api.auth.security import create_access_token, decode_access_token
from src.main import app

PROTECTED_ROUTES = [
    ("post", "/v1/customer"),
    ("get", "/v1/customer/1"),
    ("patch", "/v1/customer/1"),
    ("delete", "/v1/customer/1"),
    ("post", "/v1/customer/1/favorite"),
    ("get", "/v1/customer/1/favorites"),
]


def _token(**overrides) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": "1", "iat": now, "exp": now + timedelta(minutes=5)}
    payload.update(overrides)
    payload = {key: value for key, value in payload.items() if value is not None}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def test_login_returns_token_with_expiration(client):
    response = client.post(
        "/auth/login", json={"email": "user@example.com", "password": "senha123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings.JWT_EXPIRES_MINUTES * 60
    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == "1"
    assert payload["exp"] - payload["iat"] == settings.JWT_EXPIRES_MINUTES * 60


@pytest.mark.parametrize(
    "email, password",
    [("user@example.com", "wrong"), ("other@example.com", "senha123")],
)
def test_login_rejects_invalid_credentials(client, email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})

    assert response.status_code == 401


@pytest.mark.parametrize("method, path", PROTECTED_ROUTES)
def test_protected_route_without_token_returns_401(client, method, path):
    response = client.request(method, path)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        _token(exp=datetime.now(timezone.utc) - timedelta(minutes=1)),
        jwt.encode(
            {"sub": "1", "iat": datetime.now(timezone.utc), "exp": 9999999999},
            "another-secret-key-with-at-least-32-bytes",
            algorithm="HS256",
        ),
        _token(exp=None),
        _token(sub=None),
    ],
    ids=["malformed", "expired", "wrong-signature", "without-exp", "without-sub"],
)
@pytest.mark.parametrize("method, path", PROTECTED_ROUTES)
def test_protected_route_with_bad_token_returns_401(client, method, path, token):
    response = client.request(
        method, path, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_valid_token_reaches_the_route(client, monkeypatch):
    async def fake_session():
        yield None

    async def fake_execute(self, customer_id):
        return CustomerOutputEntity(customer_id=customer_id, name="Ana")

    app.dependency_overrides[PostgresConnectionClient.session] = fake_session
    monkeypatch.setattr(GetCustomerUseCase, "execute", fake_execute)
    token = create_access_token("1")

    try:
        response = client.get(
            "/v1/customer/1", headers={"Authorization": f"Bearer {token}"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"customer_id": 1, "name": "Ana"}
