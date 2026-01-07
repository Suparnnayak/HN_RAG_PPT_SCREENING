import os
import chromadb

class VectorStore:
    """Manages persistent ChromaDB storage for PPT chunks."""

    def __init__(self, persist_path: str = None, collection_name: str = "ppt_chunks"):
        if persist_path is None:
            # Default to <project_root>/chroma_db
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_path = os.path.join(root, "chroma_db")
            
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[dict], embeddings: list):
        """Adds chunks + embeddings to ChromaDB. Expects 'week' in chunk."""
        if not chunks:
            return

        ids = [f"{c['ppt_id']}_{c['section']}_{c.get('week', 0)}" for c in chunks]
        metadatas = [{
            "ppt_id": c["ppt_id"],
            "team_name": c.get("team_name", ""),
            "section": c["section"],
            "week": c.get("week", 0),
            "page_range": str(c.get("page_range", ""))
        } for c in chunks]
        
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=[c["text"] for c in chunks],
            metadatas=metadatas
        )

    def query_similar(self, embedding: list, n_results: int = 10, where: dict = None):
        """Executes nearest-neighbor search."""
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where
        )
