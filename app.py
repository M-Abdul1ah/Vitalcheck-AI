"""
VitalCheck AI - Streamlit front end.

Every message goes through: input checks -> emergency gate -> knowledge search -> AI answer (streamed).
The safety gate and knowledge search work without a Groq key, so the whole UI can be tested in the browser.
"""
import html
import time

import streamlit as st

from src.safety_check import check_emergency

try:
    from src.trace import make_trace, ms_since, skipped
    from src.trace import step as trace_step
    from src.output_check import apply_output_check
    from src.workflow_ui import render_trace
except Exception:
    make_trace = ms_since = skipped = trace_step = apply_output_check = render_trace = None

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
    backend = {"retrieve": None, "retrieve_scored": None, "stream": None, "kb_chunks": 0, "kb_error": None, "ai_error": None}
    try:
        from src.embed_store import build, get_collection
        if get_collection().count() == 0:   # first start on a fresh server: chroma_db is not in Git
            build()
        backend["kb_chunks"] = get_collection().count()
        from src.retriever import retrieve
        backend["retrieve"] = retrieve
        try:
            from src.retriever import retrieve_with_scores
            backend["retrieve_scored"] = retrieve_with_scores
        except Exception:
            pass
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
if "last_trace" not in st.session_state:
    st.session_state.last_trace = None   # most recent message's step-by-step record, for the Workflow tab


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

    tracing = trace_step is not None
    steps = [] if tracing else None
    urdu = any("\u0600" <= c <= "\u06FF" for c in prompt)

    if tracing:
        steps.append(trace_step(
            "user", "done", sub="text + photo" if photo else "sent",
            inn="Chat box",
            out=f'"{prompt[:60]}" - language: {"Urdu" if urdu else "English"}, {len(prompt)} characters',
            log=f"Message received ({'Urdu' if urdu else 'English'}, {len(prompt)} characters).",
        ))
        steps[-1]["edge"] = "user-safety"

    # 1) emergency gate: plain rules, runs before any AI call
    t0 = time.perf_counter()
    urgent = check_emergency(prompt)
    if tracing:
        ms = ms_since(t0)
        if urgent:
            steps.append(trace_step("safety", "alert", ms=ms, inn="Message text",
                                     out="Red flag matched. Decision: stop and escalate.",
                                     log="Red flag found. Pipeline stopped."))
            steps[-1]["edge"] = "safety-resolution"
        else:
            steps.append(trace_step("safety", "done", ms=ms, inn="Message text",
                                     out="No red flags found. Decision: continue.",
                                     log="No red flags found. Message passed on."))
            steps[-1]["edge"] = "safety-photo"

    if urgent:
        if tracing:
            steps.append(skipped(["photo", "retriever", "ai", "output"],
                                  "Photo prep, retriever, AI and output check are not needed."))
            steps.append(trace_step("resolution", "alert", sub="Escalated", inn="Result from the safety gate",
                                     out="ESCALATED_EMERGENCY - Rescue 1122 warning shown, AI not called",
                                     log="Emergency warning shown with Rescue 1122. The AI was never called."))
            st.session_state.last_trace = make_trace(prompt, steps, "danger", urgent)
        m = {"role": "assistant", "kind": "alert", "content": urgent}
        st.session_state.messages.append(m)
        render_message(m)
        return

    # 2) photo prep already happened before handle() was called (see the uploader below)
    if tracing:
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
        if tracing:
            steps.append(trace_step("retriever", "warn", sub="offline", inn=f"Search text: {prompt[:50]}",
                                     out="Knowledge base unavailable.", log="Knowledge base not available."))
            steps.append(skipped(["ai", "output"], "AI and output check need the knowledge base."))
            steps.append(trace_step("resolution", "warn", sub="Unavailable", inn="Results from all agents",
                                     out="KB_UNAVAILABLE", log="No answer given: knowledge base offline."))
            st.session_state.last_trace = make_trace(prompt, steps, "warning", t["kb_offline"])
        m = {"role": "assistant", "kind": "error", "content": t["kb_offline"]}
        st.session_state.messages.append(m)
        render_message(m)
        return

    t0 = time.perf_counter()
    try:
        if backend["retrieve_scored"]:
            scored = backend["retrieve_scored"](prompt)
            sources = to_sources([doc for doc, _ in scored])
            matches = [[s["title"], score] for s, (_, score) in zip(sources, scored)]
        else:
            sources = to_sources(backend["retrieve"](prompt))
            matches = None
    except Exception:
        sources, matches = [], None
    if tracing:
        ms = ms_since(t0)
        best = ", ".join(s["title"] for s in sources[:3]) if sources else "none"
        step_kwargs = {"matches": matches} if matches else {"out": "No matches found."}
        steps.append(trace_step("retriever", "done", ms=ms, inn=f"Search text: {prompt[:60]}",
                                 log=f"{len(sources)} matches found. Best: {best}.", **step_kwargs))
        steps[-1]["edge"] = "retriever-ai"

    # 4) AI answer (streamed). Without a key we show the knowledge base matches instead.
    if backend["stream"] is None:
        if tracing:
            steps.append(trace_step("ai", "warn", sub="offline", inn=f"Message + {len(sources)} matches",
                                     out="AI model not connected. Falling back to the matches.",
                                     log="AI model not connected. Falling back to the matches."))
            steps[-1]["edge"] = "ai-output"
            steps.append(trace_step("output", "skip", sub="nothing", inn="No AI answer",
                                     out="Nothing to check.", log="Nothing to check without an AI answer."))
            steps[-1]["edge"] = "output-resolution"
            steps.append(trace_step("resolution", "warn", sub="Matches only", inn="Results from all agents",
                                     out="KB_ONLY_FALLBACK", log="Knowledge base matches shown without an AI answer."))
            st.session_state.last_trace = make_trace(prompt, steps, "warning", t["ai_offline"])
        m = {"role": "assistant", "kind": "offline", "content": t["ai_offline"], "sources": sources,
             "photo_note": bool(photo)}
        st.session_state.messages.append(m)
        render_message(m)
        return

    with st.chat_message("assistant", avatar="\U0001fa7a"):
        t0 = time.perf_counter()
        try:
            text = st.write_stream(backend["stream"](prompt))
            ai_ms = ms_since(t0)
            if tracing:
                steps.append(trace_step("ai", "done", ms=ai_ms, inn=f"Message + {len(sources)} matches",
                                         stream=text, log="Llama 3.3 wrote an answer using the matches."))
                steps[-1]["edge"] = "ai-output"

            if apply_output_check:
                t0 = time.perf_counter()
                checked_text, report = apply_output_check(text)
                oc_ms = ms_since(t0)
                blocked = report["action"] == "blocked"
                text = checked_text
                kind = "answer"
                if tracing:
                    if blocked:
                        out = (f"Medicine names: {len(report['medicine'])}. "
                               f"Diagnosis phrases: {len(report['diagnosis'])}. Answer blocked.")
                        log = "Answer blocked: contained medicine or diagnosis wording."
                        out_state, res_state, res_sub = "warn", "warn", "Blocked"
                        tone, end = "warning", "Resolution: the answer was held back by the output check; a doctor visit is advised."
                    else:
                        out = f"Medicine names: 0. Diagnosis phrases: 0. Doctor advice: {'present' if report['doctor'] else 'added'}."
                        log = "No medicine names or diagnosis wording found."
                        out_state, res_state, res_sub = "done", "done", "Answered"
                        tone, end = "success", "Resolution: answered from the knowledge base, with a doctor visit advised."
                    steps.append(trace_step("output", out_state, ms=oc_ms, inn=f"AI answer, {report['words']} words",
                                             out=out, log=log))
                    steps[-1]["edge"] = "output-resolution"
                    steps.append(trace_step("resolution", res_state, sub=res_sub, inn="Results from all agents",
                                             out=f"ANSWERED_FROM_KB · {res_sub.upper()}", log=log))
                    st.session_state.last_trace = make_trace(prompt, steps, tone, end)
            else:
                kind = "answer"
                if tracing:
                    steps.append(trace_step("resolution", "done", sub="Answered", inn="Results from all agents",
                                             out="ANSWERED_FROM_KB", log="Answered from the knowledge base."))
                    st.session_state.last_trace = make_trace(
                        prompt, steps, "success",
                        "Resolution: answered from the knowledge base, with a doctor visit advised.",
                    )
        except Exception:
            text = t["ai_error"]
            st.markdown(text)
            kind = "error"
            if tracing:
                steps.append(trace_step("ai", "warn", sub="error", inn=f"Message + {len(sources)} matches",
                                         out="The AI call failed.", log="The AI call failed."))
                steps.append(trace_step("resolution", "warn", sub="Error", inn="Results from all agents",
                                         out="AI_ERROR", log="No answer: the AI call failed."))
                st.session_state.last_trace = make_trace(prompt, steps, "warning", t["ai_error"])
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

if render_trace:
    chat_tab, workflow_tab = st.tabs([t["chat_tab"], t["workflow_tab"]])
else:
    chat_tab, workflow_tab = st.container(), None
chat_tab.__enter__()

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

chat_tab.__exit__(None, None, None)
if workflow_tab is not None:
    with workflow_tab:
        render_trace(st.session_state.last_trace, lang)

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
