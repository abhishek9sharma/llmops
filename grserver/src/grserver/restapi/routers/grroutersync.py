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
    print("payload_in", payload_in.model)
    guards = get_guards(payload_in.guards_to_apply)
    api_base = payload_in.org_api_base
    api_key = api_key
    model = payload_in.model
    open_ai_payload = convert_to_chat_completions_req(payload_in)

    # open_ai_payload.model = "gpt-4o-mini" if open_ai_payload.model == "gpt-4" else open_ai_payload.model
    open_ai_payload = open_ai_payload.model_dump()

    # try:
    fragment_generator = guards(
        litellm.completion,
        api_base=api_base,
        api_key=api_key,
        **open_ai_payload,
    )
    return fragment_generator


@router.post("/chat/completions")
def chatcompletion(chat_req: ChatCompletionsReqGuarded, request: Request):

    # Extract valies form header
    api_key = request.headers.get("Authorization").replace("Bearer ", "")
    chat_req.model = (
        "deepseek/" + chat_req.model if "deepseek" in chat_req.model else chat_req.model
    )
    ID = str(uuid.uuid4())

    def stream_responses():
        try:
            for result in completion_gg(chat_req, api_key):
                chunk = json.dumps(
                    outcome_to_stream_response(
                        validation_outcome=result, ID=ID, model=chat_req.model
                    )
                )
                ystr = f"data: {chunk}\n\n"
                yield ystr
                # chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
                # yield chunk_string
        except Exception as e:
            error_strs = (
                "I cannot respond further as Guardrails has failed. Please try again."
            )
            for word in error_strs.split():
                chunk = json.dumps(
                    outcome_to_stream_response(
                        validation_outcome=result, ID=ID, model=chat_req.model
                    )
                )
                ystr = f"data: {chunk}\n\n"
                yield ystr
        finally:
            # Close the generator
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream_responses(), media_type="text/event-stream")
