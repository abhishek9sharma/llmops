import asyncio
import json

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from grserver.core.grwrapper_async import acompletion_gg
from grserver.schemas.chat import ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import (trace_async_generator,
                                           trace_calls_async)

router = APIRouter()


@trace_async_generator
async def streamer(chat_req: ChatCompletionsReqGuarded):
    async for result in acompletion_gg(chat_req):
        yield str(result) + "\n"


@router.post("/chat_acompletions")
async def chatacompletion(chat_req: ChatCompletionsReqGuarded):
    return StreamingResponse(streamer(chat_req), media_type="text/event-stream")
