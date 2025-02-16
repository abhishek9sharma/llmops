import time

import guardrails as gd
import litellm
from guardrails.hub import CompetitorCheck

prompt = "Tell me about the Apple Iphone"

guard = gd.Guard().use(CompetitorCheck, ["Apple"])
fragment_generator = guard(
    litellm.completion,
    model="openai/llama3:latest",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about LLM streaming APIs."},
    ],
    max_tokens=100,
    # api_key="",
    api_base="http://localhost:11434/v1",
    temperature=0,
    stream=True,
    max_token=20,
)


for op in fragment_generator:
    print(op)
    time.sleep(0.5)
