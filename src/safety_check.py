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
RASH_WORDS = ["rash", "spots", "blisters", "hives", "دانے", "خارش", "چھالے", "dane", "daney", "daane", "chhale", "chale", "khujli"]
SEVERE_FEVER = [
    "high fever", "very high fever", "severe fever", "fever and chills", "fever with chills",
    "تیز بخار", "شدید بخار", "بہت بخار",
    "tez bukhar", "bohat bukhar", "bahut bukhar", "shadeed bukhar", "shadid bukhar", "bukhar bohat tez", "bukhar bahut tez",
]

import re

# Pattern rules catch wording variants a phrase list misses. Each rule is (category, regex).
# They only flag a serious body part or sign next to a serious word, so "pimples on my chest" is not flagged.
_I = re.I
RULES = [
    ("chest", re.compile(r"\b(chest|heart)\s+(is\s+|feels\s+|has\s+been\s+|was\s+)?"
                         r"(hurt|hurts|hurting|ache|aches|aching|pain|pains|paining|tight|tightness|burning|heavy)\b")),
    ("chest", re.compile(r"\b(pain|pains|pressure|tightness|heaviness|squeezing|crushing)\b.{0,25}\b(chest|heart)\b")),
    ("chest", re.compile(r"\bchest\b.{0,12}\b(pressure|squeez\w*|crushing)\b")),
    ("chest", re.compile(r"\bdil\s+(band|ruk|dhadak)|seene?\s+(mein\s+|me\s+|mai\s+|par\s+|pe\s+)?(\w+\s+){0,2}(dard|dabao|bhaari|bhari|dukh)\b")),
    ("chest", re.compile(r"سینے\s+(میں|پر)\s+(\S+\s+){0,2}(درد|دباؤ|بھاری|جکڑ)")),
    ("breathing", re.compile(r"\b(hard|difficult|trouble|struggl\w*|can'?t|cannot|unable|not able)\s+(to\s+)?breath\w*"
                             r"|\bbreath\w*\s+(is\s+|has\s+become\s+)?(hard|difficult|laboured|labored)"
                             r"|\b(gasping|choking|wheezing)\b|\bshort of breath\b")),
    ("breathing", re.compile(r"سانس\s+(لینے\s+میں\s+)?(\S+\s+)?(تکلیف|مشکل|دشواری|پھول|رک|نہیں)|سانس\s+پھول")),
    ("breathing", re.compile(r"\bsaans\s+(lene\s+(mein|me)\s+)?(\w+\s+)?(takleef|mushkil|dikkat|phool|ruk|nahi)\b|\bsans\s+phool")),
    ("allergy", re.compile(r"\b(throat|windpipe)\s+(feels?\s+|is\s+|was\s+)?(like\s+)?(it\s+(is|was)\s+)?(\w+\s+)?(closing|closed|tight|swelling|swollen)"
                           r"|\b(swollen|swelling|tight)\s+throat")),
    ("allergy", re.compile(r"\b(lips?|tongue|face|eyelids?)\s+(are\s+|is\s+|were\s+|was\s+|feel\s+|feels\s+|look\s+|looks\s+)?"
                           r"(swelling|swollen|swelled|ballooning)")),
    ("allergy", re.compile(r"(چہرہ|چہرے|ہونٹ|زبان|گلا|گلے)\s+(میں\s+|پر\s+|کا\s+|کی\s+|اور\s+\S+\s+)?(سوج|پھول|سوجن)|نگلنا\s+مشکل")),
    ("allergy", re.compile(r"\b(chehra|chehre|hont|honth|zuban|zubaan|gala|gale)\s+(par\s+|pe\s+|mein\s+|me\s+|ka\s+|ki\s+)?(sooj|soojan|phool|phul|sujan|suj)"
                           r"|nigalna\s+mushkil")),
    ("unconscious", re.compile(r"\b(faint(ed|ing)?|blacked out|black out|collaps(ed|ing)|unresponsive|not responding|won'?t wake|not waking|not wake)\b")),
    ("bleeding", re.compile(r"\b(won'?t|will not|doesn'?t|does not|not|isn'?t|is not|can'?t|cannot)\s+(\w+\s+)?(stop|stopping)\s+(\w+\s+)?bleed"
                            r"|\bbleed\w*\s+(\w+\s+){0,3}(won'?t|will not|doesn'?t|does not|isn'?t|is not)\s+(\w+\s+)?stop"
                            r"|\bblood\s+(is\s+)?(pouring|gushing|spurting)")),
    ("bleeding", re.compile(r"خون\s+(\S+\s+){0,3}(رک|بند)")),
    ("bleeding", re.compile(r"\bkhoon\s+(\w+\s+){0,3}(ruk|band)\b")),
    ("seizure", re.compile(r"\b(shaking uncontrollably|convuls\w*|fitting)\b")),
    ("meningitis", re.compile(r"\b(purple|dark red|maroon)\s+(spots|rash|marks|patches|dots)\b.*\b(fever|fade|press\w*)\b"
                              r"|\b(fever|feverish)\b.*\b(purple|dark red|maroon)\s+(spots|rash|marks|patches|dots)\b")),
    ("meningitis", re.compile(r"(جامنی|بنفشی)\s+(دھبے|دانے|نشان).*(بخار|دبانے\s+سے\s+نہیں)")),
    ("meningitis", re.compile(r"\b(jamni|jaamni|bainjni)\s+(daane|dane|dhabbe|nishan)\b.*\b(bukhar|dabane\s+se\s+nahi)\b")),
    ("severe_drug_reaction", re.compile(r"\bskin\b.{0,25}\bpeeling\b.{0,15}\b(off|sheets)\b|\bpeeling\b.{0,10}\bin\b.{0,10}\bsheets\b")),
    ("severe_drug_reaction", re.compile(r"جلد\s+(\S+\s+){0,2}اتر\s*رہی")),
    ("severe_drug_reaction", re.compile(r"\bjild\s+(\w+\s+){0,2}utar\s+rahi")),
    ("infection", re.compile(r"\b(red|reddish)\s+(lines?|streaks?)\b.{0,30}\b(spread\w*|up|going|moving)\b|\b(spread\w*|going|moving)\b.{0,30}\b(red|reddish)\s+(lines?|streaks?)\b")),
    ("infection", re.compile(r"سرخ\s+لکیر")),
    ("infection", re.compile(r"\blaal\s+lakeer")),
    ("self_harm", re.compile(r"\b(hurt|harm|cut|injure)\s+myself|\bdon'?t\s+want\s+to\s+(live|be\s+alive|exist)|\bno\s+reason\s+to\s+live"
                             r"|\bbetter\s+off\s+dead|\bend\s+it\s+all|\btake\s+my\s+own\s+life|\bsuicidal\b")),
    ("self_harm", re.compile(r"جینا\s+نہیں\s+چاہ|زندہ\s+نہیں\s+رہنا|اپنی\s+جان\s+لے|خود\s+کو\s+(نقصان|مار|زخمی)")),
    ("self_harm", re.compile(r"\b(jeena|jina|zinda\s+rehna|zinda\s+rehne)\s+(\w+\s+)?nahi|apni\s+jaan\s+le|khud\s+ko\s+(nuksan|maar|zakhmi)|\bmar\s+jana\s+chah")),
    ("overdose", re.compile(r"\b(took|taken|swallowed|ate|eaten|drank|drunk)\s+(too\s+many|a\s+lot\s+of|lots\s+of|many|an?\s+entire|the\s+whole)\s+(\w+\s+)?(pills?|tablets?|medicine|medication|capsules?)"
                            r"|\b(drank|swallowed|ate)\s+(poison|bleach|pesticide|acid)\b|\bpoisoned\b")),
    ("overdose", re.compile(r"(بہت|بہت\s+ساری|ڈھیر\s+ساری|زیادہ)\s+(\S+\s+)?(گولیاں|گولی|دوا)\s+(\S+\s+)?کھا|زہر\s+(کھا|پی)")),
    ("overdose", re.compile(r"\b(bohat|bahut|bohot|zyada|dher)\s+(saari\s+|sari\s+)?(goliyan|goli|dawai|dawa)\s+(\w+\s+)?kha|\bzeher\s+(kha|pi)|\bzehar\s+(kha|pi)")),
    ("burn", re.compile(r"\b(burn|burnt|burned|scald\w*)\b.{0,40}\b(most\s+of|whole|entire|covering|large\s+area|big\s+area|electric\w*|chemical|acid)\b"
                        r"|\b(boiling|hot)\s+(water|oil|tea|milk)\b.{0,40}\b(burn|burnt|burned|scald\w*)")),
    ("burn", re.compile(r"(ساری|سارا|پوری|پورا)\s+\S+(\s+\S+){0,3}\s+جل\s+گئ")),
    ("burn", re.compile(r"\b(poori|poora|sari|saari|sara|pura)\s+\w+(\s+\w+){0,2}\s+jal\s+(gayi|gaya|gai|gaye)\b")),
    ("eye", re.compile(r"\b(sudden|suddenly)\s+(loss\s+of\s+)?(vision|sight)|\blost\s+(my\s+)?(vision|sight)|\bvision\s+loss|\bblind\s+in\s+(one|my)\s+eye"
                       r"|\bcan'?t\s+see\s+(out\s+of|with)")),
    ("eye", re.compile(r"اچانک\s+(نظر|بینائی)|\bachanak\s+(nazar|nazr)")),
]


def _normalise(text: str) -> str:
    """Lower-case, unify apostrophes and Arabic/Urdu letter variants, collapse spaces."""
    t = text.lower().replace("’", "'").replace("ي", "ی").replace("ك", "ک").replace("ە", "ہ")
    return " ".join(t.split())


def emergency_category(text: str) -> str | None:
    """Name the kind of red flag found (chest, breathing, allergy, ...), or None."""
    t = _normalise(text)
    # remove harmless wording first: "no pain", "without any pressure", "pressure marks"
    t = re.sub(r"\b(no|without|not any|without any)\s+(any\s+)?(chest\s+)?(pain|pains|pressure|tightness)\b", " ", t)
    t = re.sub(r"\bpressure\s+marks?\b", " ", t)
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in t:
            return "phrase"
    for category, pattern in RULES:
        if pattern.search(t):
            return category
    if any(f in t for f in SEVERE_FEVER) and any(r in t for r in RASH_WORDS):
        return "fever_rash"
    return None


def check_emergency(text: str) -> str | None:
    """Return an urgent warning message if a red-flag phrase is found, else None."""
    if emergency_category(text):
        return MESSAGE_UR if _is_urdu(text) else MESSAGE_EN
    return None
