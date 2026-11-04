from src.output_check import apply_output_check


def test_clean_answer_with_doctor_advice_passes():
    ok = "Possible causes\n- This could be related to eczema\nWhen to see a doctor: if it spreads."
    text, rep = apply_output_check(ok)
    assert rep["action"] == "passed" and text == ok


def test_missing_doctor_advice_adds_reminder():
    text, rep = apply_output_check("This could be eczema. Keep the skin moisturized.")
    assert rep["action"] == "disclaimer_added" and "doctor" in text.lower()


def test_medicine_name_is_blocked():
    text, rep = apply_output_check("Use hydrocortisone cream twice a day. See a doctor.")
    assert rep["action"] == "blocked" and "hydrocortisone" in rep["medicine"]


def test_dose_is_blocked():
    _, rep = apply_output_check("Take 500 mg after food. See a doctor.")
    assert rep["action"] == "blocked"


def test_definite_diagnosis_is_blocked():
    _, rep = apply_output_check("You definitely have psoriasis. See a doctor.")
    assert rep["action"] == "blocked" and rep["diagnosis"]


def test_urdu_answer_gets_urdu_reminder():
    text, rep = apply_output_check("ممکنہ وجہ ایگزیما ہو سکتی ہے۔")
    assert rep["action"] == "disclaimer_added" and "ڈاکٹر" in text


def test_mixed_language_answer_passes():
    _, rep = apply_output_check("ٹھیک ہے۔ You have to see a doctor if it spreads.")
    assert rep["action"] == "passed"
