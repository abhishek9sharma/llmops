import json
import uuid

import guardrails as gd
import litellm
from fastapi import APIRouter, Request
from guardrails.hub import BanList
from starlette.responses import StreamingResponse

from grserver.core.common import (convert_to_chat_completions_req, get_guards,
                                  outcome_to_stream_response)
from grserver.core.guards import guard_map
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import trace_calls

router = APIRouter()


# @trace_calls
def completion_gg(payload_in: ChatCompletionsReqGuarded, api_key: str):
    guards = get_guards(payload_in.guards_to_apply)
    print("GUARDS", guards)
    api_base = payload_in.org_api_base
    api_key = api_key
    model = payload_in.model
    open_ai_payload = convert_to_chat_completions_req(payload_in)

    # open_ai_payload.model = "gpt-4o-mini" if open_ai_payload.model == "gpt-4" else open_ai_payload.model
    open_ai_payload = open_ai_payload.model_dump()
    print("open_ai_payload", open_ai_payload)
    try:
        for msg in open_ai_payload["messages"]:
            guards.validate(msg["content"])
    except Exception as e:
        error_str = "INPUT_GUARD_FAILED::" + str(e)
        raise ValueError(error_str)

    fragment_generator = guards(
        litellm.completion,
        api_base=api_base,
        api_key=api_key,
        **open_ai_payload,
    )
    print("fragment_generator", fragment_generator)
    return fragment_generator


@router.post("/chat/completions")
def chatcompletion(chat_req: ChatCompletionsReqGuarded, request: Request):
    print("chat_req", chat_req)
    # Extract valies form header
    api_key = request.headers.get("Authorization").replace("Bearer ", "")
    chat_req.model = (
        "deepseek/" + chat_req.model if "deepseek" in chat_req.model else chat_req.model
    )
    ID = str(uuid.uuid4())

    def stream_responses():
        try:
            for result in completion_gg(chat_req, api_key):
                if result.validation_passed:
                    chunk = json.dumps(
                        outcome_to_stream_response(
                            token=str(result.validated_output),
                            ID=ID,
                            model=chat_req.model,
                            validation_outcome=result,
                        )
                    )
                    ystr = f"data: {chunk}\n\n"
                    yield ystr
                else:
                    raise ValueError(f"Validation failed during output")
                # chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
                # yield chunk_string
        except Exception as e:
            print(e)
            error_strs = f"I cannot respond further as Guardrails has failed. Please try again error is: {str(e)}"

            for word in error_strs.split():
                chunk = json.dumps(
                    outcome_to_stream_response(
                        token=word + " ", ID=ID, model=chat_req.model
                    )
                )
                ystr = f"data: {chunk}\n\n"
                yield ystr
        finally:
            # Close the generator
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream_responses(), media_type="text/event-stream")
