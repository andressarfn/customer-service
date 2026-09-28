from pydantic import BaseModel


class HealthCheckResponseSchema(BaseModel):
    status_code: int
    message: str
