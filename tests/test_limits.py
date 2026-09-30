from src.limits import check_input_length, check_rate_limit


def test_length():
    assert check_input_length("a" * 500)[0] is True
    assert check_input_length("a" * 501)[0] is False


def test_rate():
    h = []
    for _ in range(20):
        ok, _, h = check_rate_limit(h)
        assert ok
    ok, msg, h = check_rate_limit(h)
    assert ok is False
