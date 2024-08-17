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
    client = chromadb.HttpClient(host="vector-backend", port=8000, ssl=False)
    ids = [f"{request_id}_{i}" for i in range(len(chunks))]
    collection = client.get_or_create_collection(
        # name=f"context_{request_id}",
        name="code"
    )
    collection.add(documents=chunks, embeddings=chunk_embeddings, ids=ids)

    return collection.id


def get_context(collection_name, query):
    chroma_client = chromadb.HttpClient(host="vector-backend", port=8000, ssl=False)
    collection = chroma_client.get_or_create_collection(name=collection_name)

    results = collection.query(
        query_texts=[query],  # Chroma will embed this for you
        n_results=2,  # how many results to return
    )
    return results
