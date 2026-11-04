"""Mean +/- std over the 3 seeds of each model, from training/results/<model>_seed<N>.json.
Run from the repo root:  python scripts/benchmark_stats.py
Writes training/results/benchmark_mean_std.csv and prints markdown tables."""
import csv
import json
import statistics as st
from pathlib import Path

RES = Path("training/results")
KEYS = ["accuracy", "macro_f1", "melanoma_recall", "auc", "params_m", "size_mb",
        "latency_ms", "train_time_min", "best_epoch"]
CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

runs = {}
for f in sorted(RES.glob("*_seed*.json")):
    if f.stem.endswith("_history"):
        continue
    d = json.loads(f.read_text(encoding="utf-8"))
    runs.setdefault(d["model"], []).append(d)


def ms(values, digits=3):
    m = st.mean(values)
    s = st.stdev(values) if len(values) > 1 else 0.0
    return f"{m:.{digits}f} ± {s:.{digits}f}"


rows = []
for model, rs in runs.items():
    row = {"model": model, "runs": len(rs), "seeds": " ".join(str(r["seed"]) for r in rs)}
    for k in KEYS:
        row[k] = ms([r[k] for r in rs], 2 if k in ("params_m", "size_mb", "latency_ms", "train_time_min", "best_epoch") else 3)
    for c in CLASSES:
        row["recall_" + c] = ms([r["per_class_recall"][c] for r in rs])
    rows.append(row)

out = RES / "benchmark_mean_std.csv"
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("| Model | Seeds | Accuracy | Macro F1 | Melanoma recall | AUC |")
print("|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['model']} | {r['seeds']} | {r['accuracy']} | {r['macro_f1']} | {r['melanoma_recall']} | {r['auc']} |")
print()
print("| Model | Params (M) | Size (MB) | Latency (ms) | Train (min) | Best epoch |")
print("|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['model']} | {r['params_m']} | {r['size_mb']} | {r['latency_ms']} | {r['train_time_min']} | {r['best_epoch']} |")
print()
print("| Model | " + " | ".join(CLASSES) + " |")
print("|---|" + "---|" * len(CLASSES))
for r in rows:
    print(f"| {r['model']} | " + " | ".join(r["recall_" + c] for c in CLASSES) + " |")
print("\nSaved:", out)