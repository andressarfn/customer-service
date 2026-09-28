from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder


@dataclass
class CustomException(Exception):
    title: str
    detail: Any | None = None
    traceback: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_type": "CustomerServiceEventError",
            "params": {
                "exc_type": self.__class__.__name__,
                "exc_title": self.title,
                "exc_detail": self.detail,
                "exc_traceback": self.traceback,
            },
        }

    def __str__(self) -> str:
        return f"{self.title}: {self.detail}" if self.detail else self.title


@dataclass
class CustomHttpException(HTTPException):
    title: str
    status_code: int
    detail: Any | None = None
    traceback: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_type": "CustomerServiceEventError",
            "params": {
                "exc_type": self.__class__.__name__,
                "exc_title": self.title,
                "exc_code": self.status_code,
                "exc_detail": self.detail,
                "exc_traceback": self.traceback,
            },
        }

    def as_json(self) -> dict[str, Any]:
        return {
            "status_code": self.status_code,
            "content": jsonable_encoder(
                {
                    "title": self.title,
                    "detail": self.detail,
                }
            ),
        }
