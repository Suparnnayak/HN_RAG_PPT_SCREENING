
import os
import sys
import argparse
import json

# Setup import path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "ragpptxx"))

from evaluation import IdeaEvaluator

def run_evaluation(ppt_id: str, model: str):
    """Run evaluation for a given PPT ID."""
    evaluator = IdeaEvaluator(model=model)
    
    print(f"Evaluating PPT ID: {ppt_id} using model: {model}...")
    result = evaluator.evaluate(ppt_id)
    
    print("\n=== EVALUATION REPORT ===")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate PPT Idea using Ollama")
    parser.add_argument("--ppt_id", required=True, help="ID of the PPT to evaluate (must exist in ChromaDB)")
    parser.add_argument("--model", default="tinyllama:latest", help="Ollama model to use")
    
    args = parser.parse_args()
    
    run_evaluation(args.ppt_id, args.model)
