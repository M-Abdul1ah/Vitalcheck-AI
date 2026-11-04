"""
Input guard: catches messages that are too vague to search (for example "I need help").
Such a message gets a friendly "tell me more" reply instead of knowledge-base matches.
"""
import re

VAGUE_PHRASES = {
    "help", "help me", "i need help", "need help", "please help", "help please",
    "hi", "hello", "hey", "salam", "assalam o alaikum", "assalamualaikum",
    "problem", "i have a problem", "i have a skin problem", "skin problem",
    "madad", "madad karo", "madad chahiye", "mujhe madad chahiye", "meri madad karo", "mujhe help chahiye",
    "help chahiye", "mujhe masla hai", "mera masla hai",
    "مدد", "مدد کریں", "مجھے مدد چاہیے", "میری مدد کریں", "مجھے مسئلہ ہے", "ہیلو", "سلام",
}

# A single word is only searched if it names a skin concern.
SKIN_WORDS = {
    "rash", "itch", "itching", "itchy", "acne", "pimple", "pimples", "eczema", "psoriasis",
    "ringworm", "scabies", "hives", "dandruff", "blister", "blisters", "mole", "wart", "warts",
    "burn", "burns", "dryness", "redness", "swelling",
    "khujli", "daad", "dane", "jild", "chaale",
    "خارش", "کھجلی", "دانے", "داد", "ایگزیما", "چھالے", "جلد", "سرخی", "الرجی",
}


def normalize(text: str) -> str:
    t = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(t.split())


def is_too_vague(text: str) -> bool:
    t = normalize(text)
    if not t or t in VAGUE_PHRASES:
        return True
    words = t.split()
    return len(words) == 1 and words[0] not in SKIN_WORDS