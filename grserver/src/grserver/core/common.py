import os

import guardrails as gd
from guardrails import OnFailAction

from grserver.core.guards import guard_map
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import trace_calls


def outcome_to_stream_response(validation_outcome):
    stream_chunk_template = {
        "choices": [
            {
                "delta": {
                    "content": validation_outcome.validated_output,
                },
            }
        ],
        "guardrails": {
            "reask": validation_outcome.reask or None,
            "validation_passed": validation_outcome.validation_passed,
            "error": validation_outcome.error or None,
        },
    }
    stream_chunk = stream_chunk_template
    stream_chunk["choices"][0]["delta"]["content"] = validation_outcome.validated_output
    return stream_chunk


def convert_to_chat_completions_req(
    guarded_req: ChatCompletionsReqGuarded,
) -> ChatCompletionsReq:
    return ChatCompletionsReq(
        model=guarded_req.model,
        messages=guarded_req.messages,
        max_tokens=guarded_req.max_tokens,
        stream=guarded_req.stream,
    )


@trace_calls
def get_config(guard_to_apply: str = None):
    api_key = os.environ["OPEN_AI_KEY"]
    api_base = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    if guard_to_apply is None:
        guard_x = gd.AsyncGuard(name="Profanity").use(
            ProfanityFree, on_fail=OnFailAction.NOOP
        )
    else:
        guard_x = gd.AsyncGuard(name=guard_to_apply).use(
            guard_map[guard_to_apply], on_fail=OnFailAction.EXCEPTION
        )
        # print(guard_x)
    return api_key, api_base, model, guard_x


@trace_calls
def get_config_sync(guard_to_apply: str = None):
    api_key = os.environ["OPEN_AI_KEY"]
    api_base = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    if guard_to_apply is None:
        guard_x = gd.Guard(name="Profanity").use(
            ProfanityFree, on_fail=OnFailAction.NOOP
        )
    else:
        guard_x = gd.Guard(name=guard_to_apply).use(
            guard_map[guard_to_apply], on_fail=OnFailAction.EXCEPTION
        )
        # print(guard_x)
    return api_key, api_base, model, guard_x
