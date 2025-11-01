import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Header
from starlette.responses import StreamingResponse

from grserver.core.common import outcome_to_stream_response_err
from grserver.core.grwrapper_async import acompletion_gg
from grserver.schemas.chat import ChatCompletionsReq
#from grserver.telemetry.otel_setup import trace_async_generator, trace_calls_async

router = APIRouter()



async def streamer(chat_req: ChatCompletionsReq, api_key, api_base, guards):
    try:
        if chat_req.stream:
            async for result in acompletion_gg(chat_req, api_key, api_base, guards):
                yield str(result) + "\n"
        else:
            collected = []
            
            async for result in acompletion_gg(chat_req, api_key, api_base, guards):
                collected.append(str(result) + "\n")
            # yield "HERE\n"
            yield " ".join(collected)
        yield b"[DONE]"

    except Exception as e:
        yield "ERROR\n"
        error_str = str(e)
        if chat_req.stream:
            for word in error_str.split():
                yield f"data: {json.dumps(outcome_to_stream_response_err(word))}\n\n"
        else:
            print(error_str)
            yield error_str
        yield b"[DONE]"


@router.post("/v1/chat/completions")
async def chatacompletion(
    chat_req: ChatCompletionsReq,
    authorization: Optional[str] = Header(None),
    apibase: Optional[str] = Header(None),
    guards: Optional[str] = Header(None),
):
    # Extract API key from Bearer token
    api_key = None
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization[7:]  # Remove "Bearer " prefix

    # Extract API base from header
    extracted_api_base = apibase
    if guards is not None:
        guards = guards.split(",")
    else:
        guards = None
    return StreamingResponse(
        streamer(chat_req, api_key=api_key, api_base=extracted_api_base, guards=guards),
        media_type="text/event-stream",
    )
