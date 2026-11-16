"""
Safety evaluation: numbers for the report.

  python scripts/run_safety_eval.py

Reads the CSV files in tests/data/ and measures
  - emergency gate recall on red-flag messages (must be 100%)
  - emergency gate false alarms on normal skin messages (should be 0)
  - output check: unsafe answers blocked, safe answers passed
and writes docs/safety_eval.csv. The gate and output check are plain rules, so no model or key is needed.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.output_check import apply_output_check  # noqa: E402
from src.safety_check import check_emergency  # noqa: E402

DATA = ROOT / "tests" / "data"


def rows(name):
    with open(DATA / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    red, ok = rows("red_flags.csv"), rows("not_emergency.csv")
    unsafe, safe = rows("unsafe_answers.csv"), rows("safe_answers.csv")

    missed = [r for r in red if not check_emergency(r["text"])]
    false_alarm = [r for r in ok if check_emergency(r["text"])]
    not_blocked = [r for r in unsafe if apply_output_check(r["text"])[1]["action"] != "blocked"]
    wrongly_blocked = [r for r in safe if apply_output_check(r["text"])[1]["action"] == "blocked"]

    result = [
        ("gate_red_flags_caught", len(red) - len(missed), len(red)),
        ("gate_false_alarms", len(false_alarm), len(ok)),
        ("output_unsafe_blocked", len(unsafe) - len(not_blocked), len(unsafe)),
        ("output_safe_wrongly_blocked", len(wrongly_blocked), len(safe)),
    ]
    print(f"{'check':32s} {'count':>6s} {'total':>6s} {'rate':>7s}")
    for name, n, total in result:
        print(f"{name:32s} {n:6d} {total:6d} {n / total:7.1%}")
    for title, items in (("MISSED red flags", missed), ("FALSE alarms", false_alarm),
                         ("Unsafe answers NOT blocked", not_blocked), ("Safe answers wrongly blocked", wrongly_blocked)):
        if items:
            print(f"\n{title}:")
            for r in items:
                print(f"  {r['id']} [{r['language']}] {r['text']}")

    out = ROOT / "docs" / "safety_eval.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["check", "count", "total", "rate"])
        for name, n, total in result:
            w.writerow([name, n, total, f"{n / total:.3f}"])
    print(f"\nSaved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
