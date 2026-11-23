"""
tests/test_text_model.py
------------------------
Unit tests for DermaVC-Text inference module (src/text_model.py).
"""

import pytest
from src import text_model


def test_is_available():
    assert text_model.is_available() is True
    assert text_model.why_unavailable() == ""


def test_labels_count():
    assert len(text_model.LABELS) == 28
    assert "eczema" in text_model.LABELS
    assert "greeting" in text_model.LABELS


def test_predict_english():
    model = text_model.TextModel()
    res = model.predict("itchy dry red patches on inner elbows and knees")
    assert "top" in res
    assert len(res["top"]) == 3
    assert res["top_label"] == "eczema"
    assert res["is_clinical"] is True
    assert res["kb_title"] == "Eczema (atopic dermatitis)"


def test_predict_roman_urdu():
    model = text_model.TextModel()
    res = model.predict("meri kohni ke andar wali side par bohot khujli aur dry patches hain")
    assert res["top_label"] == "eczema"
    assert res["is_clinical"] is True


def test_predict_urdu_script():
    model = text_model.TextModel()
    res = model.predict("چہرے پر پیپ والے دانے اور سرخ پھنسیاں ہیں")
    assert res["top_label"] == "acne"
    assert res["is_clinical"] is True


def test_empty_input():
    model = text_model.TextModel()
    with pytest.raises(text_model.TextModelError):
        model.predict("")
