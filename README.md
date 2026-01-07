# HN RAG PPT Screening System

An AI-powered screening tool designed to evaluate hackathon slides (PDFs) based on clarity, feasibility, uniqueness, and team capability. The system uses **Retrieval Augmented Generation (RAG)** to analyze specific sections of a presentation and compares the "Uniqueness" of the idea against a localized vector database of all previous submissions.

## 🚀 Features

- **Strict Section Extraction**: Enforces mandatory sections (`idea_problem`, `solution_approach`, `uniqueness_claim`, `tech_stack`, `team_capability`).
- **Internal Knowledge Base**: Vector store (ChromaDB) to check for duplicates and assess novelty.
- **Weighted AI Evaluation**:
    - **40% Uniqueness** (Database Similarity + LLM Analysis)
    - **20% Problem Clarity**
    - **15% Solution Quality**
    - **15% Technical Feasibility**
    - **10% Team Capability**
- **Calibrated Scoring**: Hard limits on AI scores to prevent inflation (e.g., max 8/10 for clarity).
- **Offline Capable**: Uses local Ollama models (default `tinyllama`).

---

## 🛠️ Setup

### Prerequisites
1.  **Python 3.10+**
2.  **Ollama**: Install from [ollama.ai](https://ollama.ai/)
    ```bash
    ollama serve
    ollama pull tinyllama
    ```

### Installation
Clone the repository and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*(Note: Ensure `numpy`, `chromadb`, `sentence-transformers`, `requests` are available)*

---

## 📖 Usage

### 1. Ingest Submissions
Parse PDFs, generate embeddings, and store them in the local database.

```bash
python3 scripts/ingestion.py \
    --file path/to/presentation.pdf \
    --team "Team Name" \
    --week 1
```
*   **Result**: Stores chunks in `chroma_db/`. Skips if already ingested.
*   **Error**: Fails if mandatory sections are missing in the PDF.

### 2. Quick Similarity Check
Check how similar a new PDF is to the existing database without ingesting it.

```bash
python3 scripts/check_similarity.py \
    --file path/to/presentation.pdf \
    --team "Team Name" \
    --week 1
```

### 3. Run AI Evaluation
Generate a comprehensive score and report for a stored PPT.

```bash
python3 scripts/evaluate_ppt.py --ppt_id <ppt_id>
```
*   `ppt_id` is the filename without extension (e.g., `sample` for `sample.pdf`).
*   **Default Model**: `tinyllama:latest`.
*   **Custom Model**:
    ```bash
    python3 scripts/evaluate_ppt.py --ppt_id sample --model mistral:7b-instruct-q4_K_M
    ```

---

## 📊 Evaluation Logic

### Scoring Weights
| Criterion | Weight | Max Score (Calibrated) | Description |
| :--- | :--- | :--- | :--- |
| **Uniqueness** | **40%** | 10.0 | `(1 - Similarity) * 8` + LLM Adjustment (±2) |
| **Problem Clarity** | 20% | 8.0 | Is the problem specific and well-defined? |
| **Solution Quality** | 15% | 8.0 | Is the solution logical and effective? |
| **Tech Feasibility** | 15% | 8.0 | Is the stack realistic for the team/scope? |
| **Team Capability** | 10% | 7.0 | Does the team have the right skills? |

### Anti-Inflation Measures
- **Clamping**: Sub-scores are strictly capped (mostly at 8.0) to prevent AI from giving 10/10 easily.
- **Penalty**: Uniqueness is mathematically derived first (`1 - max_similarity`), only adjusted slightly by the LLM.
- **Data Integrity**: Missing metadata or sections results in a hard failure, ensuring no "empty" evaluations.

---

## 📂 Project Structure

```text
├── chroma_db/              # Persistent Vector Database
├── embeddings/
│   ├── embedder.py         # SentenceTransformer wrapper
│   ├── chroma_store.py     # ChromaDB interface
│   └── similarity.py       # Uniqueness logic engine
├── evaluation/
│   └── evaluator.py        # Core RAG Evaluator (Ollama Client)
├── scripts/
│   ├── ingestion.py        # ETL Script
│   ├── check_similarity.py # Read-only Utility
│   └── evaluate_ppt.py     # Evaluation CLI
├── test_pdfs/              # Sample inputs
└── requirements.txt
```

---

## ❓ Troubleshooting

**Q: "Missing sections for..." error?**
A: The PDF parsing failed to find one of the 5 mandatory headers. Retrying usually won't help; the PDF content needs to match the expected format (Header: Text).

**Q: Ollama connection error?**
A: Ensure `ollama serve` is running in another terminal.

**Q: "Evaluator unavailable (LLM error)" in scores?**
A: The LLM timed out (limit: 180s) or crashed. Try a smaller model (`tinyllama`) or restart Ollama.
