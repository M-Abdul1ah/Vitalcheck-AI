"""
VitalCheck AI - Streamlit front end.

Every message goes through: input checks -> emergency gate -> knowledge base search
-> answer built from the matches -> output check. No AI model or API key is needed.
The own skin-photo model (DermaVC-Net) will be added as a vision step.
"""
import os
from pathlib import Path

# Model already downloaded -> skip the slow online check on every start
_hf_cache = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
if (_hf_cache / "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2").exists():
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
import html
import time

import streamlit as st

from src.intent import classify_intent
from src.limits import MAX_INPUT_CHARS as MAX_CHARS, check_input_length, check_rate_limit
from src.input_guard import is_too_vague
from src.output_check import apply_output_check
from src.report_gen import build_report
from src.safety_check import check_emergency
from src.trace import make_trace, ms_since, skipped
from src.trace import step as trace_step
from src.vision_agent import ImageError, prepare_image
from src.workflow_ui import render_trace


st.set_page_config(
    page_title="VitalCheck AI",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Text (English / Urdu)
# ----------------------------------------------------------------------------
TEXT = {
    "en": {
        "title": "What is your skin telling you?",
        "sub": "Describe your symptoms in English or Urdu. You get information on the closest matching skin conditions and when to see a doctor.",
        "notice": "General information only, not a diagnosis. In an emergency call Rescue 1122.",
        "placeholder": "Describe your skin symptoms",
        "examples": [
            "Itchy red scaly patches on my elbows",
            "A round ring-shaped rash that keeps spreading",
            "Painful pimples and blackheads on my face",
        ],
        "sources": "Knowledge base matches",
        "how_title": "How it works",
        "steps": ["Emergency check", "Knowledge base search", "Answer from the knowledge base"],
        "status": "System status",
        "safety": "Emergency check",
        "kb": "Knowledge base",
        "on": "ready",
        "off": "offline",
        "clear": "Clear chat",
        "download": "Download report (PDF)",
        "chat_tab": "Chat",
        "workflow_tab": "Workflow",
        "photo_label": "Add a photo (optional)",
        "photo_help": "JPG, PNG or WEBP, up to 5 MB. Type a short message to send it. Avoid faces and ID documents.",
        "photo_privacy": "Photo ready. Type a message and press Enter to send it together. The photo is never stored.",
        "photo_error": "The photo could not be processed.",
        "photo_too_large": "This photo is bigger than 5 MB. Choose a smaller one.",
        "photo_bad_type": "Only JPG, PNG or WEBP photos are supported.",
        "photo_unreadable": "This file could not be read as a photo.",
        "photo_too_small": "This photo is too small. Use one that is at least 100 pixels wide.",
        "photo_pending": "Photo received. Photo analysis is not connected yet, so this answer uses your text only.",
        "privacy": "Do not enter your name, phone number or address.",
        "too_long": f"Message is too long. Keep it under {MAX_CHARS} characters.",
        "limit": "Session limit reached. Refresh the page to start a new chat.",
        "kb_offline": "The knowledge base is not available, so no answer can be given.",
        "answer_intro": "Closest matches in our knowledge base for your symptoms. This is general information, not a diagnosis.",
        "no_match": "I could not match that to a skin problem. Please describe it: where it is, how long you have had it, and whether it itches or hurts. If you are worried, please see a doctor.",
        "greeting": "Hello! I am Vital Check AI. Tell me about your skin problem: where it is, how long you have had it, and whether it itches or hurts.",
        "thanks": "You are welcome. If anything changes or gets worse, please see a doctor.",
        "bye": "Take care. If your skin problem gets worse, please see a doctor.",
        "need_details": "Please tell us a little more so the right information can be found: where on the body is the problem, how long have you had it, is it itchy or painful, and is it spreading? You can also add a photo.",
        "report_error": "The report could not be created.",
        "chunks": "chunks",
    },
    "ur": {
        "title": "آپ کی جلد کیا کہہ رہی ہے؟",
        "sub": "اپنی علامات اردو یا انگریزی میں لکھیں۔ ملتی جلتی جلدی بیماریوں کی معلومات اور ڈاکٹر سے ملنے کا مشورہ پائیں۔",
        "notice": "یہ صرف عمومی معلومات ہیں، تشخیص نہیں۔ ایمرجنسی میں Rescue 1122 پر کال کریں۔",
        "placeholder": "اپنی جلد کی علامات لکھیں",
        "examples": [
            "میری کہنیوں پر خارش اور سرخ خشک دھبے ہیں",
            "جلد پر گول دائرے جیسا خارش والا نشان پھیل رہا ہے",
            "چہرے پر تکلیف دہ دانے اور بلیک ہیڈز ہیں",
        ],
        "sources": "علمی ذخیرے سے ملتی جلتی معلومات",
        "how_title": "یہ کیسے کام کرتا ہے",
        "steps": ["ہنگامی علامات کی جانچ", "علمی ذخیرے میں تلاش", "علمی ذخیرے سے جواب"],
        "status": "سسٹم کی حالت",
        "safety": "ہنگامی جانچ",
        "kb": "علمی ذخیرہ",
        "on": "فعال",
        "off": "بند",
        "clear": "چیٹ صاف کریں",
        "download": "رپورٹ ڈاؤن لوڈ کریں (PDF)",
        "chat_tab": "چیٹ",
        "workflow_tab": "ورک فلو",
        "photo_label": "تصویر شامل کریں (اختیاری)",
        "photo_help": "JPG، PNG یا WEBP، زیادہ سے زیادہ 5 MB۔ بھیجنے کے لیے مختصر پیغام بھی لکھیں۔ چہرے اور شناختی کاغذات سے پرہیز کریں۔",
        "photo_privacy": "تصویر تیار ہے۔ پیغام لکھ کر Enter دبائیں تو تصویر ساتھ جائے گی۔ تصویر کبھی محفوظ نہیں کی جاتی۔",
        "photo_error": "تصویر پر عمل نہیں ہو سکا۔",
        "photo_too_large": "یہ تصویر 5 MB سے بڑی ہے۔ چھوٹی تصویر چنیں۔",
        "photo_bad_type": "صرف JPG، PNG یا WEBP تصاویر قبول ہیں۔",
        "photo_unreadable": "یہ فائل تصویر کے طور پر نہیں پڑھی جا سکی۔",
        "photo_too_small": "یہ تصویر بہت چھوٹی ہے۔ کم از کم 100 پکسل چوڑی تصویر استعمال کریں۔",
        "photo_pending": "تصویر مل گئی۔ تصویر کا تجزیہ ابھی منسلک نہیں ہے، اس لیے یہ جواب صرف آپ کی تحریر پر مبنی ہے۔",
        "privacy": "اپنا نام، فون نمبر یا پتہ درج نہ کریں۔",
        "too_long": f"پیغام بہت لمبا ہے۔ اسے {MAX_CHARS} حروف سے کم رکھیں۔",
        "limit": "اس سیشن کی حد پوری ہو گئی۔ نئی چیٹ کے لیے صفحہ ری فریش کریں۔",
        "kb_offline": "علمی ذخیرہ دستیاب نہیں، اس لیے جواب نہیں دیا جا سکتا۔",
        "answer_intro": "آپ کی علامات سے ملتی جلتی معلومات ہمارے علمی ذخیرے سے۔ یہ عمومی معلومات ہیں، تشخیص نہیں۔",
        "no_match": "میں اسے جلد کے کسی مسئلے سے نہیں ملا سکا۔ براہ کرم بتائیں کہ مسئلہ کہاں ہے، کتنے عرصے سے ہے اور خارش یا درد ہے یا نہیں۔ فکر ہو تو ڈاکٹر سے ملیں۔",
        "greeting": "السلام علیکم! میں Vital Check AI ہوں۔ اپنی جلد کا مسئلہ بتائیں: کہاں ہے، کتنے عرصے سے ہے اور خارش یا درد ہے یا نہیں۔",
        "thanks": "خوش آمدید۔ اگر کچھ بدلے یا بگڑے تو ڈاکٹر سے ملیں۔",
        "bye": "خیال رکھیں۔ اگر جلد کا مسئلہ بڑھے تو ڈاکٹر سے ملیں۔",
        "need_details": "براہ کرم کچھ مزید بتائیں تاکہ درست معلومات تلاش کی جا سکیں: مسئلہ جسم کے کس حصے میں ہے، کتنے دن سے ہے، کیا خارش یا درد ہے، اور کیا یہ پھیل رہا ہے؟ آپ تصویر بھی شامل کر سکتے ہیں۔",
        "report_error": "رپورٹ نہیں بن سکی۔",
        "chunks": "حصے",
    },
}

EXTRA = {
    "en": {
        "hint": "Use the + button in the chat box to add a skin photo.",
        "chips": ["Urdu and English", "Emergency check", "Photos never stored"],
        "need_text": "Add a short description of your symptoms together with the photo.",
    },
    "ur": {
        "hint": "تصویر شامل کرنے کے لیے چیٹ باکس کا + بٹن استعمال کریں۔",
        "chips": ["اردو اور انگریزی", "ہنگامی جانچ", "تصاویر محفوظ نہیں کی جاتیں"],
        "need_text": "تصویر کے ساتھ اپنی علامات کی مختصر تفصیل بھی لکھیں۔",
    },
}

lang_label = st.session_state.get("lang_label", "English")
lang = "ur" if lang_label == "اردو" else "en"
t = {**TEXT[lang], **EXTRA[lang]}

# ----------------------------------------------------------------------------
# Look and feel
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=Public+Sans:wght@400;500;600&family=Noto+Nastaliq+Urdu:wght@400;600&display=swap');

:root {
  --ink: #16302B;
  --muted: #5B6F6A;
  --brand: #0B4F4A;
  --brand-soft: #E3EFEC;
  --blush: #F6D9CE;
  --page: #F5F7F6;
  --line: #D5E0DC;
  --danger: #B3261E;
  --danger-soft: #FBE9E7;
  --warn-soft: #FFF3D1;
}

.stApp { background: var(--page); color: var(--ink); }
.stApp p, .stApp li, .stApp textarea, .stApp button, .stApp label { font-family: 'Public Sans', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 760px; padding-top: 1.6rem; padding-bottom: 6rem; }

/* wordmark */
.brand { display: flex; align-items: center; gap: .6rem; font-family: 'Bricolage Grotesque', sans-serif;
         font-weight: 700; font-size: 1.25rem; color: var(--brand); padding-top: .35rem; }
.brand-mark { width: 1.9rem; height: 1.9rem; border-radius: 50%; background: var(--brand); color: #fff;
              display: inline-flex; align-items: center; justify-content: center; font-size: 1.25rem; line-height: 1; }

/* language switch */
div[role="radiogroup"] { justify-content: flex-end; gap: .25rem; }

/* disclaimer strip */
.notice { background: var(--warn-soft); border-radius: 10px; padding: .55rem .9rem; margin: .9rem 0 0;
          font-size: .88rem; color: #5A4A10; }

/* hero: the headline is the memorable element, everything else stays quiet */
.hero-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 3rem; line-height: 1.05;
              letter-spacing: -0.025em; color: var(--brand); margin: 3rem 0 .9rem; max-width: 14ch; }
.hero-sub { font-size: 1.05rem; line-height: 1.6; color: var(--muted); max-width: 52ch; margin: 0 0 1.6rem; }

/* example buttons and other buttons */
div.stButton > button, div.stDownloadButton > button { width: 100%; justify-content: flex-start; text-align: start; background: #fff; color: var(--ink);
    border: 1px solid var(--line); border-radius: 12px; padding: .65rem 1rem; font-weight: 500;
    transition: border-color .15s, background .15s; }
div.stButton > button:hover, div.stDownloadButton > button:hover { border-color: var(--brand); background: var(--brand-soft); color: var(--brand); }
div.stButton > button:focus-visible, div.stDownloadButton > button:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }

/* conversation: user = blush bubble, assistant = ruled panel */
.user-row { display: flex; justify-content: flex-end; margin: 1.2rem 0 .6rem; }
.user-bubble { background: var(--blush); color: var(--ink); padding: .7rem 1rem; max-width: 85%;
               border-radius: 18px 18px 4px 18px; line-height: 1.55; overflow-wrap: anywhere; }
[data-testid="stChatMessage"] { background: #fff; border: 1px solid var(--line); border-left: 4px solid var(--brand);
    border-radius: 6px 16px 16px 6px; padding: 1rem 1.15rem; margin: .4rem 0 1rem; }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { line-height: 1.65; }
[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 10px; background: var(--page); }

/* emergency card */
.alert { background: var(--danger-soft); border: 1px solid #F0B8B2; border-left: 5px solid var(--danger);
         border-radius: 6px 14px 14px 6px; padding: 1rem 1.15rem; margin: .4rem 0 1rem; color: #5E1410;
         font-weight: 500; line-height: 1.65; }

/* photo uploader */
[data-testid="stFileUploader"] section { border: 1px dashed var(--line); border-radius: 12px; background: #fff; }

/* input */
[data-testid="stChatInput"] { border-radius: 16px; }

/* sidebar */
[data-testid="stSidebar"] { background: var(--brand-soft); border-right: 1px solid var(--line); }
.step { display: flex; gap: .7rem; align-items: flex-start; margin: .5rem 0; font-size: .95rem; }
.step-n { flex: none; width: 1.5rem; height: 1.5rem; border-radius: 50%; background: var(--brand); color: #fff;
          font-size: .8rem; font-weight: 600; display: inline-flex; align-items: center; justify-content: center; }
.pill-row { display: flex; justify-content: space-between; align-items: center; margin: .4rem 0; font-size: .92rem; }
.pill { border-radius: 999px; padding: .1rem .7rem; font-size: .8rem; font-weight: 600; }
.pill.ok { background: #CFE8DD; color: #0B4F4A; }
.pill.off { background: #F6D9CE; color: #7A2E12; }
.side-note { font-size: .82rem; color: var(--muted); line-height: 1.5; }

@media (max-width: 640px) { .hero-title { font-size: 2.2rem; margin-top: 1.6rem; } }
</style>
"""

RTL_CSS = """
<style>
.hero-title, .hero-sub, .notice, .alert, .step, .side-note,
[data-testid="stChatMessage"] .stMarkdown, div.stButton > button, div.stDownloadButton > button { direction: rtl; text-align: right; }
.hero-title, .hero-sub, .notice, .alert, .step, .side-note, .pill,
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li, div.stButton > button, div.stDownloadButton > button {
  font-family: 'Noto Nastaliq Urdu', serif; line-height: 2.2; }
.hero-title { line-height: 1.9; max-width: none; }
.brand { direction: ltr; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)
if lang == "ur":
    st.markdown(RTL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.chips { display: flex; flex-wrap: wrap; gap: .5rem; margin: 0 0 .8rem; }
.chip { background: #fff; border: 1px solid var(--line); border-radius: 999px;
        padding: .25rem .8rem; font-size: .82rem; font-weight: 600; color: var(--brand); }
.hint { font-size: .9rem; color: var(--muted); margin: 0 0 1.2rem; }
[data-testid="stChatInput"] { box-shadow: 0 2px 14px rgba(11,79,74,.12); border: 1px solid var(--line); }
[data-testid="stChatMessage"] { border: 1px solid var(--line); border-left: 4px solid var(--brand); }
</style>
""", unsafe_allow_html=True)
if lang == "ur":
    st.markdown("<style>.hint,.chips{direction:rtl;text-align:right}</style>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Backend (loaded once per server, not on every click)
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Getting things ready...")
def load_backend():
    backend = {"retrieve": None, "retrieve_scored": None, "kb_chunks": 0, "kb_error": None}
    try:
        from src.embed_store import build, get_collection
        if get_collection().count() == 0:   # first start on a fresh server: chroma_db is not in Git
            build()
        backend["kb_chunks"] = get_collection().count()
        from src.retriever import retrieve, retrieve_with_scores
        backend["retrieve"] = retrieve
        backend["retrieve_scored"] = retrieve_with_scores
    except Exception as e:
        backend["kb_error"] = str(e)
    return backend


backend = load_backend()

# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "req_times" not in st.session_state:
    st.session_state.req_times = []   # recent request times for the rate limit
if "photo_key" not in st.session_state:
    st.session_state.photo_key = 0   # changing this key empties the photo box after a photo is sent
if "last_trace" not in st.session_state:
    st.session_state.last_trace = None   # most recent message's step-by-step record, for the Workflow tab


def set_pending(text):
    st.session_state.pending = text


def clear_chat():
    st.session_state.messages = []


# ----------------------------------------------------------------------------
# Rendering helpers
# ----------------------------------------------------------------------------
def render_user(text, photo=None):
    if photo:
        _, right = st.columns([2, 1])
        right.image(photo)
    st.markdown(
        f'<div class="user-row"><div class="user-bubble" dir="auto">{html.escape(text)}</div></div>',
        unsafe_allow_html=True,
    )


def render_sources(sources, expanded=False):
    if not sources:
        return
    with st.expander(t["sources"], expanded=expanded):
        for s in sources:
            st.markdown(f"**{s['title']}**")
            st.caption(s["text"][:300] + ("..." if len(s["text"]) > 300 else ""))


def render_message(m):
    if m["role"] == "user":
        render_user(m["content"], m.get("photo"))
    elif m.get("kind") == "alert":
        st.markdown(f'<div class="alert">{html.escape(m["content"])}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="🩺"):
            st.markdown(m["content"])
            if m.get("photo_note"):
                st.caption(t["photo_pending"])
            render_sources(m.get("sources"))


# Below this cosine score a match is treated as "not relevant" (tune it with the 40-query test set).
MIN_MATCH_SCORE = float(os.getenv("MIN_MATCH_SCORE", "0.30"))


def to_sources(chunks):
    return [{"title": c.split(":")[0].strip(), "text": c} for c in chunks]


def build_answer(sources):
    """Answer text built from the knowledge base matches (no AI model): title + first sentence of each."""
    if not sources:
        return t["no_match"]
    lines = [t["answer_intro"], ""]
    for s in sources:
        rest = s["text"].split(":", 1)[-1].strip()
        first = rest.split(". ")[0].rstrip(".") + "."
        lines.append(f"- **{s['title']}**: {first}")
    return "\n".join(lines)


def finish(prompt, steps, tone, end, message):
    """Save the trace and the assistant message, then show the message."""
    st.session_state.last_trace = make_trace(prompt, steps, tone, end)
    st.session_state.messages.append(message)
    render_message(message)


def handle(prompt, photo=None):
    prompt = prompt.strip()
    if not prompt:
        return
    ok, _ = check_input_length(prompt)
    if not ok:
        st.warning(t["too_long"])
        return
    ok, _, st.session_state.req_times = check_rate_limit(st.session_state.req_times)
    if not ok:
        st.warning(t["limit"])
        return

    st.session_state.messages.append({"role": "user", "content": prompt, "photo": photo})
    render_user(prompt, photo)

    urdu = any("\u0600" <= c <= "\u06FF" for c in prompt)
    language = "Urdu" if urdu else "English"
    steps = [trace_step(
        "user", "done", sub="text + photo" if photo else "sent", inn="Chat box",
        out=f'"{prompt[:60]}" - language: {language}, {len(prompt)} characters',
        log=f"Message received ({language}, {len(prompt)} characters).",
    )]
    steps[-1]["edge"] = "user-safety"

    # 1) emergency gate: plain rules, runs first
    t0 = time.perf_counter()
    urgent = check_emergency(prompt)
    ms = ms_since(t0)
    if urgent:
        steps.append(trace_step("safety", "alert", ms=ms, inn="Message text",
                                out="Red flag matched. Decision: stop and escalate.",
                                log="Red flag found. Pipeline stopped."))
        steps[-1]["edge"] = "safety-resolution"
        steps.append(skipped(["photo", "retriever", "ai", "output"],
                             "Photo prep, retriever, answer and output check are not needed."))
        steps.append(trace_step("resolution", "alert", sub="Escalated", inn="Result from the safety gate",
                                out="ESCALATED_EMERGENCY - Rescue 1122 warning shown",
                                log="Emergency warning shown with Rescue 1122."))
        finish(prompt, steps, "danger", urgent, {"role": "assistant", "kind": "alert", "content": urgent})
        return
    steps.append(trace_step("safety", "done", ms=ms, inn="Message text",
                            out="No red flags found. Decision: continue.",
                            log="No red flags found. Message passed on."))
    steps[-1]["edge"] = "safety-photo"

    # 1a) small talk: greetings / thanks / goodbye get a friendly reply, no search
    intent = classify_intent(prompt) if not photo else "other"
    if intent != "other":
        steps[-1]["log"] = f"No red flags. Message is small talk ({intent}), so no search is needed."
        steps[-1]["edge"] = "safety-resolution"
        steps.append(skipped(["photo", "retriever", "ai", "output"], "Not needed for small talk."))
        steps.append(trace_step("resolution", "done", sub="Small talk", inn="Result from the intent check",
                                out=f"SMALL_TALK_{intent.upper()}", log="Friendly reply shown."))
        finish(prompt, steps, "success", "Resolution: small talk, no medical search.",
               {"role": "assistant", "kind": "answer", "content": t[intent], "sources": []})
        return

    # 1b) too vague to search (for example "I need help"): ask for details, do not print knowledge-base matches
    if is_too_vague(prompt):
        steps[-1]["edge"] = "safety-resolution"
        steps.append(skipped(["photo", "retriever", "ai", "output"], "The message is too vague to search."))
        steps.append(trace_step("resolution", "warn", sub="Need details", inn="Message text",
                                out="NEEDS_DETAILS - asked the user for more information",
                                log="Message too vague: asked for more details. Knowledge base not searched."))
        finish(prompt, steps, "warning", t["need_details"],
               {"role": "assistant", "kind": "info", "content": t["need_details"]})
        return

    # 2) photo prep already happened before handle() was called (see the chat box below)
    if photo:
        steps.append(trace_step("photo", "done", ms=1, inn=f"Photo, {len(photo)} bytes after cleanup",
                                out="Cleaned earlier: resized, metadata removed.",
                                log="Photo already cleaned; ready to use."))
    else:
        steps.append(trace_step("photo", "skip", sub="no photo", inn="No photo attached",
                                out="Step skipped.", log="No photo attached, so this step is skipped."))
    steps[-1]["edge"] = "photo-retriever"

    # 3) knowledge base search
    if backend["retrieve"] is None:
        steps.append(trace_step("retriever", "warn", sub="offline", inn=f"Search text: {prompt[:50]}",
                                out="Knowledge base unavailable.", log="Knowledge base not available."))
        steps.append(skipped(["ai", "output"], "Answer and output check need the knowledge base."))
        steps.append(trace_step("resolution", "warn", sub="Unavailable", inn="Results from all agents",
                                out="KB_UNAVAILABLE", log="No answer given: knowledge base offline."))
        finish(prompt, steps, "warning", t["kb_offline"], {"role": "assistant", "kind": "error", "content": t["kb_offline"]})
        return

    t0 = time.perf_counter()
    try:
        scored = backend["retrieve_scored"](prompt)
        sources = to_sources([doc for doc, _ in scored])
        matches = [[s["title"], score] for s, (_, score) in zip(sources, scored)]
        if not scored or max(score for _, score in scored) < MIN_MATCH_SCORE:
            sources = []          # nothing relevant: ask the user to describe the problem instead
    except Exception:
        sources, matches = [], None
    ms = ms_since(t0)
    best = ", ".join(s["title"] for s in sources[:3]) if sources else "none"
    step_kwargs = {"matches": matches} if (matches and sources) else {
        "out": f"No relevant match (best score below {MIN_MATCH_SCORE}). Asking the user to describe the problem."}
    steps.append(trace_step("retriever", "done", ms=ms, inn=f"Search text: {prompt[:60]}",
                            log=f"{len(sources)} matches found. Best: {best}.", **step_kwargs))
    steps[-1]["edge"] = "retriever-ai"

    # 4) answer built from the matches (no AI model)
    t0 = time.perf_counter()
    answer = build_answer(sources)
    steps.append(trace_step("ai", "done", ms=ms_since(t0), inn=f"{len(sources)} matches",
                            out=f"Answer built from {len(sources)} knowledge base matches.",
                            log="Answer built from the knowledge base matches. No AI model is used."))
    steps[-1]["edge"] = "ai-output"

    # 5) output check: rules on the final text
    t0 = time.perf_counter()
    text, report = apply_output_check(answer)
    oc_ms = ms_since(t0)
    if report["action"] == "blocked":
        out = (f"Medicine names: {len(report['medicine'])}. "
               f"Diagnosis phrases: {len(report['diagnosis'])}. Answer blocked.")
        log = "Answer blocked: contained medicine or diagnosis wording."
        state, sub, tone = "warn", "Blocked", "warning"
        end = "Resolution: the answer was held back by the output check; a doctor visit is advised."
    else:
        out = f"Medicine names: 0. Diagnosis phrases: 0. Doctor advice: {'present' if report['doctor'] else 'added'}."
        log = "No medicine names or diagnosis wording found."
        state, sub, tone = "done", "Answered", "success"
        end = "Resolution: answered from the knowledge base, with a doctor visit advised."
    steps.append(trace_step("output", state, ms=oc_ms, inn=f"Answer, {report['words']} words", out=out, log=log))
    steps[-1]["edge"] = "output-resolution"
    steps.append(trace_step("resolution", state, sub=sub, inn="Results from all agents",
                            out=f"ANSWERED_FROM_KB - {sub.upper()}", log=log))
    finish(prompt, steps, tone, end,
           {"role": "assistant", "kind": "answer", "content": text, "sources": sources, "photo_note": bool(photo)})


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def pill(label, ok):
    cls, word = ("ok", t["on"]) if ok else ("off", t["off"])
    return f'<div class="pill-row"><span>{label}</span><span class="pill {cls}">{word}</span></div>'


with st.sidebar:
    st.markdown(f"**{t['how_title']}**")
    for i, label in enumerate(t["steps"], 1):
        st.markdown(f'<div class="step"><span class="step-n">{i}</span><span>{label}</span></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown(f"**{t['status']}**")
    kb_ok = backend["retrieve"] is not None
    st.markdown(
        pill(t["safety"], True)
        + pill(f"{t['kb']} ({backend['kb_chunks']} {t['chunks']})", kb_ok),
        unsafe_allow_html=True,
    )
    st.divider()
    report_slot = st.empty()   # filled at the end of the script, after the newest answer exists
    st.button(t["clear"], on_click=clear_chat)
    st.markdown(f'<p class="side-note">{t["privacy"]}</p>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Main page
# ----------------------------------------------------------------------------
pending = st.session_state.pop("pending", None)
typed = st.chat_input(
    t["placeholder"], accept_file=True, file_type=["jpg", "jpeg", "png", "webp"]
)
text_in, file_in = "", None
if typed:
    text_in = (typed["text"] or "").strip()
    file_in = typed["files"][0] if typed["files"] else None
prompt = text_in or pending

top_l, top_r = st.columns([3, 2])
with top_l:
    st.markdown('<div class="brand"><span class="brand-mark">+</span>VitalCheck AI</div>', unsafe_allow_html=True)
with top_r:
    st.radio("Language", ["English", "اردو"], horizontal=True, key="lang_label", label_visibility="collapsed")

chat_tab, workflow_tab = st.tabs([t["chat_tab"], t["workflow_tab"]])

with chat_tab:
    st.markdown(f'<div class="notice">{t["notice"]}</div>', unsafe_allow_html=True)

    if not st.session_state.messages and not prompt:
        st.markdown(f'<div class="hero-title">{t["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="hero-sub">{t["sub"]}</p>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip">{c}</span>' for c in t["chips"])
        st.markdown(f'<div class="chips">{chips}</div><p class="hint">{t["hint"]}</p>', unsafe_allow_html=True)
        for i, example in enumerate(t["examples"]):
            st.button(example, key=f"ex{i}", on_click=set_pending, args=(example,))

    for m in st.session_state.messages:
        render_message(m)

    if file_in is not None and not text_in:
        st.warning(t["need_text"])

    if prompt:
        photo_bytes = None
        if file_in is not None:
            try:
                photo_bytes = prepare_image(file_in.getvalue())
            except ImageError as e:
                st.warning(t[f"photo_{e.code}"])
            except Exception as e:
                st.warning(f"{t['photo_error']} ({type(e).__name__})")
        handle(prompt, photo_bytes)

with workflow_tab:
    render_trace(st.session_state.last_trace, lang)

# PDF report button (built last so it includes the message that was just answered)
if any(m["role"] == "assistant" for m in st.session_state.messages):
    try:
        with report_slot:
            st.download_button(
                t["download"],
                data=build_report(st.session_state.messages, lang),
                file_name="vitalcheck_report.pdf",
                mime="application/pdf",
            )
    except Exception as e:
        report_slot.caption(f"{t['report_error']} ({type(e).__name__})")
