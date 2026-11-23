"""
Feedback form storage: validates a rating, a category and a short message, then appends one row to a CSV file.
No personal data is collected. On Hugging Face Spaces the disk is not permanent, so the file can be reset on restart.
No Streamlit import here, so tests can load it.
"""
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = Path(os.getenv("FEEDBACK_FILE", str(ROOT / "data" / "feedback.csv")))
CATEGORIES = ("bug", "wrong_answer", "idea", "other")
MAX_CHARS = 1000
MIN_CHARS = 5
FIELDS = ["time_utc", "rating", "category", "message"]


def validate(rating, category, message):
    """Returns (ok, code). Codes: rating, category, too_short, too_long."""
    if rating not in (1, 2, 3, 4, 5):
        return False, "rating"
    if category not in CATEGORIES:
        return False, "category"
    message = (message or "").strip()
    if len(message) < MIN_CHARS:
        return False, "too_short"
    if len(message) > MAX_CHARS:
        return False, "too_long"
    return True, ""


def _safe_cell(text):
    """Stops spreadsheet formula injection: a cell that starts with = + - @ gets a leading apostrophe."""
    text = " ".join(str(text).split())
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


def save(rating, category, message, path=None):
    """Appends one feedback row. Returns True on success. Raises ValueError for invalid input."""
    ok, code = validate(rating, category, message)
    if not ok:
        raise ValueError(code)
    path = Path(path) if path else FEEDBACK_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(FIELDS)
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), rating, category, _safe_cell(message.strip())])
    return True
