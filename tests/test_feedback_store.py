import csv

import pytest

from src.feedback_store import MAX_CHARS, save, validate


def test_valid():
    assert validate(5, "bug", "The photo button is hard to find") == (True, "")


@pytest.mark.parametrize("args,code", [
    ((0, "bug", "hello world"), "rating"),
    ((3, "spam", "hello world"), "category"),
    ((3, "bug", "hi"), "too_short"),
    ((3, "bug", "x" * (MAX_CHARS + 1)), "too_long"),
])
def test_invalid(args, code):
    assert validate(*args) == (False, code)


def test_save_writes_header_and_row(tmp_path):
    f = tmp_path / "fb.csv"
    save(4, "idea", "Add a dark mode please", path=f)
    save(2, "bug", "Urdu text looks cut off", path=f)
    rows = list(csv.reader(f.open(encoding="utf-8")))
    assert rows[0] == ["time_utc", "rating", "category", "message"]
    assert len(rows) == 3 and rows[1][1] == "4"


def test_formula_cells_are_neutralised(tmp_path):
    f = tmp_path / "fb.csv"
    save(1, "other", "=HYPERLINK(\"http://x\")", path=f)
    assert list(csv.reader(f.open(encoding="utf-8")))[1][3].startswith("'=")


def test_invalid_save_raises(tmp_path):
    with pytest.raises(ValueError):
        save(9, "bug", "hello world", path=tmp_path / "x.csv")
