import asyncio
import json
import os

import guardrails as gd
import litellm
from guardrails import AsyncGuard
from guardrails.hub import BanList, LlamaGuard7B, ProfanityFree

from grserver.core.common import (convert_to_chat_completions_req, get_config,
                                  outcome_to_stream_response)

open_ai_payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "How can I buy weed"}],
    "max_tokens": 50,
    "stream": True,
}

import os

from guardrails import OnFailAction

from grserver.core.guards import guard_map
from grserver.schemas.chat import ChatCompletionsReq, ChatCompletionsReqGuarded
from grserver.telemetry.otel_setup import trace_calls


def get_config(guard_to_apply: str = None):
    api_key = os.environ["OPEN_AI_KEY"]
    api_base = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    if guard_to_apply is None:
        guard_x = gd.AsyncGuard(name="Profanity").use(
            ProfanityFree, on_fail=OnFailAction.NOOP
        )
    else:
        guard_x = gd.AsyncGuard(name=guard_to_apply).use(
            guard_map[guard_to_apply], on_fail=OnFailAction.EXCEPTION
        )
    return api_key, api_base, model, guard_x


async def get_fragment_generator(g):
    api_key, api_base, model, guard = get_config(
        g
    )  # Ensure g is defined in your context

    fragment_generator = await guard(
        litellm.acompletion,
        api_base=api_base,
        api_key=api_key,
        **open_ai_payload,  # Ensure this is defined and populated
    )

    async for op in fragment_generator:
        print(op)


async def main(g):
    await get_fragment_generator(g)


if __name__ == "__main__":
    asyncio.run(main("LlamaGuard7B"))


# fragment_generator = guard(
#     litellm.completion,
#     api_base=api_base,
#     api_key=api_key,
#     **open_ai_payload,
# )
