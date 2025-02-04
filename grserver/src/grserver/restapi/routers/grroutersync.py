import json

import guardrails as gd
import litellm
from fastapi import APIRouter
from guardrails.hub import ProfanityFree
from starlette.responses import StreamingResponse

from grserver.core.common import outcome_to_stream_response
from grserver.schemas.chat import ChatCompletionsReq
from grserver.telemetry.otel_setup import trace_calls

router = APIRouter()


@trace_calls
def get_config_normal():
    api_key = "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"
    api_base = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    # guard = gd.AsyncGuard(name="Profanity").use(ProfanityFree, on_fail="exception")
    guard = gd.Guard(name="Profanity").use(ProfanityFree, on_fail="NOOP")

    return api_key, api_base, model, guard


@trace_calls
def completion_gg(payload_in: ChatCompletionsReq):

    api_key, api_base, model, guard = get_config_normal()
    payload = payload_in.model_dump()
    fragment_generator = guard(
        litellm.completion,
        api_base=api_base,
        api_key=api_key,
        **payload,
    )
    return fragment_generator


@router.post("/chat_completions")
def chatcompletion(chat_req: ChatCompletionsReq):
    def stream_responses():
        for result in completion_gg(chat_req):
            chunk_string = f"data: {json.dumps(outcome_to_stream_response(validation_outcome=result))}\n\n"
            yield chunk_string
            yield str(result) + "\n"
            yield "############################################\n\n"

    return StreamingResponse(stream_responses(), media_type="text/event-stream")
