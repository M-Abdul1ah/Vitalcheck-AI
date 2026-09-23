from src.report_gen import build_report

SAMPLE = [
    {"role": "user", "content": "Itchy red scaly patches on my elbows"},
    {"role": "assistant", "kind": "answer",
     "content": "- Possible causes: eczema or psoriasis\n- Self-care tip: keep skin moisturized\n- When to see a doctor: if it spreads",
     "sources": [{"title": "Eczema (atopic dermatitis)", "text": "..."}]},
    {"role": "user", "content": "میرے سینے میں درد ہے"},
    {"role": "assistant", "kind": "alert", "content": "⚠️ یہ طبی ایمرجنسی ہو سکتی ہے۔ Rescue 1122 پر کال کریں۔"},
]


def _photo():
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (800, 600), (200, 90, 80)).save(buf, "JPEG")
    return buf.getvalue()


def run():
    for lang in ("en", "ur"):
        pdf = build_report(SAMPLE, lang)
        assert pdf.startswith(b"%PDF") and len(pdf) > 2000

    # a photo makes the report bigger, and broken photo bytes never crash it
    with_photo = [dict(SAMPLE[0], photo=_photo())] + SAMPLE[1:]
    assert len(build_report(with_photo, "en")) > len(build_report(SAMPLE, "en"))
    broken = [dict(SAMPLE[0], photo=b"not a photo")] + SAMPLE[1:]
    assert build_report(broken, "en").startswith(b"%PDF")
    print("report tests passed")


if __name__ == "__main__":
    run()
