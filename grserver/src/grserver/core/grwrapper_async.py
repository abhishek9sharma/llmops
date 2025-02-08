import json

import guardrails as gd
import litellm
from guardrails import OnFailAction
from guardrails.hub import BanList, LlamaGuard7B, ProfanityFree

from grserver.core.common import (convert_to_chat_completions_req,
                                  outcome_to_stream_response)
from grserver.schemas.chat import ChatCompletionsReq
from grserver.telemetry.otel_setup import (trace_async_generator,
                                           trace_calls_async)

guard_map = {
    "Profanity": ProfanityFree,
    "LlamaGuard7B": LlamaGuard7B,
    "BanList": BanList(banned_words=["codename", "athena"]),
}


@trace_calls_async
async def get_config(guard_to_apply: str = None):
    api_key = "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"
    api_base = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    if guard_to_apply is None:
        guard = gd.AsyncGuard(name="Profanity").use(
            ProfanityFree, on_fail=OnFailAction.NOOP
        )
    else:
        guard = gd.AsyncGuard(name=guard_to_apply).use(
            guard_map[guard_to_apply], on_fail=OnFailAction.EXCEPTION
        )
    return api_key, api_base, model, guard


@trace_async_generator
async def acompletion_gg(payload_in: ChatCompletionsReq):

    api_key, api_base, model, guard = await get_config(payload_in.guard_to_apply)
    open_ai_payload = convert_to_chat_completions_req(payload_in)
    open_ai_payload = open_ai_payload.model_dump()
    try:
        fragment_generator = await guard(
            litellm.acompletion,
            api_base=api_base,
            api_key=api_key,
            **open_ai_payload,
        )

        async for result in fragment_generator:
            chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
            yield chunk_string
            # yield str(result) + "\n"
            # yield "############################################\n\n"
        # close the stream
        yield b"[DONE]"
    except Exception as e:
        # yield f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
        yield f"error: {str(e)}\n\n"
