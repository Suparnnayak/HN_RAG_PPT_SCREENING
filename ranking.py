import pandas as pd
import logging
from pathlib import Path

# Base directory (folder where this script exists)
BASE_DIR = Path(__file__).parent

# Paths
INPUT_FILE = BASE_DIR / "scores.csv"
OUTPUT_FILE = BASE_DIR / "ranked_results.csv"
TOP_N = 300

# Logger
logging.basicConfig(
    filename=BASE_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def rank_results():
    logging.info("Starting ranking process")

    # Check if input file exists
    if not INPUT_FILE.exists():
        logging.error(f"Input file not found: {INPUT_FILE}")
        raise FileNotFoundError(f"{INPUT_FILE} not found")

    # Check if input file is empty
    if INPUT_FILE.stat().st_size == 0:
        logging.error("Input file is empty")
        raise ValueError("scores.csv is empty")

    # Read CSV
    df = pd.read_csv(INPUT_FILE)

    # Validate required columns
    required_columns = {"id", "score"}
    if not required_columns.issubset(df.columns):
        logging.error("Missing required columns in input file")
        raise ValueError("scores.csv must contain 'id' and 'score' columns")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset="id")
    after = len(df)
    logging.info(f"Removed {before - after} duplicate rows")

    # Sort and select top N
    df = df.sort_values(by="score", ascending=False)
    top_df = df.head(TOP_N)

    # Save output
    top_df.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"Ranking completed. Saved top {len(top_df)} records")

    return OUTPUT_FILE

if __name__ == "__main__":
    rank_results()
