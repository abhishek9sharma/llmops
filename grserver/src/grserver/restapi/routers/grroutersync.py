import json

import guardrails as gd
import litellm
from fastapi import APIRouter
from guardrails.hub import BanList, LlamaGuard7B, ProfanityFree
from starlette.responses import StreamingResponse

from grserver.core.common import (convert_to_chat_completions_req,
                                  outcome_to_stream_response)
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import trace_calls

router = APIRouter()

guard_map = {
    "Profanity": ProfanityFree,
    "LlamaGuard7B": LlamaGuard7B,
    "BanList": BanList(banned_words=["codename", "athena"]),
}


@trace_calls
async def get_config_normal(guard_to_apply: str = None):
    api_key = "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"
    api_base = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    if guard_to_apply is None:
        guard = gd.AsyncGuard(name="Profanity").use(ProfanityFree, on_fail="NOOP")
    else:
        guard = gd.AsyncGuard(name=guard_to_apply).use(
            guard_map[guard_to_apply], on_fail="NOOP"
        )
    return api_key, api_base, model, guard


@trace_calls
def completion_gg(payload_in: ChatCompletionsReqGuarded):

    api_key, api_base, model, guard = get_config_normal(payload_in.guard_to_apply)
    open_ai_payload = convert_to_chat_completions_req(payload_in)
    open_ai_payload = open_ai_payload.model_dump()
    fragment_generator = guard(
        litellm.completion,
        api_base=api_base,
        api_key=api_key,
        **open_ai_payload,
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
