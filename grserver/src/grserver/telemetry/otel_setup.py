from functools import wraps

from openinference.semconv.trace import SpanAttributes
from opentelemetry import trace
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from phoenix.otel import register  # Phoenix OTEL register function

# Register Phoenix OTEL
tracer_provider = register(
    project_name="arizetest",
    endpoint="http://localhost:6006/v1/traces",
    set_global_tracer_provider=False,
)

# Get tracer
tracer = tracer_provider.get_tracer("my_custom_tracer")


# Helper decorator for tracing method calls
def trace_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__) as guard_span:
            guard_span.set_attribute(
                SpanAttributes.OPENINFERENCE_SPAN_KIND, "GUARDRAIL"
            )
            guard_span.set_attribute("args", str(args))
            guard_span.set_attribute("kwargs", str(kwargs))
            print(f"Tracing {func.__name__} with args: {args} and kwargs: {kwargs}")
            return func(*args, **kwargs)

    return wrapper


def trace_calls_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__) as guard_span:
            guard_span.set_attribute(
                SpanAttributes.OPENINFERENCE_SPAN_KIND, "GUARDRAIL"
            )
            guard_span.set_attribute("args", str(args))
            guard_span.set_attribute("kwargs", str(kwargs))
            print(f"Tracing {func.__name__} with args: {args} and kwargs: {kwargs}")
            return await func(*args, **kwargs)

    return wrapper


def trace_async_generator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__) as guard_span:
            guard_span.set_attribute(
                SpanAttributes.OPENINFERENCE_SPAN_KIND, "GUARDRAIL"
            )
            guard_span.set_attribute("args", str(args))
            guard_span.set_attribute("kwargs", str(kwargs))
            print(f"Tracing {func.__name__} with args: {args} and kwargs: {kwargs}")

            async for item in func(*args, **kwargs):
                yield item

    return wrapper


# # Function to integrate FastAPI with OpenTelemetry
# def configure_otel(app):
#     """Configures FastAPI with OpenTelemetry instrumentation."""
#     FastAPIInstrumentor.instrument_app(app)
