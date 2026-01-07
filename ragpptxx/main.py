# main.py
import os
from pipeline import process_document

def process_path(input_path, team_name, week):
    # Case 1: input is a single PDF file
    if os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
        pdfs = [input_path]

    # Case 2: input is a folder containing PDFs
    elif os.path.isdir(input_path):
        pdfs = []
        for file in os.listdir(input_path):
            if file.lower().endswith(".pdf"):
                pdfs.append(os.path.join(input_path, file))

        if not pdfs:
            raise ValueError("No PDF files found in the folder.")

    else:
        raise ValueError("Input path must be a PDF file or a folder containing PDFs.")

    # Process each PDF
    for pdf in pdfs:
        print("\n==============================")
        print(f"PROCESSING: {pdf}")
        print("==============================")

        chunks = process_document(
            pdf_path=pdf,
            team_name=team_name,
            week=week
        )

        print("TOTAL CHUNKS:", len(chunks))
        for c in chunks:
          print("\n---", c["section"], "---")
          print(c)


if __name__ == "__main__":
    # IMPORTANT: this must be a FOLDER containing PDFs
    input_path = "test_pdfs"
    team_name = "test_team"
    week = 1

    process_path(input_path, team_name, week)
