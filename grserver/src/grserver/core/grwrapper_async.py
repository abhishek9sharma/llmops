import json
import os

import guardrails
import litellm
import openai
from openai import AsyncOpenAI

from grserver.core.common import (
    convert_to_chat_completions_req,
    get_config,
    outcome_to_stream_response,
    outcome_to_stream_response_err,
)
from grserver.schemas.chat import ChatCompletionsReq
from grserver.telemetry.otel_setup import trace_async_generator, trace_calls_async

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
        try:
            print(f"api_base :{api_base} guards :{guard}")
            if 1:
                fragment_generator = await guard(
                    litellm.acompletion,
                    custom_llm_provider="openai",
                    llm_callable="openai",
                    api_base=api_base,
                    api_key=api_key,
                    **open_ai_payload,
                )
                if payload_in.stream:

                    async for result in fragment_generator:
                        chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
                        # print(result)
                        yield chunk_string
                else:
                    yield fragment_generator.validated_output
            # else:
            #     fragment_generator = await litellm.acompletion(
            #         custom_llm_provider="openai",
            #         llm_callable="openai",
            #         api_base=api_base,
            #         api_key=api_key,
            #         **open_ai_payload,
            #     )
            #     if payload_in.stream:
            #         async for result in fragment_generator:
            #             if hasattr(result, 'choices') and len(result.choices) > 0:
            #                 choice = result.choices[0]
            #                 if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
            #                     content = choice.delta.content
            #                     if content:  # Only yield non-empty content
            #                         yield {"choices": [{"delta": {"content": content}}]}
            #                 elif hasattr(choice, 'text'):
            #                     text = choice.text
            #                     if text:  # Only yield non-empty text
            #                         yield {"choices": [{"delta": {"content": text}}]}
            #             else:
            #                 # Fallback: wrap the result in the expected format
            #                 yield {"choices": [{"delta": {"content": str(result)}}]}
            #     else:
            #         yield fragment_generator

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
