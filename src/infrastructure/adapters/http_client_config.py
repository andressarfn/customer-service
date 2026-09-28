from httpx import AsyncClient, Request, Response

from src.utils.trace_id import trace_id_var


async def trace_id_middleware(request: Request, trace_id: str) -> Request:
    request.headers["X-Trace-ID"] = trace_id
    return request


original_send = AsyncClient.send


async def custom_send(self, request: Request, **kwargs) -> Response:
    trace_id = trace_id_var.get()
    request = await trace_id_middleware(request, trace_id)
    return await original_send(self, request, **kwargs)


AsyncClient.send = custom_send
