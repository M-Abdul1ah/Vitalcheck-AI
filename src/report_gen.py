"""
PDF health report.
Turns the chat into a downloadable summary. Uses fpdf2 with Noto fonts,
so Urdu (right-to-left) and English both render correctly.
"""
import io
import re
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from PIL import Image

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

BRAND = (11, 79, 74)
INK = (22, 48, 43)
MUTED = (91, 111, 106)
DANGER = (179, 38, 30)
SOFT = (227, 239, 236)
DANGER_SOFT = (251, 233, 231)

LABELS = {
    "en": {
        "title": "VitalCheck AI - Health Report",
        "date": "Date",
        "disclaimer": (
            "General information only. This report is not a diagnosis and does not replace a doctor. "
            "In an emergency call Rescue 1122."
        ),
        "check": "Check",
        "you": "Your symptoms",
        "guidance": "Guidance",
        "sources": "Knowledge base matches",
        "emergency": "Emergency warning",
        "note": "Note",
        "photo": "Photo sent with this message. The app does not store photos.",
        "footer": "General information only, not a diagnosis.",
        "page": "Page",
    },
    "ur": {
        "title": "VitalCheck AI - صحت کی رپورٹ",
        "date": "تاریخ",
        "disclaimer": (
            "یہ صرف عمومی معلومات ہیں۔ یہ رپورٹ تشخیص نہیں ہے اور ڈاکٹر کا متبادل نہیں۔ "
            "ایمرجنسی میں Rescue 1122 پر کال کریں۔"
        ),
        "check": "جانچ",
        "you": "آپ کی علامات",
        "guidance": "رہنمائی",
        "sources": "علمی ذخیرے سے ملتی جلتی معلومات",
        "emergency": "ہنگامی انتباہ",
        "note": "نوٹ",
        "photo": "اس پیغام کے ساتھ بھیجی گئی تصویر۔ ایپ تصاویر محفوظ نہیں کرتی۔",
        "footer": "یہ صرف عمومی معلومات ہیں، تشخیص نہیں۔",
        "page": "صفحہ",
    },
}


def _has_urdu(text: str) -> bool:
    return any("\u0600" <= ch <= "\u06FF" for ch in text)


URDU_DIGITS = str.maketrans("0123456789", "\u06F0\u06F1\u06F2\u06F3\u06F4\u06F5\u06F6\u06F7\u06F8\u06F9")


def _clean(text: str) -> str:
    """Remove markdown marks and emoji that the fonts cannot draw."""
    text = re.sub(r"[\u2600-\u27BF\uFE0F\U0001F300-\U0001FAFF]", "", text)
    text = re.sub(r"\*\*|__|`", "", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*]\s+", "\u2022 ", text, flags=re.M)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


class Report(FPDF):
    def __init__(self, lang: str):
        super().__init__(format="A4")
        self.lang = lang
        self.labels = LABELS[lang]
        self.set_margins(18, 18, 18)
        self.set_auto_page_break(auto=True, margin=20)
        for name, prefix in (("Sans", "NotoSans"), ("Naskh", "NotoNaskhArabic")):
            self.add_font(name, "", str(FONT_DIR / f"{prefix}-Regular.ttf"))
            self.add_font(name, "B", str(FONT_DIR / f"{prefix}-Bold.ttf"))
        self.set_text_shaping(True)          # joins Urdu letters and handles right-to-left order

    # -- helpers ---------------------------------------------------------
    def text_block(self, text, size=11, bold=False, color=INK, fill=None, gap=2, latin=False):
        """latin=True forces a left-to-right Latin line (used for the date)."""
        text = _clean(text)
        if not text:
            return
        urdu = _has_urdu(text) and not latin
        if urdu:
            size += 2  # Naskh letters look smaller than Latin at the same size
            text = "\n".join("\u200f" + line if line.strip() else line for line in text.split("\n"))
        self.set_font("Naskh" if urdu else "Sans", "B" if bold else "", size)
        self.set_text_color(*color)
        if fill:
            self.set_fill_color(*fill)
        align = "R" if urdu or (latin and self.lang == "ur") else "L"
        self.multi_cell(
            0, size * (0.7 if urdu else 0.55), text,
            align=align, fill=bool(fill), padding=3 if fill else 0,
            new_x="LMARGIN", new_y="NEXT",
        )
        self.ln(gap)

    def add_photo(self, jpeg_bytes, caption, width=60):
        """Put the photo the user sent into the report (kept small, placed on the reading side)."""
        img = Image.open(io.BytesIO(jpeg_bytes))
        img.thumbnail((700, 700))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=80)
        height = width * img.height / img.width
        if self.get_y() + height + 10 > self.page_break_trigger:
            self.add_page()
        x = self.w - self.r_margin - width if self.lang == "ur" else self.l_margin
        self.image(buf, x=x, y=self.get_y(), w=width, h=height)
        self.set_y(self.get_y() + height + 2)
        self.text_block(caption, size=8, color=MUTED, gap=3)

    def footer(self):
        self.set_y(-14)
        urdu = self.lang == "ur"
        self.set_font("Naskh" if urdu else "Sans", "", 8)
        self.set_text_color(*MUTED)
        page = str(self.page_no())
        if urdu:
            page = page.translate(URDU_DIGITS)
        self.cell(0, 6, f"{self.labels['footer']}   |   {self.labels['page']} {page}", align="C")


def build_report(messages: list, lang: str = "en") -> bytes:
    """messages: the chat list from the app (dicts with role, content, kind, sources)."""
    lang = lang if lang in LABELS else "en"
    L = LABELS[lang]
    pdf = Report(lang)
    pdf.add_page()

    pdf.text_block(L["title"], size=20, bold=True, color=BRAND, gap=1)
    pdf.text_block(datetime.now().strftime("%d %b %Y, %H:%M"), size=10, color=MUTED, gap=3, latin=True)
    pdf.text_block(L["disclaimer"], size=10, color=INK, fill=SOFT, gap=5)

    n = 0
    for m in messages:
        if m["role"] == "user":
            n += 1
            pdf.set_draw_color(*BRAND)
            pdf.set_line_width(0.4)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(3)
            num = str(n).translate(URDU_DIGITS) if lang == "ur" else str(n)
            pdf.text_block(f"{L['check']} {num}", size=9, color=MUTED, gap=1)
            pdf.text_block(L["you"], size=12, bold=True, color=BRAND, gap=1)
            pdf.text_block(m["content"], size=11, gap=3)
            if m.get("photo"):
                try:
                    pdf.add_photo(m["photo"], L["photo"])
                except Exception:
                    pass   # a broken photo must never stop the report
            continue

        kind = m.get("kind")
        if kind == "alert":
            pdf.text_block(L["emergency"], size=12, bold=True, color=DANGER, gap=1)
            pdf.text_block(m["content"], size=11, color=DANGER, fill=DANGER_SOFT, gap=3)
            continue

        heading = L["guidance"] if kind == "answer" else L["note"]
        pdf.text_block(heading, size=12, bold=True, color=BRAND, gap=1)
        pdf.text_block(m["content"], size=11, gap=3)
        titles = [s["title"] for s in m.get("sources") or []]
        if titles:
            pdf.text_block(f"{L['sources']}: " + ", ".join(titles), size=9, color=MUTED, gap=4)

    return bytes(pdf.output())
