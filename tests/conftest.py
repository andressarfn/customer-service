import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-bytes")

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
