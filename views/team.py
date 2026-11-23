"""Team page: supervisor and the four team members."""
import streamlit as st

from src import ui
from src.site_content import SUPERVISOR, TEAM, initials

lang = ui.current_lang()
ROOT = ui.ROOT

TXT = {
    "en": {"eyebrow": "Team", "title": "The people behind VitalCheck AI",
           "sub": "A four-member BSCS team at the University of Lahore, working under faculty supervision.",
           "sup": "Supervisor", "team": "Team members", "lead_note": "Idea and project direction",
           "github": "GitHub", "linkedin": "LinkedIn"},
    "ur": {"eyebrow": "ٹیم", "title": "VitalCheck AI کے پیچھے لوگ",
           "sub": "یونیورسٹی آف لاہور کے چار BSCS طلبہ کی ٹیم، فیکلٹی کی نگرانی میں۔",
           "sup": "سپروائزر", "team": "ٹیم ممبرز", "lead_note": "آئیڈیا اور پروجیکٹ کی سمت",
           "github": "گِٹ ہب", "linkedin": "لنکڈ اِن"},
}
t = TXT[lang]


def photo_url(slug):
    """Returns a data URI for assets/team/<slug>.(jpg|jpeg|png|webp) if it exists, else None."""
    import base64
    for ext, mime in (("jpg", "jpeg"), ("jpeg", "jpeg"), ("png", "png"), ("webp", "webp")):
        p = ROOT / "assets" / "team" / f"{slug}.{ext}"
        if p.exists() and p.stat().st_size < 2_000_000:
            return f"data:image/{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return None


def avatar(slug, name):
    url = photo_url(slug)
    inner = f'<img src="{url}" alt="{ui.esc(name)}">' if url else ui.esc(initials(name))
    return f'<div class="avatar">{inner}</div>'


ui.hero(t["eyebrow"], t["title"], t["sub"])

ui.section(t["sup"])
s = SUPERVISOR
st.markdown(
    f'<div class="sup">{avatar(s["slug"], s["name"])}<div><h4>{ui.esc(s["name"])}</h4>'
    f'<p>{ui.esc(s["title_" + lang])}</p><p>{ui.esc(s["university_" + lang])}</p></div></div>',
    unsafe_allow_html=True)

ui.section(t["team"])
cards = []
for m in TEAM:
    links = ""
    if m["github"]:
        links += f'<a href="{ui.esc(m["github"])}" target="_blank" rel="noopener">{t["github"]}</a>'
    if m["linkedin"]:
        links += f'<a href="{ui.esc(m["linkedin"])}" target="_blank" rel="noopener">{t["linkedin"]}</a>'
    cards.append(
        f'<div class="card">{avatar(m["slug"], m["name"])}<h4>{ui.esc(m["name"])}</h4>'
        f'<span class="role">{ui.esc(m["role_" + lang])}</span><p>{ui.esc(m["bio_" + lang])}</p>'
        f'<div class="links" style="margin-top:.6rem">{links}</div></div>')
st.markdown(f'<div class="grid">{"".join(cards)}</div>', unsafe_allow_html=True)
st.caption(f"{TEAM[0]['name']}: {t['lead_note']}.")
