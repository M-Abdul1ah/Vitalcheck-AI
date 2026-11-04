"""Underfit / overfit check from the training histories.
Run from the repo root:  python scripts/check_fit.py
Reads training/results/*_history.json, prints one row per run, writes training/results/fit_check.csv."""
import csv
import json
from pathlib import Path

RES = Path("training/results")
NAMES = {
    "train_loss": ("train_loss", "loss", "training_loss"),
    "val_loss": ("val_loss", "valid_loss", "validation_loss"),
    "train_acc": ("train_acc", "train_accuracy", "acc", "accuracy", "training_accuracy"),
    "val_acc": ("val_acc", "val_accuracy", "valid_acc", "validation_accuracy"),
}


def collect(obj, out):
    """Gather every list of numbers by key name; nested stages are joined in order."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v):
                out.setdefault(k.lower(), []).extend(v)
            else:
                collect(v, out)
    elif isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        for row in obj:
            for k, v in row.items():
                if isinstance(v, (int, float)):
                    out.setdefault(k.lower(), []).append(v)


def pick(series, wanted):
    for name in NAMES[wanted]:
        if name in series:
            return series[name]
    return None


def verdict(tr_acc, va_acc, tr_loss, va_loss):
    gap = tr_acc[-1] - va_acc[-1] if tr_acc and va_acc else None
    rise = None
    if va_loss:
        rise = va_loss[-1] / min(va_loss) - 1
    reasons = []
    if gap is not None and gap > 0.10:
        reasons.append(f"train acc is {gap:.2f} above val acc")
    if rise is not None and rise > 0.10 and tr_loss and tr_loss[-1] < tr_loss[0]:
        reasons.append(f"val loss ended {rise*100:.0f}% above its best while train loss kept falling")
    if reasons:
        return "OVERFIT", "; ".join(reasons), gap, rise
    if tr_acc and va_acc and max(tr_acc[-1], va_acc[-1]) < 0.70 and abs(gap) < 0.05:
        return "UNDERFIT?", "both train and val accuracy are low and close together", gap, rise
    return "GOOD FIT", "small train/val gap and val loss did not rise", gap, rise


rows = []
for f in sorted(RES.glob("*_history.json")):
    name = f.stem.replace("_history", "")
    series = {}
    collect(json.loads(f.read_text(encoding="utf-8")), series)
    tr_l, va_l = pick(series, "train_loss"), pick(series, "val_loss")
    tr_a, va_a = pick(series, "train_acc"), pick(series, "val_acc")
    if not (va_l or va_a):
        print(f"{name}: could not find val curves. Keys found: {sorted(series)}")
        continue
    v, why, gap, rise = verdict(tr_a, va_a, tr_l, va_l)
    best = (max(range(len(va_a)), key=va_a.__getitem__) + 1) if va_a else (min(range(len(va_l)), key=va_l.__getitem__) + 1)
    rows.append({
        "run": name, "epochs": len(va_a or va_l), "best_epoch": best,
        "train_acc_end": round(tr_a[-1], 3) if tr_a else "", "val_acc_end": round(va_a[-1], 3) if va_a else "",
        "acc_gap": round(gap, 3) if gap is not None else "",
        "train_loss_end": round(tr_l[-1], 3) if tr_l else "", "val_loss_end": round(va_l[-1], 3) if va_l else "",
        "val_loss_min": round(min(va_l), 3) if va_l else "",
        "verdict": v, "why": why,
    })

if rows:
    out = RES / "fit_check.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{'run':32} {'ep':>3} {'best':>4} {'tr_acc':>7} {'va_acc':>7} {'gap':>6} {'va_loss_end/min':>16}  verdict")
    for r in rows:
        print(f"{r['run']:32} {r['epochs']:>3} {r['best_epoch']:>4} {r['train_acc_end']:>7} {r['val_acc_end']:>7} "
              f"{r['acc_gap']:>6} {str(r['val_loss_end'])+'/'+str(r['val_loss_min']):>16}  {r['verdict']}")
    print("\nWhy:")
    for r in rows:
        print(f"- {r['run']}: {r['verdict']} ({r['why']})")
    print("\nSaved:", out)