"""Feedback page: a short form saved to a CSV, plus links to GitHub issues and email."""
import time

import streamlit as st

from src import ui
from src.feedback_store import CATEGORIES, MAX_CHARS, save, validate
from src.site_content import EMAIL, ISSUES_URL

lang = ui.current_lang()

TXT = {
    "en": {"eyebrow": "Feedback", "title": "Tell us what to improve",
           "sub": "Found a wrong answer, a bug or have an idea? It goes straight to the team.",
           "rating": "How useful was VitalCheck AI?", "cat": "Type",
           "cats": {"bug": "Something is broken", "wrong_answer": "A wrong or confusing answer", "idea": "An idea", "other": "Other"},
           "msg": "Your message", "ph": "Describe what happened or what you would like to see",
           "privacy": "Please do not write your name, phone number, address or any medical history.",
           "send": "Send feedback", "thanks": "Thank you. Your feedback was saved.",
           "too_short": "Please write a little more (at least 5 characters).", "too_long": f"Please keep it under {MAX_CHARS} characters.",
           "rating_err": "Please choose a rating.", "limit": "You have sent enough feedback for this session. Thank you.",
           "error": "Could not save feedback right now. Please use GitHub or email below.",
           "other": "Other ways to reach us", "gh": "Open an issue on GitHub", "mail": "Email the team"},
    "ur": {"eyebrow": "رائے", "title": "بتائیں کیا بہتر کریں",
           "sub": "غلط جواب، خرابی یا کوئی آئیڈیا؟ یہ سیدھا ٹیم تک پہنچتا ہے۔",
           "rating": "VitalCheck AI کتنا مفید رہا؟", "cat": "قسم",
           "cats": {"bug": "کوئی چیز خراب ہے", "wrong_answer": "غلط یا الجھا ہوا جواب", "idea": "کوئی آئیڈیا", "other": "دیگر"},
           "msg": "آپ کا پیغام", "ph": "بتائیں کیا ہوا یا آپ کیا دیکھنا چاہتے ہیں",
           "privacy": "براہ کرم اپنا نام، فون نمبر، پتہ یا طبی تاریخ نہ لکھیں۔",
           "send": "رائے بھیجیں", "thanks": "شکریہ۔ آپ کی رائے محفوظ ہو گئی۔",
           "too_short": "براہ کرم کچھ مزید لکھیں (کم از کم 5 حروف)۔", "too_long": f"براہ کرم {MAX_CHARS} حروف سے کم رکھیں۔",
           "rating_err": "براہ کرم ریٹنگ چنیں۔", "limit": "اس سیشن کے لیے کافی رائے آ چکی۔ شکریہ۔",
           "error": "ابھی رائے محفوظ نہیں ہو سکی۔ براہ کرم نیچے گِٹ ہب یا ای میل استعمال کریں۔",
           "other": "رابطے کے دوسرے طریقے", "gh": "گِٹ ہب پر مسئلہ لکھیں", "mail": "ٹیم کو ای میل کریں"},
}
t = TXT[lang]
MAX_PER_SESSION = 3

ui.hero(t["eyebrow"], t["title"], t["sub"])

sent = st.session_state.setdefault("feedback_count", 0)
with st.form("feedback_form", clear_on_submit=True):
    stars = st.feedback("stars", key="fb_stars")          # 0..4 or None
    st.caption(t["rating"])
    category = st.selectbox(t["cat"], CATEGORIES, format_func=lambda c: t["cats"][c])
    message = st.text_area(t["msg"], placeholder=t["ph"], max_chars=MAX_CHARS)
    st.caption(t["privacy"])
    submitted = st.form_submit_button(t["send"])

if submitted:
    rating = None if stars is None else stars + 1
    ok, code = validate(rating, category, message)
    if sent >= MAX_PER_SESSION:
        st.warning(t["limit"])
    elif not ok:
        st.warning(t["rating_err"] if code == "rating" else t[code] if code in t else t["error"])
    else:
        try:
            save(rating, category, message)
            st.session_state.feedback_count = sent + 1
            st.success(t["thanks"])
        except OSError:
            st.error(t["error"])

ui.section(t["other"])
st.markdown(f'<div class="links"><a href="{ISSUES_URL}" target="_blank" rel="noopener">{t["gh"]}</a>'
            f'<a href="mailto:{EMAIL}">{t["mail"]}</a></div>', unsafe_allow_html=True)
