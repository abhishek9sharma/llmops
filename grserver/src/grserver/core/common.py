from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded


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
