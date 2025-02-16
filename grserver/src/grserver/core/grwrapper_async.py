import json
import os

import litellm

from grserver.core.common import (convert_to_chat_completions_req, get_config,
                                  outcome_to_stream_response,
                                  outcome_to_stream_response_err)
from grserver.schemas.chat import ChatCompletionsReq
from grserver.telemetry.otel_setup import (trace_async_generator,
                                           trace_calls_async)


@trace_async_generator
async def acompletion_gg(payload_in: ChatCompletionsReq):

    api_key, api_base, model, guard = get_config(payload_in.guard_to_apply)
    open_ai_payload = convert_to_chat_completions_req(payload_in)
    open_ai_payload = open_ai_payload.model_dump()
    input_msgs = payload_in.messages

    try:
        for msg in input_msgs:
            try:
                x = await guard.validate(msg.content)
            except Exception as e:
                print("Input_validation_failed")
                raise ValueError("INPUT_VAL_FAILED\n" + str(e))

        try:

            fragment_generator = await guard(
                litellm.acompletion,
                api_base=api_base,
                api_key=api_key,
                **open_ai_payload,
            )
            if payload_in.stream:
                async for result in fragment_generator:
                    chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
                    yield chunk_string
            else:
                yield fragment_generator.validated_output

        except Exception as e:
            print("output_validation_failed")
            raise ValueError("OUTPUT_VAL_FAILED\n" + str(e))

        # yield str(guard)
    except Exception as e:
        raise e
        # if isinstance(e, guardrails.errors.ValidationError):
        #     error_str  = str(e)
        # else:
        # error_str = str(e)
        # for word in error_str.split():
        #     yield f"data: {json.dumps(outcome_to_stream_response_err(word))}\n\n"

        # yield f"error: {str(e)}\n\n"
