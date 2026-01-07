import os
import sys
import argparse
import json


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "ragpptxx"))

from pipeline import process_document
from embeddings import ChunkEmbedder, VectorStore, compute_internal_similarity

def check_ppt_similarity(pdf_path: str, team_name: str, week: int):
    """Safe, read-only internal similarity check."""
    if not os.path.exists(pdf_path):
        print(json.dumps({"error": "File not found"}))
        return

    try:
        chunks = process_document(pdf_path, team_name, week)
    except Exception:
        print(json.dumps({"error": "Processing failed"}))
        return

    # Find 'idea_problem'
    idea_chunk = next((c for c in chunks if c["section"] == "idea_problem"), None)
    
    # Graceful exit if no section
    if not idea_chunk or not idea_chunk["text"].strip() or idea_chunk["text"] == "[SECTION NOT PROVIDED]":
        print(json.dumps({
            "max_similarity": 0.0,
            "avg_top5_similarity": 0.0,
            "penalty": 0.0,
            "similar_ppt_ids": []
        }, indent=2))
        return

    # Embed & Compute
    try:
        embedder = ChunkEmbedder()
        embedding = embedder.embed([idea_chunk["text"]])[0]
        
        store = VectorStore()
        result = compute_internal_similarity(store, embedding, idea_chunk["ppt_id"])
        
        print("\n=== SIMILARITY RESULTS ===")
        print(json.dumps(result, indent=2))
        
    except Exception:
        # Fallback for unexpected failures
        print(json.dumps({
            "max_similarity": 0.0,
            "penalty": 0.0,
            "error": "Computation failed"
        }, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--week", type=int, required=True)
    args = parser.parse_args()
    
    check_ppt_similarity(args.file, args.team, args.week)
