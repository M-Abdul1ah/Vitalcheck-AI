import pytest

from src.input_guard import is_too_vague

VAGUE = [
    "I need help", "help!", "Hi", "hello?", "please help", "skin problem",
    "mujhe madad chahiye", "مجھے مدد چاہیے", "سلام", "asdfgh", "   ",
]
SPECIFIC = [
    "red itchy patches on my arm", "rash", "pimples", "I need help with itchy skin on my arm",
    "meri kohni par khujli hai", "میری کہنیوں پر خارش ہے", "خارش", "ایگزیما",
]


@pytest.mark.parametrize("text", VAGUE)
def test_vague_message_is_caught(text):
    assert is_too_vague(text)


@pytest.mark.parametrize("text", SPECIFIC)
def test_specific_message_is_searched(text):
    assert not is_too_vague(text)