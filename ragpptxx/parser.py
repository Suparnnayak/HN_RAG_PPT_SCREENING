# parser.py
import fitz  # PyMuPDF

def extract_text(pdf_path):
    pages = []
    doc = fitz.open(pdf_path)

    for i, page in enumerate(doc):
        text = page.get_text()
        if text:
            pages.append({
                "page": i + 1,
                "text": text
            })

    doc.close()
    return pages
