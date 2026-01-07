import json
import logging
import requests
from embeddings import VectorStore, ChunkEmbedder, compute_internal_similarity

PROMPT_BASE = """You are a hackathon idea evaluator.

You will be given:
1. Extracted content from a single team’s submission
2. A scoring criterion

Rules:
- Do NOT assume missing information
- Penalize vague, generic, or marketing-style language
- Be conservative in scoring
- Output STRICT JSON only
- Score from 0 to 10 (integers only)

Context:
{retrieved_chunks}

Criterion:
{criterion_description}

Return JSON:
{{
  "score": <int>,
  "reason": "<short, factual justification>"
}}"""

PROMPT_CLARITY = """Criterion: Clarity and effort of explanation.

Instructions:
- Penalize generic phrases (e.g. “revolutionary”, “cutting-edge”)
- Reward concrete constraints, scope, users, or data
- If language is vague or polished without substance, score low
- Do NOT judge grammar or writing style

Score from 0 to 10.
Return STRICT JSON.
{{
  "score": <int>,
  "reason": "<short, factual justification>"
}}"""

PROMPT_UNIQUENESS = """You are evaluating idea uniqueness.

Inputs:
1. Current team’s idea description
2. Summaries of similar existing ideas

Task:
Classify novelty as:
a) Near-duplicate
b) Common hackathon idea
c) Novel variation
d) Highly original

Rules:
- Do NOT penalize common problems
- Focus on solution differentiation
- Do NOT reject ideas

Return JSON:
{{
  "novelty_category": "a | b | c | d",
  "score_adjustment": 0,
  "reason": "..."
}}

CURRENT IDEA:
{current_idea}

SIMILAR IDEAS:
{similar_ideas}
"""

class IdeaEvaluator:
    """Evaluates a single PPT using RAG and internal similarity."""
    
    def __init__(self, model="tinyllama:latest", ollama_url="http://localhost:11434"):
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"
        self.store = VectorStore()
        self.embedder = ChunkEmbedder()

    def _call_ollama(self, prompt, retries=3):
        """Generic Ollama caller with JSON enforcement."""
        payload = {
            "model": self.model, "prompt": prompt, "stream": False, "format": "json",
            "options": {"num_ctx": 2048, "temperature": 0.1}
        }
        for _ in range(retries):
            try:
                resp = requests.post(self.api_url, json=payload, timeout=90)
                resp.raise_for_status()
                return json.loads(resp.json().get("response", "{}"))
            except Exception:
                continue
        return None

    def evaluate(self, ppt_id: str):
        """Main evaluation flow."""
        # 1. Retrieve & Validate
        results = self.store.collection.get(where={"ppt_id": ppt_id}, include=["documents", "metadatas"])
        chunks = {}
        if results and results["metadatas"]:
            for i, meta in enumerate(results["metadatas"]):
                if isinstance(meta, dict):
                    chunks[meta["section"]] = {**meta, "text": results["documents"][i]}
        
        required = ["idea_problem", "solution_approach", "uniqueness_claim", "tech_stack", "team_capability"]
        if missing := [s for s in required if s not in chunks]:
            raise ValueError(f"Missing sections for {ppt_id}: {missing}")

        final_scores, explanations = {}, {}
        fail_msg = "Evaluator unavailable (LLM error)"

        # 2. Evaluate Criteria (Batched Config)
        criteria = [
            ("problem_clarity", chunks["idea_problem"]["text"], PROMPT_CLARITY, 8.0),
            ("solution_quality", chunks["solution_approach"]["text"], "Assess solution logic, depth, and feasibility.", 8.0),
            ("technical_feasibility", chunks["tech_stack"]["text"], "Assess technical feasibility and stack realism.", 8.0),
            ("team_capability", chunks["team_capability"]["text"], "Assess team skills to execute the idea.", 7.0),
        ]

        for key, text, desc, max_score in criteria:
            res = self._call_ollama(PROMPT_BASE.format(retrieved_chunks=text, criterion_description=desc)) or \
                  {"score": 0, "reason": fail_msg}
            final_scores[key] = min(res.get("score", 0), max_score)
            explanations[key] = res.get("reason", "N/A")

        # 3. Evaluate Uniqueness
        emb = self.embedder.embed([chunks["idea_problem"]["text"]])[0]
        sim_stats = compute_internal_similarity(self.store, emb, ppt_id)
        
        # Base: (1 - max_sim) * 8.0
        base_uniq = max(0.0, (1.0 - sim_stats["max_similarity"]) * 8.0)
        
        # Adjustment Context
        sim_text = "No similar ideas found."
        if ids := sim_stats.get("similar_ppt_ids", [])[:3]:
            # Optimistic fetch of similar ideas
            # Note: Ideally batch fetch, but here strictly ensuring efficiency
            if docs := self.store.collection.get(where={"$and": [{"ppt_id": {"$in": ids}}, {"section": "idea_problem"}]})["documents"]:
                sim_text = "\n---\n".join(docs)

        uniq_res = self._call_ollama(PROMPT_UNIQUENESS.format(
            current_idea=f"{chunks['idea_problem']['text']}\n{chunks['uniqueness_claim']['text']}",
            similar_ideas=sim_text
        )) or {"score_adjustment": 0, "reason": fail_msg}

        # Adjustment: Clamp -2 to +2
        adj = max(-2, min(2, uniq_res.get("score_adjustment", 0)))
        final_scores["uniqueness"] = round(max(0, min(10, base_uniq + adj)), 1)
        explanations["uniqueness"] = uniq_res.get("reason", "N/A")

        # 4. Total Calculation
        # Weights: Uniq 40, Clarity 20, Sol 15, Tech 15, Team 10
        total = (final_scores["uniqueness"] * 4.0 +
                 final_scores["problem_clarity"] * 2.0 +
                 final_scores["solution_quality"] * 1.5 +
                 final_scores["technical_feasibility"] * 1.5 +
                 final_scores["team_capability"] * 1.0)

        return {
            "ppt_id": ppt_id,
            "team_name": chunks["idea_problem"].get("team_name", ""),
            "week": chunks["idea_problem"].get("week", 0),
            "scores": final_scores,
            "total_score": round(total, 1),
            "explanation": explanations
        }
