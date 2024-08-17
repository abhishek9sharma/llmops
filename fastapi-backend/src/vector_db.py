import chromadb
import pandas as pd
from langchain_community.vectorstores import Chroma


def chunk_doc(document):
    return document.split()


def ingest_document(request_id, document, embedder):
    print(document)
    chunks = chunk_doc(document)
    chunk_embeddings = embedder.model.encode(chunks)
    # client = chromadb.PersistentClient(path="temp")
    client = chromadb.HttpClient(
        host="vector-backend",
        port=8000,
        ssl=False
    )
    ids = [f"{request_id}_{i}" for i in range(len(chunks))]
    collection = client.get_or_create_collection(
        name=f"context_{request_id}",
    )
    collection.add(documents=chunks, embeddings=chunk_embeddings, ids=ids)

    return collection.id
