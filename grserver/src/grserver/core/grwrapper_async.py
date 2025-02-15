import json
import os

import litellm

from grserver.core.common import (convert_to_chat_completions_req, get_config,
                                  outcome_to_stream_response)
from grserver.schemas.chat import ChatCompletionsReq
from grserver.telemetry.otel_setup import (trace_async_generator,
                                           trace_calls_async)


@trace_async_generator
async def acompletion_gg(payload_in: ChatCompletionsReq):

    api_key, api_base, model, guard = get_config(payload_in.guard_to_apply)
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
            yield str(guard)
            # yield str(result) + "\n"
            # yield "############################################\n\n"
        # close the stream
        yield b"[DONE]"
    except Exception as e:
        # yield f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
        yield f"error: {str(e)}\n\n"
