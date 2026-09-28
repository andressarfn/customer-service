import contextvars
import uuid

trace_id_var = contextvars.ContextVar("trace_id", default=None)


def configure_trace_id(request) -> str:
    trace_id = request.headers.get("X-Trace-ID")
    if not trace_id:
        trace_id = str(uuid.uuid4())
    trace_id_var.set(trace_id)
    return trace_id
