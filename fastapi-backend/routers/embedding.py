import json
from uuid import UUID

import requests
from fastapi import APIRouter, Depends, FastAPI, File, UploadFile
from pydantic import BaseModel
from src.model import EmbeddingModel, get_embedder
from src.vector_db import chunk_doc, get_context, ingest_document

embedding_router = APIRouter()


class CodeEmbeddingRequest(BaseModel):
    code: str


class QueryVectorDB(BaseModel):
    collection_name: str
    query: str


class CodeContextRequest(BaseModel):
    request_id: UUID
    contents: str


@embedding_router.post("/chunk")
def chunker(data):
    return chunk_doc(data)


@embedding_router.post("/generate-embedding")
async def generate_embedding_request(
    request_data: CodeEmbeddingRequest, embedder: EmbeddingModel = Depends(get_embedder)
):
    # Placeholder for processing code and generating embeddings
    # In a real scenario, you would insert the processed code into your vector database here

    # Simulated response
    chunks = chunker(request_data.code)
    embedding = {
        "embedding": str(embedder.model.encode(chunks)),
        "metadata": {
            "chunked_content": chunks,
        },
    }

    return embedding


@embedding_router.post("/update_context/")
async def update_context(
    # request_id: UUID,
    # file: UploadFile = File(...),
    # contents: str,
    request_data: CodeContextRequest,
    embedder: EmbeddingModel = Depends(get_embedder),
):
    try:
        # if file is None:
        #    raise ValueError("File is missing")
        # contents = await file.read()
        if not request_data.contents:
            raise ValueError("empty")
        # decoded_contents = contents.decode("utf-8")
        collection_name = "code"
        cid = ingest_document(
            request_data.request_id, request_data.contents, embedder, collection_name
        )
        return {
            "message": f"Code processed and stored in chroma collection {collection_name}, CID:{str(cid)} <--> RID:{request_data.request_id}"
        }
    except Exception as e:
        return {"error": str(e)}


@embedding_router.post("/query_collection")
async def update_context(
    # request_id: UUID,
    # file: UploadFile = File(...),
    # contents: str,
    request_data: QueryVectorDB,
):
    return get_context(request_data.collection_name, request_data.query)
