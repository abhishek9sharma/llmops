import asyncio
import json

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from grserver.core.common import outcome_to_stream_response_err
from grserver.core.grwrapper_async import acompletion_gg
from grserver.schemas.chat import ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import (trace_async_generator,
                                           trace_calls_async)

router = APIRouter()


@trace_async_generator
async def streamer(chat_req: ChatCompletionsReqGuarded):
    try:
        if chat_req.stream:
            async for result in acompletion_gg(chat_req):
                yield str(result) + "\n"
        else:
            collected = []
            async for result in acompletion_gg(chat_req):
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


@router.post("/chat_acompletions")
async def chatacompletion(chat_req: ChatCompletionsReqGuarded):
    return StreamingResponse(streamer(chat_req), media_type="text/event-stream")
