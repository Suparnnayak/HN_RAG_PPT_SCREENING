import numpy as np
from sentence_transformers import SentenceTransformer

class ChunkEmbedder:
    """Wraps SentenceTransformer for deterministic, normalized embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        """Generates normalized embeddings. Returns empty array if input is empty."""
        if not texts:
            return np.array([])
        # normalize_embeddings=True ensures cosine similarity via dot product
        return self.model.encode(texts, normalize_embeddings=True)
