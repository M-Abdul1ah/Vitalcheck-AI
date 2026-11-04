"""
Tiny rule-based intent check. Runs right after the emergency gate.
Detects greetings / thanks / goodbyes (English, Urdu, Roman Urdu) so the app
replies politely instead of searching the knowledge base.
"""
import re

GREETING_WORDS = {
    # English
    "hi", "hii", "hiii", "hello", "hey", "heyy", "yo", "salam", "good", "morning", "afternoon", "evening",
    "there", "howdy", "greetings", "sup", "whats", "up", "how", "are", "you", "doing",
    # Roman Urdu
    "assalamualaikum", "assalam", "alaikum", "aoa", "slam", "salaam", "walaikum", "walaikumassalam",
    "kia", "kya", "haal", "hal", "hai", "ho", "aap", "kaise", "kese", "kaisay", "janab",
    # Urdu script
    "سلام", "ہیلو", "ہائے", "السلام", "علیکم", "وعلیکم", "آداب", "کیا", "حال", "ہے", "آپ", "کیسے", "ہیں",
}
THANKS_WORDS = {"thanks", "thank", "you", "thx", "shukria", "shukriya", "jazakallah", "ok", "okay", "great",
                "شکریہ", "جزاک", "اللہ", "ٹھیک"}
BYE_WORDS = {"bye", "goodbye", "allah", "hafiz", "khuda", "see", "later", "الوداع", "خدا", "حافظ"}


def _tokens(text: str) -> list[str]:
    cleaned = re.sub(r"[^\w\u0600-\u06FF\s]", " ", text.lower().replace("’", "'"))
    return cleaned.split()


def classify_intent(text: str) -> str:
    """Return 'greeting', 'thanks', 'bye' or 'other'. Only short messages can be small talk."""
    toks = _tokens(text)
    if not toks or len(toks) > 6:
        return "other"
    if all(tok in THANKS_WORDS for tok in toks):
        return "thanks"
    if all(tok in BYE_WORDS for tok in toks):
        return "bye"
    if all(tok in GREETING_WORDS for tok in toks):
        return "greeting"
    return "other"
