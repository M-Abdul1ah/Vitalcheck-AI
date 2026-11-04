import pytest

from src.intent import classify_intent

GREETINGS = ["hi", "Hello", "hey there", "good morning", "hello how are you", "Assalamualaikum",
             "salam", "kya haal hai", "سلام", "السلام علیکم", "آپ کیسے ہیں"]
SKIN = ["I have acne on my arm", "hi I have acne", "itchy red patches", "meri kohni par khujli hai",
        "چہرے پر دانے ہیں", "dry scaly skin on my hands"]


@pytest.mark.parametrize("text", GREETINGS)
def test_greeting(text):
    assert classify_intent(text) == "greeting"


@pytest.mark.parametrize("text", SKIN)
def test_skin_message_is_not_small_talk(text):
    assert classify_intent(text) == "other"


def test_thanks_and_bye():
    assert classify_intent("thanks") == "thanks"
    assert classify_intent("shukriya") == "thanks"
    assert classify_intent("bye") == "bye"
