# validator.py

REQUIRED_FIELDS = [
    "ppt_id",
    "team_name",
    "week",
    "section",
    "page_range",
    "text"
]

def validate_chunk(chunk):
    for field in REQUIRED_FIELDS:
        if field not in chunk:
            raise ValueError(f"Missing metadata field: {field}")
