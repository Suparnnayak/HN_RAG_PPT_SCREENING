# pipeline.py
import os
from parser import extract_text
from template_extractor import extract_sections
from validator import validate_chunk

SECTIONS = [
    "idea_problem",
    "solution_approach",
    "uniqueness_claim",
    "tech_stack",
    "team_capability"
]

def process_document(pdf_path, team_name, week):
    # TEXT EXTRACTION
    pages = extract_text(pdf_path)

    #  EXTRACTED TEXT
    print("\n=== EXTRACTED TEXT ===")
    for p in pages:
        print(f"\n--- Page {p['page']} ---")
        print(p["text"]) 

    # 2️⃣ METADATA
    ppt_id = os.path.splitext(os.path.basename(pdf_path))[0]

    # 3️⃣ TEMPLATE-BASED SECTION EXTRACTION
    section_texts, page_map = extract_sections(pages)

    # 4️⃣ CHUNK CREATION
    chunks = []

    for section in SECTIONS:
        text = section_texts.get(section)

        if not text:
            text = "[SECTION NOT PROVIDED]"

        chunk = {
            "ppt_id": ppt_id,
            "team_name": team_name,
            "week": week,
            "section": section,
            "page_range": page_map.get(section),
            "text": text
        }

        validate_chunk(chunk)
        chunks.append(chunk)

    return chunks
