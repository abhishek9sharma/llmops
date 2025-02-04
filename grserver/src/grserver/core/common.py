def a_call():
    """A function that performs some logic and calls b_call."""
    print("Executing a_call")
    result = b_call()
    return f"a_call -> {result}"


def b_call():
    """A function that performs some logic."""
    print("Executing b_call")
    return "b_call completed"


def check_profanity(msg):
    a_call()
    guard = gd.Guard(name="Profanity").use(ProfanityFree, on_fail="NOOP")
    result = guard.validate(msg)
    return result


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
