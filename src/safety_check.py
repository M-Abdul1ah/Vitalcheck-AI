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
    "skin turning black", "skin is turning black", "skin has turned black", "skin turned black",
    "skin is black", "turning black", "blistering all over",
    "chest hurts", "chest is hurting", "chest is paining", "chest tightness", "tight chest", "pressure in my chest",
    "swelling of my face", "swelling of the face", "swelling in my face", "face swelling", "face is swollen",
    "swelling of my tongue", "swelling of my lips", "swelling of my throat", "tongue swelling", "lip swelling",
    "neck is stiff", "neck stiffness", "stiffness in my neck",
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
    "seene mein jalan", "seena dukh", "seena dard", "chehra soj", "chehre par soojan", "chehre pe soojan",
    "gardan akar", "gardan akad", "gardan sakht", "jild kali", "jild kaali",
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


# Combination rules: a rash together with a serious sign is a red flag, even when no exact phrase matches.
RASH_WORDS = ["rash", "spots", "blisters", "hives", "دانے", "خارش", "چھالے", "dane", "daney", "chhale", "chale", "khujli"]
SEVERE_FEVER = [
    "high fever", "very high fever", "severe fever", "fever and chills", "fever with chills",
    "تیز بخار", "شدید بخار", "بہت بخار",
    "tez bukhar", "bohat bukhar", "bahut bukhar", "shadeed bukhar", "shadid bukhar",
]


import re

# Pattern rules catch wording variants a phrase list misses ("chest hurt", "chest is aching", "heart hurting").
# Only a body part directly followed by a pain word is flagged, so "pimples on my chest" is not.
PATTERNS = [
    re.compile(r"\b(chest|heart)\s+(is\s+|feels\s+|has\s+been\s+|was\s+)?"
               r"(hurt|hurts|hurting|ache|aches|aching|pain|pains|paining|tight|tightness|burning|heavy)\b"),
    re.compile(r"\bpains?\s+(in|on|around)\s+(my\s+|the\s+)?(chest|heart)\b"),
]


def check_emergency(text: str) -> str | None:
    """Return an urgent warning message if a red-flag phrase is found, else None."""
    t = " ".join(text.lower().replace("’", "'").split())
    flagged = any(keyword in t for keyword in EMERGENCY_KEYWORDS) or any(p.search(t) for p in PATTERNS)
    if not flagged and any(f in t for f in SEVERE_FEVER) and any(r in t for r in RASH_WORDS):
        flagged = True
    if flagged:
        return MESSAGE_UR if _is_urdu(text) else MESSAGE_EN
    return None