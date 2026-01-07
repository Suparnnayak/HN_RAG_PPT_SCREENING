import numpy as np
from .chroma_store import VectorStore

def compute_internal_similarity(store: VectorStore, embedding: np.ndarray, ppt_id: str) -> dict:
    """
    Computes cosine similarity against historical 'idea_problem' chunks.
    Returns numeric metrics only (max, avg_top5, penalty).
    Safe against empty DBs and missing sections.
    """
    ZERO_RESULT = {
        "max_similarity": 0.0,
        "avg_top5_similarity": 0.0,
        "penalty": 0.0,
        "similar_ppt_ids": []
    }

    # Defensive: Empty input or malformed embedding
    if embedding is None or len(embedding) == 0:
        return ZERO_RESULT

    # Ensure list format for Chroma
    query_emb = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding

    try:
        results = store.query_similar(
            embedding=query_emb,
            n_results=10,
            where={
                "$and": [
                    {"section": {"$eq": "idea_problem"}},
                    {"ppt_id": {"$ne": ppt_id}}
                ]
            }
        )
        
        # Check for empty results
        if not results['ids'] or not results['ids'][0]:
            return ZERO_RESULT

        # Chroma returns distance. Similarity = 1 - distance
        distances = results['distances'][0]
        metadatas = results['metadatas'][0]
        
        # Clamp to [0, 1]
        similarities = [max(0.0, min(1.0, 1.0 - d)) for d in distances]
        
        if not similarities:
            return ZERO_RESULT
            
        max_sim = max(similarities)
        
        # Top 5 Avg
        top5 = sorted(similarities, reverse=True)[:5]
        avg_top5 = sum(top5) / len(top5) if top5 else 0.0
        
        # Penalty Rules (Hardcoded)
        if max_sim >= 0.85:
            penalty = 0.25
        elif max_sim >= 0.70:
            penalty = 0.15
        else:
            penalty = 0.0
            
        return {
            "max_similarity": float(max_sim),
            "avg_top5_similarity": float(avg_top5),
            "penalty": float(penalty),
            "similar_ppt_ids": [m.get('ppt_id') for m in metadatas]
        }

    except Exception:
        # Fail gracefully on ANY DB error
        return ZERO_RESULT
