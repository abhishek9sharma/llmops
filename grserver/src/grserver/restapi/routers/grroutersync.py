import json

import guardrails as gd
import litellm
from fastapi import APIRouter
from guardrails.hub import BanList, LlamaGuard7B, ProfanityFree
from starlette.responses import StreamingResponse

from grserver.core.common import (convert_to_chat_completions_req,
                                  get_config_sync, outcome_to_stream_response,
                                  outcome_to_stream_response_err)
from grserver.core.guards import guard_map
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import trace_calls

router = APIRouter()


@trace_calls
def completion_gg(payload_in: ChatCompletionsReqGuarded):

    api_key, api_base, model, guard = get_config_sync(payload_in.guard_to_apply)
    open_ai_payload = convert_to_chat_completions_req(payload_in)
    open_ai_payload = open_ai_payload.model_dump()
    input_msgs = payload_in.messages

    try:
        for msg in input_msgs:
            print(msg)
            guard.validate(msg.content)
    except Exception as e:
        error_str = str(e)
        return error_str.split(), True

    fragment_generator = guard(
        litellm.completion,
        api_base=api_base,
        api_key=api_key,
        **open_ai_payload,
    )
    return fragment_generator, False
    # except Exception as e:
    #    if isinstance(e, ve):
    #        print(ve)


@router.post("/chat_completions")
def chatcompletion(chat_req: ChatCompletionsReqGuarded):

    if chat_req.stream:

        def stream_responses():
            completion_outcome, error = completion_gg(chat_req)
            for result in completion_outcome:
                if error:
                    chunk_string = f"data: {json.dumps(outcome_to_stream_response_err(result))}\n\n"
                else:
                    chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
                yield chunk_string
                # yield str(result) + "\n"
                # yield "############################################\n\n"

        return StreamingResponse(stream_responses(), media_type="text/event-stream")
    else:
        completion_outcome, error = completion_gg(chat_req)
        if error:
            return " ".join(completion_outcome)
        else:
            res = " ".join([v for v in completion_outcome])
            return res
