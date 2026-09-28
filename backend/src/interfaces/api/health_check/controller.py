from fastapi import APIRouter, status

from src.interfaces.api.health_check.schema import HealthCheckResponseSchema

health_check_router = APIRouter(tags=["Health Check"])


@health_check_router.get("/ready", response_model=HealthCheckResponseSchema)
async def health_check():
    return HealthCheckResponseSchema(status_code=status.HTTP_200_OK, message="OK")
