import os

import guardrails as gd
from guardrails import OnFailAction

from grserver.core.guards import guard_map
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import  trace_error


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



def get_config(guards_to_apply: str = None):
    if guards_to_apply is None or guards_to_apply == []:
        # guard_x = gd.AsyncGuard(name="Profanity").use(
        #     ProfanityFree, on_fail=OnFailAction.NOOP
        # )
        rq_guards = []
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


@trace_error
def get_guardrail_violation_message(failed_at: str, guard_failed: str = "UNKNOWN", failed_content = "UNKNOWN") -> str:
    """Generate a guardrail violation message.
    
    Args:
        failed_at: The point where the guardrail violation occurred
        guard_failed: Specific guardrail that failed (optional)
    
    Returns:
        Formatted violation message
    """
    if guard_failed is None:
        return f"I am sorry I cannot respond further as I found that {failed_at} violates one of our content guardrails"
    else:
        return f"I am sorry I cannot respond further as I found that {failed_at} violates one of our content guardrails: {guard_failed}"



def get_guardrail_error_details(hist, failed_at):
    """Extract guardrail error message from validation logs."""

    if hist.last.failed_validations.last.validation_result.validated_chunk:
        failed_content = hist.last.failed_validations.last.validation_result.validated_chunk
    else:
        failed_content = "unknown"
    
    if hist.last.failed_validations.validator_name:
        guard_failed = hist.last.failed_validations.last.validator_name
    else:
        guard_failed = "unknown"


    # for v in hist.last.validator_logs:
    #     if v.validation_result.outcome == "fail" \
    #         and v.value_after_validation is None:#=="":
    #             guard_failed = v.validator_name
    #             failed_content = v.value_before_validation
    #             break
    
    return get_guardrail_violation_message(failed_at, guard_failed, failed_content)