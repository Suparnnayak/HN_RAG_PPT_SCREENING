import pandas as pd
import logging
from pathlib import Path


BASE_DIR = Path(__file__).parent


INPUT_FILE = BASE_DIR / "ranked_results.csv"
OUTPUT_FILE = BASE_DIR / "final_results.xlsx"

logging.basicConfig(
    filename=BASE_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def write_results():
    logging.info("Starting Excel writing process")
    if not INPUT_FILE.exists():
        logging.error(f"Input file not found: {INPUT_FILE}")
        raise FileNotFoundError(f"{INPUT_FILE} not found")

    if INPUT_FILE.stat().st_size == 0:
        logging.error("ranked_results.csv is empty")
        raise ValueError("ranked_results.csv is empty")
    new_df = pd.read_csv(INPUT_FILE)

    required_columns = {"id", "score"}
    if not required_columns.issubset(new_df.columns):
        logging.error("Missing required columns in ranked_results.csv")
        raise ValueError("ranked_results.csv must contain 'id' and 'score'")
    if OUTPUT_FILE.exists():
        existing_df = pd.read_excel(OUTPUT_FILE)

        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        before = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset="id")
        after = len(combined_df)

        logging.info(f"Removed {before - after} duplicate rows while appending")

    else:
        combined_df = new_df
        logging.info("Excel file does not exist. Creating new file")
    combined_df.to_excel(OUTPUT_FILE, index=False)
    logging.info(f"Excel writing completed. Total records: {len(combined_df)}")

    return OUTPUT_FILE


if __name__ == "__main__":
    write_results()
