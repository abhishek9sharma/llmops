from litellm import completion

guards_to_apply = {
    "banlist": {
        "input": True,
        "output": False,
    }
}


def amethod(v, **kwargs):
    print("method called")
    print(v)
    print(kwargs)
    return "DONE"


print(amethod(v=1, a=2, b=3))

response = completion(
    api_key="sk-e9c0e35c168b4bd69229362bd45b7352",
    api_base="http://localhost:8001/guarded_sync/chat_completions",
    model="deepseek/deepseek-chat",
    messages=[{"role": "user", "content": "yo"}],
    stream=True,
    max_tokens=10,
    #     org_api_base = "https://api.deepseek.com/chat/completions",
    #     guards_to_apply =["BanList"]
)


for chunk in response:
    print(chunk)
    # x = chunk.choices
    # print(type(x))
    # print(x[0].delta.content)

# from guardrails import Guard
# from guardrails.hub import (
#     RegexMatch, BanList
# )
# from guardrails import OnFailAction
# competitors = ["Apple", "Samsung"]
# L = [BanList(banned_words=["codename", "athena"], on_fail=OnFailAction.EXCEPTION),
#     RegexMatch(regex="^[A-Z][a-z]*$")]
# guard = Guard().use_many(*L)
# print(guard)
# #guard.validate("My favorite phone is BlackBerry.")
