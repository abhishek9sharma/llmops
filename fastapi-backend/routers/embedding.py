import json
from fastapi import FastAPI, File, UploadFile
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.model import EmbeddingModel, get_embedder
from src.vector_db import ingest_document
from uuid import UUID

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
    request_id: UUID,
    file: UploadFile = File(...),
    embedder: EmbeddingModel = Depends(get_embedder),
):
    try:
        if file is None:
            raise ValueError("File is missing")
        contents = await file.read()
        if not contents:
            raise ValueError("File is empty")
        decoded_contents = contents.decode("utf-8")
        cid = ingest_document(request_id, decoded_contents, embedder)
        return {"message": f"Code processed and stored in chroma CID:{str(cid)} <--> RID:{request_id}"}
    except Exception as e:
        return {"error": str(e)}
