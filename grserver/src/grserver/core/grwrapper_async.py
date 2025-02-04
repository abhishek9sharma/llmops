import json

import guardrails as gd
import litellm
from guardrails.hub import ProfanityFree

from grserver.core.common import outcome_to_stream_response
from grserver.schemas.chat import ChatCompletionsReq
from grserver.telemetry.otel_setup import (trace_async_generator,
                                           trace_calls_async)


@trace_calls_async
async def get_config():
    api_key = "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"
    api_base = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    # guard = gd.AsyncGuard(name="Profanity").use(ProfanityFree, on_fail="exception")
    guard = gd.AsyncGuard(name="Profanity").use(ProfanityFree, on_fail="NOOP")

    return api_key, api_base, model, guard


@trace_async_generator
async def acompletion_gg(payload_in: ChatCompletionsReq):

    api_key, api_base, model, guard = await get_config()
    payload = payload_in.model_dump()
    fragment_generator = await guard(
        litellm.acompletion,
        api_base=api_base,
        api_key=api_key,
        **payload,
    )

    async for result in fragment_generator:
        chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
        yield chunk_string
        # yield str(result) + "\n"
        # yield "############################################\n\n"
    # close the stream
    yield b"[DONE]"
