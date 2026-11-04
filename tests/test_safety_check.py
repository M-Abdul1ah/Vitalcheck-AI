import pytest

from src.safety_check import check_emergency

RED_FLAGS = [
    # English
    "I have chest pain and a rash", "heart pain since morning", "I can't breathe", "difficulty breathing after the rash",
    "my lips turning blue", "stiff neck with rash", "my skin turning black", "bleeding a lot from the wound",
    "I passed out", "swollen tongue and hives", "I want to die",
    # Urdu script
    "میرے سینے میں درد ہے", "دل میں درد ہو رہا ہے", "سانس لینے میں مشکل ہے", "بہت خون بہہ رہا ہے",
    "وہ ہوش میں نہیں ہے", "خودکشی کا خیال آ رہا ہے",
    # Roman Urdu
    "seene mein dard hai", "dil mein dard hai", "saans nahi aa rahi", "saans lene mein masla hai",
    "bohat khoon beh raha hai", "hosh mein nahi hai", "wo behosh ho gaya", "marne laga hon",
]

NORMAL = [
    "itchy red patches on my elbows", "painful pimples and blackheads on my face",
    "a round ring-shaped rash that keeps spreading", "dry scaly skin on my hands",
    "میری کہنیوں پر خارش اور سرخ خشک دھبے ہیں", "چہرے پر دانے ہیں",
    "meri kohni par khujli hai", "chehre par dane hain",
]


@pytest.mark.parametrize("text", RED_FLAGS)
def test_red_flag_detected(text):
    assert check_emergency(text) is not None


@pytest.mark.parametrize("text", NORMAL)
def test_normal_message_passes(text):
    assert check_emergency(text) is None


def test_warning_mentions_rescue_1122_in_both_languages():
    en = check_emergency("I can't breathe")
    ur = check_emergency("میرے سینے میں درد ہے")
    assert "1122" in en and "1122" in ur and en != ur
