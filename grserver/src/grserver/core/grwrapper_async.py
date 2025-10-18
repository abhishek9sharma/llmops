import json
import os

import guardrails
import litellm
import openai
from openai import AsyncOpenAI

from grserver.core.common import (convert_to_chat_completions_req, get_config,
                                  outcome_to_stream_response,
                                  outcome_to_stream_response_err)
from grserver.schemas.chat import ChatCompletionsReq
from grserver.telemetry.otel_setup import (trace_async_generator,
                                           trace_calls_async)

# fragment_generator = await guard(
#     #litellm.acompletion,
#     #llm_callable="openai",
#     #api_base=api_base,
#     #api_key=api_key,
#     client.chat.completions.create,
#     **open_ai_payload,
# )


@trace_async_generator
async def acompletion_gg(payload_in: ChatCompletionsReq, api_key, api_base, guards):
    guard = get_config(guards)
    open_ai_payload = convert_to_chat_completions_req(payload_in)
    open_ai_payload = open_ai_payload.model_dump()
    input_msgs = payload_in.messages
    client = AsyncOpenAI(api_key=api_key, base_url=api_base)

    try:
        # Validate input messages if guard is present
        if guard is not None:
            for msg in input_msgs:
                try:
                    await guard.validate(msg.content)
                except Exception as e:
                    print("Input_validation_failed")
                    raise ValueError("INPUT_VAL_FAILED\n" + str(e))

        # Define streaming callable
        # FIXME
        async def openai_streaming_callable(**kwargs):
            kwargs["stream"] = True
            stream = await client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    # Extract and print the content from the current chunk
                    content = chunk.choices[0].delta.content
                    yield content

        # Define non-streaming callable
        async def openai_callable(**kwargs):
            kwargs["stream"] = False
            response = await client.chat.completions.create(**kwargs)
            return response.choices[0].message.content

        try:
            # Choose callable based on streaming preference
            callable_func = (
                openai_streaming_callable if payload_in.stream else openai_callable
            )

            if guard:
                # Use guardrails validation
                if payload_in.stream:
                    print("HXH")
                    if api_key == "ollama":
                        open_ai_payload["model"] = f"openai/{payload_in.model}"
                    fragment_generator = await guard(
                        litellm.acompletion,
                        llm_callable="openai",
                        api_base=api_base,
                        api_key=api_key,
                        **open_ai_payload,
                    )
                    async for result in fragment_generator:
                        chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
                        print(result)
                        yield chunk_string
                else:
                    fragment_generator = await guard(
                        callable_func,
                        **open_ai_payload,
                    )
                    yield fragment_generator.validated_output
            else:
                # Direct OpenAI call without guardrails
                if payload_in.stream:
                    async for chunk in callable_func(**open_ai_payload):
                        chunk_string = f"data: {json.dumps(outcome_to_stream_response(content=chunk))}\n\n"
                        yield chunk_string
                else:
                    result = await callable_func(**open_ai_payload)
                    yield result

        except Exception as e:
            print("output_validation_failed")
            raise ValueError("OUTPUT_VAL_FAILED\n" + str(e))

    except Exception as e:
        print(e)
        if isinstance(e, guardrails.errors.ValidationError):
            error_str = str(e)
        else:
            error_str = str(e)

        for word in error_str.split():
            yield f"data: {json.dumps(outcome_to_stream_response_err(word))}\n\n"

        yield f"error: {str(e)}\n\n"
