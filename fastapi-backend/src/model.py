from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")


embedder = EmbeddingModel()


def get_embedder():
    return embedder
