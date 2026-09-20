"""
Rule-based emergency detector. Runs BEFORE the LLM.
If a red-flag phrase is found, we show an urgent warning and skip the AI.
"""

EMERGENCY_KEYWORDS = [
    # English
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "trouble breathing", "shortness of breath", "severe bleeding",
    "won't stop bleeding", "unconscious", "passed out", "seizure",
    "throat closing", "swollen tongue", "swollen lips", "swollen face",
    "vomiting blood", "coughing blood", "suicide", "kill myself",
    # Urdu (script)
    "سینے میں درد", "سانس نہیں آ", "سانس لینے میں مشکل", "سانس لینے میں دشواری",
    "بے ہوش", "بیہوش", "شدید خون", "خون بہنا بند نہیں", "دورہ پڑ",
    "گلا بند", "زبان سوج", "ہونٹ سوج", "چہرہ سوج", "خودکشی",
    # Roman Urdu
    "seene mein dard", "saans nahi", "behosh", "khud kushi",
]

MESSAGE_EN = (
    "⚠️ This may be a medical emergency. Please go to the nearest hospital or "
    "call your local emergency number now (in Pakistan: Rescue 1122). "
    "Do not wait for an online answer."
)
MESSAGE_UR = (
    "⚠️ یہ طبی ایمرجنسی ہو سکتی ہے۔ براہ کرم فوراً قریبی ہسپتال جائیں یا "
    "ایمرجنسی سروس (Rescue 1122) پر کال کریں۔ آن لائن جواب کا انتظار نہ کریں۔"
)


def _is_urdu(text: str) -> bool:
    return any("\u0600" <= ch <= "\u06FF" for ch in text)


def check_emergency(text: str) -> str | None:
    """Return an urgent warning message if a red-flag phrase is found, else None."""
    t = text.lower().replace("’", "'")
    if any(keyword in t for keyword in EMERGENCY_KEYWORDS):
        return MESSAGE_UR if _is_urdu(text) else MESSAGE_EN
    return None