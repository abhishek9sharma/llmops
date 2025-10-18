import os

import guardrails as gd
from guardrails import OnFailAction
from guardrails.hub import ProfanityFree

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
def get_config(guards_to_apply: str = None):
    if guards_to_apply is None or guards_to_apply == []:
        # guard_x = gd.AsyncGuard(name="Profanity").use(
        #     ProfanityFree, on_fail=OnFailAction.NOOP
        # )
        return None
    else:
        rq_guards = [guard_map[g] for g in guards_to_apply]
        guard_x = gd.AsyncGuard(name="G").use_many(*rq_guards)
        # print(guard_x)
    print("GUARDS", guards_to_apply, rq_guards)
    return guard_x


def outcome_to_stream_response_err(error_str):
    stream_chunk_template = {
        "choices": [
            {
                "delta": {"content": error_str},
            }
        ],
        "guardrails": {
            "reask": None,
            "validation_passed": False,
            "error": error_str,
        },
    }
    stream_chunk = stream_chunk_template
    stream_chunk["choices"][0]["delta"]["content"] = error_str
    return stream_chunk
