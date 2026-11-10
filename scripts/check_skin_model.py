"""
Check that DermaVC-Net loads and behaves like the training results.

  python scripts/check_skin_model.py                       -> loads the model and prints its status
  python scripts/check_skin_model.py --image photo.jpg     -> top-3 for one photo
  python scripts/check_skin_model.py --images-dir D:\\HAM10000\\images --n 300
        -> accuracy on the first N rows of training/splits/test.csv (expected about 0.83 for seed 7)
           and tries both resize modes, so you can see which one matches training.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import skin_model as sm  # noqa: E402
from src.vision_agent import prepare_image  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image")
    ap.add_argument("--images-dir")
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()

    print("Model file:", sm.MODEL_PATH, "| exists:", sm.MODEL_PATH.exists())
    t0 = time.time()
    try:
        model = sm.SkinModel()
    except sm.SkinModelError as e:
        sys.exit(f"LOAD FAILED: {e}")
    print(f"Loaded in {time.time() - t0:.1f}s. Classes: {model.classes}. Policy: {model.policy}")

    if args.image:
        data = prepare_image(Path(args.image).read_bytes())
        t0 = time.time()
        r = model.predict(data, heatmap=True)
        print(f"Predicted in {(time.time() - t0) * 1000:.0f} ms")
        if r.get("heatmap_png"):
            Path("heatmap_test.png").write_bytes(r["heatmap_png"])
            print("Heatmap saved to heatmap_test.png (open it to look)")
        else:
            print("HEATMAP FAILED:", r.get("heatmap_error") or "unknown")
        for t in r["top"]:
            print(f"  {t['code']:6s} {t['probability']:.3f}  {t['label_en']}")
        print("confident:", r["confident"], "| melanoma flag:", r["melanoma_flag"], f"({r['mel_probability']:.3f})")

    if args.images_dir:
        rows = list(csv.DictReader(open(sm.ROOT / "training" / "splits" / "test.csv", encoding="utf-8")))
        step = max(1, len(rows) // args.n)
        rows = rows[::step][: args.n]
        for mode in ("squash", "crop"):
            sm.RESIZE_MODE = mode
            ok = mel_ok = mel_n = 0
            used = 0
            for row in rows:
                f = Path(args.images_dir) / f"{row['image_id']}.jpg"
                if not f.exists():
                    continue
                used += 1
                logits = model.logits(f.read_bytes())
                pred = sm.interpret(logits, model.classes, model.policy)["top"][0]["code"]
                ok += pred == row["dx"]
                if row["dx"] == "mel":
                    mel_n += 1
                    mel_ok += pred == "mel"
            if used == 0:
                sys.exit("No images found. Check --images-dir (files should be named like ISIC_0027419.jpg).")
            print(f"mode={mode:6s} images={used}  accuracy={ok / used:.3f}  melanoma recall={mel_ok / max(1, mel_n):.3f} (n={mel_n})")
        print("The mode with accuracy near 0.83 is right. If both are far below, the preprocessing or the .pt file differs from training.")


if __name__ == "__main__":
    main()
