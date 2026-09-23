"""
VitalCheck AI - Streamlit front end.

Every message goes through: input checks -> emergency gate -> knowledge search -> AI answer (streamed).
The safety gate and knowledge search work without a Groq key, so the whole UI can be tested in the browser.
"""
import html

import streamlit as st

from src.safety_check import check_emergency

try:
    from src.vision_agent import ImageError, prepare_image   # photo preparation (needs Pillow)
except Exception:
    prepare_image = None

try:
    from src.report_gen import build_report   # PDF report (needs fpdf2 + uharfbuzz)
except Exception:
    build_report = None

MAX_CHARS = 500      # longest message accepted
MAX_REQUESTS = 20    # messages allowed per browser session (protects the free Groq quota)

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
        "sub": "Describe your symptoms in English or Urdu. You get possible causes, a self-care tip and when to see a doctor.",
        "notice": "General information only, not a diagnosis. In an emergency call Rescue 1122.",
        "placeholder": "Describe your skin symptoms",
        "examples": [
            "Itchy red scaly patches on my elbows",
            "A round ring-shaped rash that keeps spreading",
            "Painful pimples and blackheads on my face",
        ],
        "sources": "Knowledge base matches",
        "how_title": "How it works",
        "steps": ["Emergency check", "Knowledge base search", "AI answer"],
        "status": "System status",
        "safety": "Emergency check",
        "kb": "Knowledge base",
        "ai": "AI model",
        "on": "ready",
        "off": "offline",
        "clear": "Clear chat",
        "download": "Download report (PDF)",
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
        "ai_offline": "The AI model is not connected yet. Here is what the knowledge base found for your symptoms.",
        "ai_error": "The AI could not answer right now. Wait a moment and send the message again.",
        "kb_offline": "The knowledge base is not available, so no answer can be given.",
        "chunks": "chunks",
    },
    "ur": {
        "title": "آپ کی جلد کیا کہہ رہی ہے؟",
        "sub": "اپنی علامات اردو یا انگریزی میں لکھیں۔ ممکنہ وجوہات، خود دیکھ بھال کا مشورہ اور ڈاکٹر سے ملنے کا وقت جانیں۔",
        "notice": "یہ صرف عمومی معلومات ہیں، تشخیص نہیں۔ ایمرجنسی میں Rescue 1122 پر کال کریں۔",
        "placeholder": "اپنی جلد کی علامات لکھیں",
        "examples": [
            "میری کہنیوں پر خارش اور سرخ خشک دھبے ہیں",
            "جلد پر گول دائرے جیسا خارش والا نشان پھیل رہا ہے",
            "چہرے پر تکلیف دہ دانے اور بلیک ہیڈز ہیں",
        ],
        "sources": "علمی ذخیرے سے ملتی جلتی معلومات",
        "how_title": "یہ کیسے کام کرتا ہے",
        "steps": ["ہنگامی علامات کی جانچ", "علمی ذخیرے میں تلاش", "AI کا جواب"],
        "status": "سسٹم کی حالت",
        "safety": "ہنگامی جانچ",
        "kb": "علمی ذخیرہ",
        "ai": "AI ماڈل",
        "on": "فعال",
        "off": "بند",
        "clear": "چیٹ صاف کریں",
        "download": "رپورٹ ڈاؤن لوڈ کریں (PDF)",
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
        "ai_offline": "AI ماڈل ابھی منسلک نہیں ہے۔ آپ کی علامات کے لیے علمی ذخیرے میں یہ ملا۔",
        "ai_error": "AI ابھی جواب نہیں دے سکا۔ کچھ دیر بعد پیغام دوبارہ بھیجیں۔",
        "kb_offline": "علمی ذخیرہ دستیاب نہیں، اس لیے جواب نہیں دیا جا سکتا۔",
        "chunks": "حصے",
    },
}

lang_label = st.session_state.get("lang_label", "English")
lang = "ur" if lang_label == "اردو" else "en"
t = TEXT[lang]

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


# ----------------------------------------------------------------------------
# Backend (loaded once per server, not on every click)
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Getting things ready...")
def load_backend():
    backend = {"retrieve": None, "stream": None, "kb_chunks": 0, "kb_error": None, "ai_error": None}
    try:
        from src.embed_store import build, get_collection
        if get_collection().count() == 0:   # first start on a fresh server: chroma_db is not in Git
            build()
        backend["kb_chunks"] = get_collection().count()
        from src.retriever import retrieve
        backend["retrieve"] = retrieve
    except Exception as e:
        backend["kb_error"] = str(e)
    try:
        from src.chains.symptom_chain import check_symptoms_stream
        backend["stream"] = check_symptoms_stream
    except Exception as e:                  # for example: GROQ_API_KEY missing
        backend["ai_error"] = str(e)
    return backend


backend = load_backend()

# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "count" not in st.session_state:
    st.session_state.count = 0
if "photo_key" not in st.session_state:
    st.session_state.photo_key = 0   # changing this key empties the photo box after a photo is sent


def set_pending(text):
    st.session_state.pending = text


def clear_chat():
    st.session_state.messages = []
    st.session_state.count = 0


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
            render_sources(m.get("sources"), expanded=m.get("kind") == "offline")


def to_sources(chunks):
    return [{"title": c.split(":")[0].strip(), "text": c} for c in chunks]


def handle(prompt, photo=None):
    prompt = prompt.strip()
    if not prompt:
        return
    if len(prompt) > MAX_CHARS:
        st.warning(t["too_long"])
        return
    if st.session_state.count >= MAX_REQUESTS:
        st.warning(t["limit"])
        return
    st.session_state.count += 1

    st.session_state.messages.append({"role": "user", "content": prompt, "photo": photo})
    render_user(prompt, photo)

    # 1) emergency gate: plain rules, runs before any AI call
    urgent = check_emergency(prompt)
    if urgent:
        m = {"role": "assistant", "kind": "alert", "content": urgent}
        st.session_state.messages.append(m)
        render_message(m)
        return

    # 2) knowledge base search
    if backend["retrieve"] is None:
        m = {"role": "assistant", "kind": "error", "content": t["kb_offline"]}
        st.session_state.messages.append(m)
        render_message(m)
        return
    try:
        sources = to_sources(backend["retrieve"](prompt))
    except Exception:
        sources = []

    # 3) AI answer (streamed). Without a key we show the knowledge base matches instead.
    if backend["stream"] is None:
        m = {"role": "assistant", "kind": "offline", "content": t["ai_offline"], "sources": sources, "photo_note": bool(photo)}
        st.session_state.messages.append(m)
        render_message(m)
        return

    with st.chat_message("assistant", avatar="🩺"):
        try:
            text = st.write_stream(backend["stream"](prompt))
            kind = "answer"
        except Exception:
            text = t["ai_error"]
            st.markdown(text)
            kind = "error"
        if photo:
            st.caption(t["photo_pending"])
        render_sources(sources)
    st.session_state.messages.append(
        {"role": "assistant", "kind": kind, "content": text, "sources": sources, "photo_note": bool(photo)}
    )


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def pill(label, ok):
    cls, word = ("ok", t["on"]) if ok else ("off", t["off"])
    return f'<div class="pill-row"><span>{label}</span><span class="pill {cls}">{word}</span></div>'


with st.sidebar:
    st.markdown(f"**{t['how_title']}**")
    for i, step in enumerate(t["steps"], 1):
        st.markdown(f'<div class="step"><span class="step-n">{i}</span><span>{step}</span></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown(f"**{t['status']}**")
    kb_ok = backend["retrieve"] is not None
    st.markdown(
        pill(t["safety"], True)
        + pill(f"{t['kb']} ({backend['kb_chunks']} {t['chunks']})", kb_ok)
        + pill(t["ai"], backend["stream"] is not None),
        unsafe_allow_html=True,
    )
    if backend["ai_error"]:
        st.caption(backend["ai_error"][:160])
    st.divider()
    report_slot = st.empty()   # filled at the end of the script, after the newest answer exists
    st.button(t["clear"], on_click=clear_chat)
    st.markdown(f'<p class="side-note">{t["privacy"]}</p>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Main page
# ----------------------------------------------------------------------------
pending = st.session_state.pop("pending", None)
typed = st.chat_input(t["placeholder"])
prompt = typed or pending

top_l, top_r = st.columns([3, 2])
with top_l:
    st.markdown('<div class="brand"><span class="brand-mark">+</span>VitalCheck AI</div>', unsafe_allow_html=True)
with top_r:
    st.radio("Language", ["English", "اردو"], horizontal=True, key="lang_label", label_visibility="collapsed")

st.markdown(f'<div class="notice">{t["notice"]}</div>', unsafe_allow_html=True)

photo_bytes = None
if prepare_image:
    with st.expander(t["photo_label"]):
        upload = st.file_uploader(
            t["photo_help"], type=["jpg", "jpeg", "png", "webp"],
            key=f"photo_{st.session_state.photo_key}", label_visibility="collapsed",
        )
        st.caption(t["photo_help"])
        if upload is not None:
            try:
                photo_bytes = prepare_image(upload.getvalue())
                st.image(photo_bytes, width=160)
                st.success(t["photo_privacy"])
            except ImageError as e:
                st.warning(t[f"photo_{e.code}"])
            except Exception as e:            # anything unexpected: show the reason instead of failing silently
                st.warning(f"{t['photo_error']} ({type(e).__name__}: {str(e)[:120]})")

if not st.session_state.messages and not prompt:
    st.markdown(f'<div class="hero-title">{t["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-sub">{t["sub"]}</p>', unsafe_allow_html=True)
    for i, example in enumerate(t["examples"]):
        st.button(example, key=f"ex{i}", on_click=set_pending, args=(example,))

for m in st.session_state.messages:
    render_message(m)

if prompt:
    handle(prompt, photo_bytes)
    if photo_bytes:                       # empty the photo box, then redraw the page
        st.session_state.photo_key += 1
        st.rerun()

# PDF report button (built last so it includes the message that was just answered)
if build_report and any(m["role"] == "assistant" for m in st.session_state.messages):
    try:
        with report_slot:
            st.download_button(
                t["download"],
                data=build_report(st.session_state.messages, lang),
                file_name="vitalcheck_report.pdf",
                mime="application/pdf",
            )
    except Exception:
        pass
