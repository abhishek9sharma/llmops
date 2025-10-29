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
        except Exception as e:
            print("output_validation_failed")
            raise ValueError("OUTPUT_VAL_FAILED\n" + str(e))

    except Exception as e:
        print(e)
        if isinstance(e, guardrails.errors.ValidationError):
            error_str = str(e)
        else:
            if "INPUT_VAL_FAILED" in str(e):
                error_str = " I am sorry I cannot responsd further as I found that your input violates on of of our content guardrails"
            else:
                error_str = str(e)

        for word in error_str.split():
            w = word+" "
            yield f"data: {json.dumps(outcome_to_stream_response_err(w))}\n\n"

        yield f"error: {str(e)}\n\n"
