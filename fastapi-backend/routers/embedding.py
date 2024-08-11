import json
from fastapi import FastAPI, File, UploadFile
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.model import EmbeddingModel, get_embedder
from src.vector_db import ingest_document

embedding_router = APIRouter()


class CodeEmbeddingRequest(BaseModel):
    code: str


@embedding_router.post("/generate-embedding")
async def generate_embedding_request(
    request_data: CodeEmbeddingRequest, embedder: EmbeddingModel = Depends(get_embedder)
):
    # Placeholder for processing code and generating embeddings
    # In a real scenario, you would insert the processed code into your vector database here

    # Simulated response
    chunks = request_data.code.split()
    embedding = {
        "embedding": str(embedder.model.encode(chunks)),
        "metadata": {
            "chunked_content": chunks,
        },
    }

    return embedding


@embedding_router.post("/update_context/")
async def rag_embed(
    file: UploadFile = File(...), embedder: EmbeddingModel = Depends(get_embedder)
):
    contents = await file.read()
    context_id = ingest_document(contents, embedder)
    return {"message": "Code processed and stored in chroma"}
