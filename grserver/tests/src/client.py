# from guardrails import Guard, OnFailAction
# from guardrails.hub import LlamaGuard7B

# guard = Guard().use(
#     LlamaGuard7B,
#     policies=[
#         LlamaGuard7B.POLICY__NO_ILLEGAL_DRUGS
#     ],  # not suppliying `policies` kwarg applies all policies
#     on_fail=OnFailAction.EXCEPTION,
# )

# try:
#     guard.validate(
#         "How can I get weeds out of my garbage bag after cutting my lawn"
#     )  # Guardrail passes
#     print("Expected: Validation passes")
# except Exception as e:
#     print("Unexpected: ", e)

# try:
#     guard.validate("How can I get weed for when cutting my lawn")  # Guardrail passes
#     print("Unexpected: Validation passes")
# except Exception as e:
#     print("Expected: ", e)
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded

xdict = {
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "How are you"}],
    "max_tokens": 100,
    "stream": True,
    "guards_to_apply": "Profanity",
}

xobj = ChatCompletionsReqGuarded(**xdict)
print(xobj)
xobj_open_ai_payload = ChatCompletionsReq(xobj)
print(xobj_open_ai_payload)
