import os
import time

import guardrails as gd
from guardrails import OnFailAction
from guardrails.classes import ValidationOutcome
from guardrails.hub import ProfanityFree

from grserver.core.guards import guard_map
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import trace_calls


def outcome_to_stream_response(validation_outcome: ValidationOutcome, ID, model):
    stream_chunk_template = {
        "id": f"chatcmpl-{ID}",  # Added ID field
        "object": "chat.completion.chunk",
        "created": int(time.time()),  # Added created field with current timestamp
        "model": model,
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
    # does this even make sense with a stream? wed need each chunk as theyre emitted
    stream_chunk = stream_chunk_template
    stream_chunk["choices"][0]["delta"]["content"] = validation_outcome.validated_output
    return stream_chunk


def outcome_to_chat_completion(
    validation_outcome: ValidationOutcome,
    llm_response,
    has_tool_gd_tool_call=False,
):
    completion_template = (
        {"choices": [{"message": {"content": ""}}]}
        if not has_tool_gd_tool_call
        else {
            "choices": [{"message": {"tool_calls": [{"function": {"arguments": ""}}]}}]
        }
    )
    completion = getattr(llm_response, "full_raw_llm_output", completion_template)
    completion["guardrails"] = {
        "reask": validation_outcome.reask or None,
        "validation_passed": validation_outcome.validation_passed,
        "error": validation_outcome.error or None,
    }

    # string completion
    try:
        completion["choices"][0]["message"][
            "content"
        ] = validation_outcome.validated_output
    except KeyError:
        pass

    # tool completion
    try:
        choice = completion["choices"][0]
        # if this is accessible it means a tool was called so set our validated output to that
        choice["message"]["tool_calls"][-1]["function"][
            "arguments"
        ] = validation_outcome.validated_output
    except KeyError:
        pass

    return completion


def convert_to_chat_completions_req(
    guarded_req: ChatCompletionsReqGuarded,
) -> ChatCompletionsReq:
    return ChatCompletionsReq(
        model=guarded_req.model,
        messages=guarded_req.messages,
        max_tokens=guarded_req.max_tokens,
        stream=guarded_req.stream,
    )


##@trace_calls
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


##@trace_calls
def get_guards(guards_to_apply=None):
    gL = []
    if guards_to_apply is None:
        guard_x = gd.Guard(name="Profanity").use(
            ProfanityFree, on_fail=OnFailAction.NOOP
        )
    else:
        # for g in guard_to_apply:
        gL = [guard_map[g] for g in guards_to_apply]
        print("gL", gL)
        guard_x = gd.Guard(name="GG").use_many(*gL)
        print("guard_x", guard_x)
        #gL.append(guard_x)
    return guard_x
