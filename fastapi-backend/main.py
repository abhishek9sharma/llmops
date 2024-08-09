from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from routers.embedding import embedding_router
app = FastAPI()

class Message(BaseModel):
    sender: str
    message: str

messages_db = []

@app.post("/messages/", status_code=201)
async def receive_message(message: Message):
    """
    Receive a message from the frontend and store it.
    """
    messages_db.append(message.dict())
    return {"status": "Message received", "message": message.dict()}

@app.get("/messages/", response_model=List[dict])
async def get_messages():
    """
    Retrieve all messages from the storage.
    """
    return messages_db

app.include_router(embedding_router, prefix="/embedding")