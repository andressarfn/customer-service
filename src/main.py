import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from src.infrastructure.config.settings import settings
from src.infrastructure.database.postgres_client import PostgresConnectionClient
from src.interfaces.api.auth.controller import auth_router
from src.interfaces.api.health_check.controller import health_check_router
from src.interfaces.api.v1.customer.controller import customer_v1_router
from src.interfaces.api.v1.favorite.controller import favorite_v1_router
from src.utils.trace_id import configure_trace_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    await PostgresConnectionClient.initialize(
        settings.DATABASE_URL, settings.DATABASE_SCHEMA, settings.DEBUG
    )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    root_path=settings.ROOT_PATH,
    docs_url="/docs",
    openapi_url="/documentation",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception occurred at %s", request.url, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal Server Error", "error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.error("Validation error occurred at %s", request.url, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Validation Error", "error": str(exc)},
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    logger.error("HTTP error occurred at %s", request.url, exc_info=exc)

    message = "HTTP Error"

    if exc.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND):
        message = "Bad Request"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": message,
            "error": str(exc.detail),
        },
        headers=getattr(exc, "headers", None),
    )


@app.middleware("http")
async def request_middleware(request: Request, call_next: callable):
    request_id = request.headers.get("X-Request-ID")
    trace_id = configure_trace_id(request)

    if not request_id:
        logger.debug("The x-request-id is missing. Creating generic one.")
        request_id = str(uuid.uuid4())

    with logger.contextualize(
        request_id=request_id, trace_id=trace_id, context="APP", route=request.url.path
    ):
        logger.info("Request start")

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id

        logger.info("Request end", status_code=response.status_code)

        return response


app.include_router(health_check_router)
app.include_router(customer_v1_router)
app.include_router(favorite_v1_router)
app.include_router(auth_router)
