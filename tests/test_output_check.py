from src.output_check import apply_output_check


def run():
    ok = "Possible causes\n- This could be related to eczema\nWhen to see a doctor: if it spreads."
    text, rep = apply_output_check(ok)
    assert rep["action"] == "passed" and text == ok

    text, rep = apply_output_check("This could be eczema. Keep the skin moisturized.")
    assert rep["action"] == "disclaimer_added" and "doctor" in text.lower()

    text, rep = apply_output_check("Use hydrocortisone cream twice a day. See a doctor.")
    assert rep["action"] == "blocked" and "hydrocortisone" in rep["medicine"]

    text, rep = apply_output_check("Take 500 mg after food. See a doctor.")
    assert rep["action"] == "blocked"

    text, rep = apply_output_check("You definitely have psoriasis. See a doctor.")
    assert rep["action"] == "blocked" and rep["diagnosis"]

    text, rep = apply_output_check("ممکنہ وجہ ایگزیما ہو سکتی ہے۔")
    assert rep["action"] == "disclaimer_added" and "ڈاکٹر" in text

    text, rep = apply_output_check("ٹھیک ہے۔ You have to see a doctor if it spreads.")
    assert rep["action"] == "passed"
    print("output check tests passed")


if __name__ == "__main__":
    run()
