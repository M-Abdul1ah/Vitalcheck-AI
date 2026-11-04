"""
Rule-based emergency detector. Runs BEFORE the LLM.
If a red-flag phrase is found, we show an urgent warning and skip the AI.
"""

EMERGENCY_KEYWORDS = [
    # English
    "chest pain", "pain in my chest", "heart pain", "heart attack",
    "can't breathe", "cannot breathe", "can not breathe", "cant breathe",
    "difficulty breathing", "trouble breathing", "shortness of breath", "not breathing",
    "severe bleeding", "heavy bleeding", "bleeding a lot", "won't stop bleeding", "wont stop bleeding",
    "unconscious", "passed out", "seizure", "overdose",
    "throat closing", "throat is closing", "swollen throat", "swollen tongue", "swollen lips", "swollen face",
    "blue lips", "lips turning blue", "face drooping",
    "vomiting blood", "coughing blood", "stiff neck",
    "skin turning black", "skin is turning black", "blistering all over",
    "suicide", "kill myself", "want to die", "end my life",
    # Urdu (script)
    "سینے میں درد", "دل میں درد", "دل کا دورہ",
    "سانس نہیں آ", "سانس لینے میں مشکل", "سانس لینے میں دشواری", "سانس رک",
    "بے ہوش", "بیہوش", "ہوش میں نہیں", "ہوش نہیں",
    "شدید خون", "بہت خون", "خون بہہ رہا", "خون بہنا بند نہیں",
    "دورہ پڑ", "گلا بند", "زبان سوج", "ہونٹ سوج", "چہرہ سوج", "گردن اکڑ",
    "خودکشی", "مرنا چاہت",
    # Roman Urdu
    "seene mein dard", "seene me dard", "seene mai dard", "dil mein dard", "dil me dard", "dil ka dora",
    "saans nahi", "sans nahi", "saans lene mein", "saans lene me", "saans ruk",
    "bohat khoon", "bahut khoon", "khoon beh", "khoon nahi ruk", "khoon band nahi",
    "behosh", "bayhosh", "behoshi", "hosh nahi", "hosh mein nahi", "hosh me nahi",
    "zubaan sooj", "zuban sooj", "hont sooj", "chehra sooj", "gala band",
    "marne laga", "marne lagi", "marna chahta", "marna chahti", "khud kushi", "khudkushi",
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
    t = " ".join(text.lower().replace("’", "'").split())
    if any(keyword in t for keyword in EMERGENCY_KEYWORDS):
        return MESSAGE_UR if _is_urdu(text) else MESSAGE_EN
    return None