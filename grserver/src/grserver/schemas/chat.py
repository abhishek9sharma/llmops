from typing import List, Optional

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionsReq(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 100
    stream: Optional[bool] = True


class ChatCompletionsReqGuarded(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 100
    stream: Optional[bool] = True
    guard_to_apply: Optional[str] = None


# data = {
#     "messages": [{"role": "user", "content": "tell me a joke"}],
#     "model": "gpt-4",
#     "max_tokens": 1024,
#     "stream": True,
# }
# x = ChatCompletionsReq(**data)
# print(x)
