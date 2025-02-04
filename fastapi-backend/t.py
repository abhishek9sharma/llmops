from uuid import UUID

from src.model import get_embedder

embedder = get_embedder()
from src.vector_db import *

doc = "def add"

request_id = UUID("123e4567-e89b-12d3-a456-426655440000")
x = ingest_document(request_id, doc, embedder)
print(x)
