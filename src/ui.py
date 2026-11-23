"""Shared front-end pieces: language, stylesheet, header, footer and small HTML helpers. Used by app.py and views/."""
import html
from pathlib import Path

import streamlit as st

from src.site_content import EMAIL, EMERGENCY_NUMBER, GITHUB_URL, SUPERVISOR

ROOT = Path(__file__).resolve().parent.parent

RTL_CSS = """
<style>
.hero-title, .hero-sub, .notice, .alert, .step, .side-note, .page-hero, .section-title, .card, .sup, .quote,
.site-footer, .topmatch, .others, .hint, .chips, .links,
[data-testid="stChatMessage"] .stMarkdown, [data-testid="stExpander"], div.stButton > button,
div.stDownloadButton > button, div.stFormSubmitButton > button, [data-testid="stForm"] { direction: rtl; text-align: right; }
.hero-title, .hero-sub, .notice, .alert, .step, .side-note, .pill, .page-title, .page-sub, .section-title, .card p,
.card h4, .sup h4, .sup p, .quote, .site-footer, .role, .others, .badge, [data-testid="stExpander"] p, .eyebrow,
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li, div.stButton > button, div.stDownloadButton > button,
div.stFormSubmitButton > button, label, textarea { font-family: 'Noto Nastaliq Urdu', serif !important; line-height: 2.2; }
.hero-title, .page-title { line-height: 1.9; max-width: none; letter-spacing: 0; text-transform: none; }
.eyebrow { text-transform: none; letter-spacing: 0; }
.brand, .others .row .p { direction: ltr; }
.others .row .p { text-align: left; }
</style>
"""


def esc(x):
    return html.escape(str(x))


def current_lang():
    return "ur" if st.session_state.get("lang_label") == "اردو" else "en"


def load_css(lang):
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    if lang == "ur":
        st.markdown(RTL_CSS, unsafe_allow_html=True)


def header():
    """Render a clear brand row with the language control kept out of the footer."""
    left, right = st.columns([2.5, 1.5], gap="large")
    with left:
        st.markdown(
            '<div class="vc-header-brand">'
            '<span class="vc-brand-mark">+</span>'
            '<span class="vc-brand-copy"><strong>VitalCheck AI</strong>'
            '<small>Urdu / English skin guidance</small></span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="vc-language-label">LANGUAGE <span>زبان</span></div>', unsafe_allow_html=True)
        st.radio(
            "Language",
            ["English", "اردو"],
            horizontal=True,
            key="lang_label",
            label_visibility="collapsed",
        )
    st.markdown('<div class="vc-header-rule"></div>', unsafe_allow_html=True)


def hero(eyebrow, title, sub=""):
    sub_html = f'<p class="page-sub">{esc(sub)}</p>' if sub else ""
    st.markdown(f'<div class="page-hero"><div class="eyebrow">{esc(eyebrow)}</div>'
                f'<div class="page-title">{esc(title)}</div>{sub_html}</div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section-title">{esc(title)}</div>', unsafe_allow_html=True)


def grid(cards):
    """cards: list of dicts with title, body and optional icon or num. Rendered as one responsive grid."""
    out = []
    for c in cards:
        mark = f'<span class="num">{esc(c["num"])}</span>' if c.get("num") else (f'<div class="ico">{c["icon"]}</div>' if c.get("icon") else "")
        out.append(f'<div class="card">{mark}<h4>{esc(c["title"])}</h4><p>{esc(c["body"])}</p></div>')
    st.markdown(f'<div class="grid">{"".join(out)}</div>', unsafe_allow_html=True)


def chips(items):
    st.markdown('<div class="chips">' + "".join(f'<span class="chip">{esc(i)}</span>' for i in items) + "</div>",
                unsafe_allow_html=True)


FOOT = {
    "en": {
        "about": "VitalCheck AI",
        "about_txt": "Bilingual skin guidance built with our own models. General information only, never a diagnosis.",
        "emergency": "In an emergency",
        "emergency_txt": f"Call Rescue {EMERGENCY_NUMBER}. Do not wait for an app.",
        "project": "Project",
        "project_txt": "5th semester project, University of Lahore.",
        "sup": "Supervised by",
        "contact": "Contact",
        "copy": "Informational tool only. It does not diagnose or prescribe. Always consult a licensed doctor.",
        "idea": "Idea by Muhammad Abdullah Nawaz.",
    },
    "ur": {
        "about": "VitalCheck AI",
        "about_txt": "ہمارے اپنے ماڈلز سے بنی دو زبانی جلد کی رہنمائی۔ صرف عمومی معلومات، تشخیص نہیں۔",
        "emergency": "ایمرجنسی میں",
        "emergency_txt": f"Rescue {EMERGENCY_NUMBER} پر کال کریں۔ ایپ کا انتظار نہ کریں۔",
        "project": "پروجیکٹ",
        "project_txt": "پانچویں سمسٹر کا پروجیکٹ، یونیورسٹی آف لاہور۔",
        "sup": "زیرِ نگرانی",
        "contact": "رابطہ",
        "copy": "یہ صرف معلوماتی ٹول ہے۔ یہ تشخیص یا دوا تجویز نہیں کرتا۔ ہمیشہ مستند ڈاکٹر سے رجوع کریں۔",
        "idea": "آئیڈیا: محمد عبداللہ نواز۔",
    },
}


def footer(lang):
    f = FOOT[lang]
    sup = SUPERVISOR
    st.markdown(
        f'<div class="site-footer">'
        f'<div><b>{esc(f["about"])}</b>{esc(f["about_txt"])}<br>{esc(f["idea"])}</div>'
        f'<div><b>{esc(f["emergency"])}</b>{esc(f["emergency_txt"])}<br><a href="tel:{EMERGENCY_NUMBER}">{EMERGENCY_NUMBER}</a></div>'
        f'<div><b>{esc(f["project"])}</b>{esc(f["project_txt"])}<br>{esc(f["sup"])} {esc(sup["name"])}, {esc(sup["title_" + lang])}</div>'
        f'<div><b>{esc(f["contact"])}</b><a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a><br>'
        f'<a href="mailto:{EMAIL}">{esc(EMAIL)}</a></div>'
        f'<div class="copy">&copy; 2026 VitalCheck AI. {esc(f["copy"])}</div></div>',
        unsafe_allow_html=True)
