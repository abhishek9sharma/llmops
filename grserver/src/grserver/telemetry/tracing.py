# import os
# from functools import wraps

# # from common import get_tracer_provider
# from openinference.semconv.trace import SpanAttributes
# # Create a reusable tracer from the TracerProvider
# # if get_tracer_provider():
# #     tracer = get_tracer_provider().get_tracer("my_custom_tracer")
# # else:
# #     tracer = None
# from phoenix.otel import register

# # Register a non-global TracerProvider


# PHOENIX_API_KEY = ""
# os.environ["PHONEIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
# tracer_provider = None
# # tracer_provider = register(
# #     project_name="arizetest", endpoint="http://localhost:6006/v1/traces",
# #     set_global_tracer_provider=False)


# def register_tracer():
#     global tracer_provider
#     print("registering tracer")
#     tracer_provider = register(
#         project_name="arizetest", endpoint="http://localhost:6006/v1/traces"
#     )
#     print(tracer_provider)


# # Define the decorator
# def trace_abc(span_kind: str):
#     tracer = tracer_provider.get_tracer("my_custom_tracer")

#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             if tracer is None:
#                 print("tracer not found")
#                 return func(*args, **kwargs)
#             with tracer.start_as_current_span(func.__name__) as span:
#                 try:
#                     span.set_attribute(
#                         SpanAttributes.OPENINFERENCE_SPAN_KIND, "GUARDRAIL"
#                     )
#                     # Pass arguments as span attributes if needed
#                     for i, arg in enumerate(args):
#                         span.set_attribute(f"arg_{i}", str(arg))
#                     for k, v in kwargs.items():
#                         span.set_attribute(f"kwarg_{k}", str(v))

#                     # Call the original function
#                     result = func(*args, **kwargs)

#                     # Optionally log the result or other metadata
#                     span.set_attribute("result", str(result))
#                     return result
#                 except Exception as e:
#                     # Log exceptions as span events
#                     span.record_exception(e)
#                     span.set_status("error")
#                     raise

#         return wrapper

#     return decorator


# # # Example usage of the decorator
# # @trace_span("example_function_span")
# # def example_function(x, y):
# #     return x + y

# # if __name__ == "__main__":
# #     result = example_function(5, 3)
# #     print("Result:", result)
