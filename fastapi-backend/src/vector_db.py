import chromadb
import pandas as pd
from langchain_community.vectorstores import Chroma


def chunk_doc(document):
    return document.split()


def ingest_document(document, embedder):

    chunks = chunk_doc(document)
    chunk_embeddings = embedder.model.encode(chunks)
    print(chunks, chunk_embeddings)
    client = chromadb.PersistentClient(path="temp")
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection = client.get_or_create_collection(name="code_snippets")
    collection.add(documents=chunks, embeddings=chunk_embeddings, ids=ids)
    return collection
