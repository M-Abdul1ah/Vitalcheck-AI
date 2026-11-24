"""
VitalCheck AI - Streamlit entry point (router).

This file only sets up the page, the shared look, the header and the footer, and then runs the page the
user picked. The pages live in views/: home (the chat), vision, about, team, models, help, feedback.
"""
import os
from pathlib import Path

# Model already downloaded -> skip the slow online check on every start
_hf_cache = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
if (_hf_cache / "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2").exists():
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

import streamlit as st

from src import ui

st.set_page_config(page_title="VitalCheck AI", page_icon="🩺", layout="centered", initial_sidebar_state="expanded")

NAV = {
    "en": {"home": "Home", "vision": "Our Vision", "about": "About", "team": "Team", "models": "Models",
           "help": "Help", "feedback": "Feedback"},
    "ur": {"home": "ہوم", "vision": "ہمارا وژن", "about": "تعارف", "team": "ٹیم", "models": "ماڈلز",
           "help": "مدد", "feedback": "رائے"},
}

lang = ui.current_lang()
ui.load_css(lang)
ui.header()
lang = ui.current_lang()   # the language switch was just drawn, so read it again

n = NAV[lang]
pages = [
    st.Page("views/home.py", title=n["home"], icon="🩺", default=True),
    st.Page("views/vision.py", title=n["vision"], icon="🎯", url_path="vision"),
    st.Page("views/about.py", title=n["about"], icon="ℹ️", url_path="about"),
    st.Page("views/team.py", title=n["team"], icon="👥", url_path="team"),
    st.Page("views/models.py", title=n["models"], icon="📊", url_path="models"),
    st.Page("views/help.py", title=n["help"], icon="❓", url_path="help"),
    st.Page("views/feedback.py", title=n["feedback"], icon="💬", url_path="feedback"),
]
page = st.navigation(pages, position="sidebar")
page.run()

ui.footer(lang)
