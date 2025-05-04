from typing import List, Optional, Set

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionsReq(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 100
    stream: Optional[bool] = True


# class GuardAttrs(BaseModel):
#     input: Optional[bool] = False
#     output: Optional[bool] = False


class Guard(BaseModel):
    name: str


class ChatCompletionsReqGuarded(ChatCompletionsReq):
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    extra_body: Optional[dict] = None
    org_api_base: Optional[str]
    guards_to_apply: Optional[
        Set[str]
    ] = None  # Changed to support nested Guard objects
