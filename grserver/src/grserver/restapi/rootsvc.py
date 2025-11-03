import asyncio

import httpx
from fastapi import FastAPI

from grserver.restapi.routers import grrouterasync

app = FastAPI()


@app.get("/")
def start_svc():
    return {"Info": "GR Service is running"}


app.include_router(grrouterasync.router, prefix="/guarded")


# @app.on_event("startup")
# async def startup_event():
#     """Send test message to chat completions endpoint on startup"""
#     await asyncio.sleep(10)

#     test_payload = {
#         "model": "tinyllama:1.1b",
#         "messages": [
#             {"role": "user", "content": "Hello, this is a startup test message"}
#         ],
#         "stream": True,
#     }

#     headers = {
#         "Content-Type": "application/json",
#         "apibase": "http://ollama-service:11434/v1/",  # Add if needed
#     }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 "http://localhost:8000/v1/chat/completions",
#                 json=test_payload,
#                 headers=headers,
#             )
#             print(f"Startup test response status: {response.status_code}")
#     except Exception as e:
#         print(f"Startup test failed: {e}")


# ... existing code ...

# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8001)
