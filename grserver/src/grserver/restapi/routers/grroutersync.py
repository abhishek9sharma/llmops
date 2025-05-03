import json

import guardrails as gd
import litellm
from fastapi import APIRouter
from guardrails.hub import BanList
from starlette.responses import StreamingResponse

from grserver.core.common import (convert_to_chat_completions_req, get_guards,
                                  outcome_to_stream_response)
from grserver.core.guards import guard_map
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import trace_calls

router = APIRouter()


# @trace_calls
def completion_gg(payload_in: ChatCompletionsReqGuarded):

    guards = get_guards(payload_in.guards_to_apply)
    api_base = payload_in.org_api_base
    api_key = payload_in.api_key
    model = payload_in.model
    open_ai_payload = convert_to_chat_completions_req(payload_in)
    open_ai_payload = open_ai_payload.model_dump()

    # try:
    fragment_generator = guards(
        litellm.completion,
        api_base=api_base,
        api_key=api_key,
        **open_ai_payload,
    )
    return fragment_generator


@router.post("/chat_completions")
def chatcompletion(chat_req: ChatCompletionsReqGuarded):
    print("chat_req", chat_req)

    def stream_responses():
        try:
            for result in completion_gg(chat_req):
                chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
                yield chunk_string
        except Exception as e:
            error_response = {"error": str(e), "status_code": 500}
            yield f"data: {json.dumps(error_response)}\n\n"

    return StreamingResponse(stream_responses(), media_type="text/event-stream")
