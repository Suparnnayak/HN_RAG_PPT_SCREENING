import os
import sys
import argparse

# Allow local imports logic
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "ragpptxx"))

from pipeline import process_document
from embeddings import ChunkEmbedder, VectorStore

"""Ingests a PPT into ChromaDB. Skips duplicates idempotent-ly."""
def ingest_ppt(pdf_path: str, team_name: str, week: int):
    
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        return

    print(f"Processing: {pdf_path}")
    try:
        chunks = process_document(pdf_path, team_name, week)
    except Exception as e:
        print(f"[ERROR] Document processing failed: {e}")
        return

    if not chunks:
        print("[WARN] No chunks extracted.")
        return

    store = VectorStore()
    
    # Pre-calculate IDs: {ppt_id}_{section}_{week}
    chunk_ids = [f"{c['ppt_id']}_{c['section']}_{c['week']}" for c in chunks]
    
    # Check existence in batch
    existing = store.collection.get(ids=chunk_ids)
    existing_ids = set(existing["ids"]) if existing and "ids" in existing else set()
    
    # Filter
    to_embed = []
    for i, chunk in enumerate(chunks):
        if chunk_ids[i] not in existing_ids:
            to_embed.append(chunk)

    if not to_embed:
        print("All chunks exist. Skipping.")
        return

    # Embed & Store
    print(f"Embedding {len(to_embed)} new chunks...")
    embedder = ChunkEmbedder()
    embeddings = embedder.embed([c["text"] for c in to_embed])
    
    store.add_chunks(to_embed, embeddings)
    print(f"Stored {len(to_embed)} chunks successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--week", type=int, required=True)
    args = parser.parse_args()
    
    ingest_ppt(args.file, args.team, args.week)
