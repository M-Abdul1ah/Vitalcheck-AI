from src.safety_check import check_emergency


def run():
    assert check_emergency("I have chest pain and a rash") is not None
    assert check_emergency("میرے سینے میں درد ہے") is not None
    assert check_emergency("seene mein dard hai") is not None
    assert "1122" in check_emergency("I can't breathe")
    assert check_emergency("itchy red patches on my elbows") is None
    print("all safety tests passed")


if __name__ == "__main__":
    run()
