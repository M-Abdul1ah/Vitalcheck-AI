"""Safety suite: reads the CSV files in tests/data/ so the tests and the evaluation script use the same data."""
import csv
from pathlib import Path

import pytest

from src.output_check import apply_output_check
from src.safety_check import check_emergency, emergency_category

DATA = Path(__file__).parent / "data"


def rows(name):
    with open(DATA / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


RED, OK = rows("red_flags.csv"), rows("not_emergency.csv")
UNSAFE, SAFE = rows("unsafe_answers.csv"), rows("safe_answers.csv")


@pytest.mark.parametrize("r", RED, ids=[r["id"] for r in RED])
def test_gate_catches_every_red_flag(r):
    assert check_emergency(r["text"]), f"missed ({r['category']}): {r['text']}"


@pytest.mark.parametrize("r", OK, ids=[r["id"] for r in OK])
def test_gate_does_not_flag_normal_skin_messages(r):
    assert not check_emergency(r["text"]), f"false alarm ({emergency_category(r['text'])}): {r['text']}"


@pytest.mark.parametrize("r", UNSAFE, ids=[r["id"] for r in UNSAFE])
def test_output_check_blocks_unsafe_answers(r):
    assert apply_output_check(r["text"])[1]["action"] == "blocked", r["text"]


@pytest.mark.parametrize("r", SAFE, ids=[r["id"] for r in SAFE])
def test_output_check_passes_safe_answers(r):
    assert apply_output_check(r["text"])[1]["action"] != "blocked", r["text"]


def test_category_names_are_reported():
    assert emergency_category("my chest hurts") in {"phrase", "chest"}
    assert emergency_category("itchy rash on my arm") is None
