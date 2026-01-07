# template_extractor.py
import re
from templates import SECTION_TEMPLATES

def extract_sections(pages):
    section_texts = {}
    page_map = {}

    # initialize
    for section in SECTION_TEMPLATES:
        section_texts[section] = ""
        page_map[section] = []

    for page in pages:
        page_num = page["page"]
        text = page["text"].lower()

        for section, patterns in SECTION_TEMPLATES.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    section_texts[section] += page["text"] + "\n"
                    page_map[section].append(page_num)
                    break

    # convert page list → range string
    page_range_map = {}
    for section, pages_list in page_map.items():
        if not pages_list:
            page_range_map[section] = None
        else:
            start = min(pages_list)
            end = max(pages_list)
            page_range_map[section] = (
                str(start) if start == end else f"{start}-{end}"
            )

    return section_texts, page_range_map
