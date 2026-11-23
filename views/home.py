"""Home page: the chat (text + photo), with the Workflow tab. Routed from app.py."""
import html
import os
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
from src import skin_model
from src import text_model
from src.workflow_ui import render_trace
from src import ui


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
        "steps": ["Emergency check", "DermaVC-Text symptom analysis", "Knowledge base guidance"],
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
        "photo_pending": "Photo analysis is not available on this server, so this answer uses your text only.",
        "vision_title": "Photo analysis (our own model, DermaVC-Net)",
        "vision_possible": "Possible matches, not a diagnosis:",
        "vision_note": "This model was trained on close-up photos of 7 types of skin lesions, mostly moles. It cannot recognise rashes, eczema or acne, and ordinary phone photos are harder for it.",
        "vision_unclear": "The photo is unclear for this model, so no match is shown as reliable. If you are worried, please see a doctor.",
        "vision_mel": "Warning: the photo analysis found a possible melanoma warning sign ({p}% chance). Please see a doctor soon.",
        "vision_heatmap": "Where the model looked (Grad-CAM)",
        "text_model_title": "Symptom analysis (our own model, DermaVC-Text)",
        "text_model_possible": "Possible matching skin conditions (not a diagnosis):",
        "text_model_note": "This model analyzes clinical descriptions in English, Roman Urdu, and Urdu across 24 common skin conditions.",
        "text_model_unclear": "The description is not detailed enough for high confidence. If symptoms persist, please consult a physician.",
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
        "steps": ["ہنگامی علامات کی جانچ", "DermaVC-Text علامات کا جائزہ", "علمی ذخیرے سے رہنمائی"],
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
        "photo_pending": "اس سرور پر تصویر کا تجزیہ دستیاب نہیں، اس لیے یہ جواب صرف آپ کی تحریر پر مبنی ہے۔",
        "vision_title": "تصویر کا تجزیہ (ہمارا اپنا ماڈل، DermaVC-Net)",
        "vision_possible": "ممکنہ مماثلتیں، تشخیص نہیں:",
        "vision_note": "یہ ماڈل جلد کے 7 قسم کے نشانوں کی قریب سے لی گئی تصاویر پر سیکھا گیا ہے، زیادہ تر تل۔ یہ خارش، ایکزیما یا کیل مہاسوں کو نہیں پہچان سکتا، اور عام موبائل تصاویر اس کے لیے مشکل ہیں۔",
        "vision_unclear": "اس ماڈل کے لیے تصویر واضح نہیں، اس لیے کوئی نتیجہ قابلِ بھروسا نہیں۔ فکر ہو تو ڈاکٹر سے ملیں۔",
        "vision_mel": "انتباہ: تصویر کے تجزیے میں میلانوما کی ممکنہ علامت ملی ({p}% امکان)۔ براہ کرم جلد ڈاکٹر سے ملیں۔",
        "vision_heatmap": "ماڈل نے کہاں دیکھا (Grad-CAM)",
        "text_model_title": "علامات کا جائزہ (ہمارا ماڈل، DermaVC-Text)",
        "text_model_possible": "ممکنہ جلدی امراض (یہ حتمی تشخیص نہیں ہے):",
        "text_model_note": "یہ ماڈل انگریزی، رومن اردو اور اردو میں لکھی گئی علامات کی بنیاد پر 24 جلدی امراض کی درجہ بندی کرتا ہے۔",
        "text_model_unclear": "علامات کی تفصیل کم ہونے کی وجہ سے حتمی مماثلت واضح نہیں۔ ضرورت پڑنے پر ڈاکٹر سے رجوع کریں۔",
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
        "alert_title": "This may be an emergency",
        "call": "Call Rescue 1122",
        "top_label": "Closest match",
        "others_label": "Other possibilities",
        "conf": "confidence",
        "features": [
            {"icon": "⌨️", "title": "Describe it", "body": "Write your symptoms in English, Urdu or Roman Urdu."},
            {"icon": "📷", "title": "Add a photo", "body": "Our own model suggests possible matches. Photos are never stored."},
            {"icon": "🩺", "title": "Know when to see a doctor", "body": "Sourced guidance, never a diagnosis."},
        ],
    },
    "ur": {
        "hint": "تصویر شامل کرنے کے لیے چیٹ باکس کا + بٹن استعمال کریں۔",
        "chips": ["اردو اور انگریزی", "ہنگامی جانچ", "تصاویر محفوظ نہیں کی جاتیں"],
        "need_text": "تصویر کے ساتھ اپنی علامات کی مختصر تفصیل بھی لکھیں۔",
        "alert_title": "یہ ہنگامی صورتحال ہو سکتی ہے",
        "call": "Rescue 1122 پر کال کریں",
        "top_label": "سب سے قریبی مماثلت",
        "others_label": "دیگر امکانات",
        "conf": "اعتماد",
        "features": [
            {"icon": "⌨️", "title": "بیان کریں", "body": "اپنی علامات انگریزی، اردو یا رومن اردو میں لکھیں۔"},
            {"icon": "📷", "title": "تصویر شامل کریں", "body": "ہمارا اپنا ماڈل ممکنہ مماثلتیں بتاتا ہے۔ تصاویر کبھی محفوظ نہیں ہوتیں۔"},
            {"icon": "🩺", "title": "جانیں کب ڈاکٹر سے ملیں", "body": "حوالہ جاتی رہنمائی، تشخیص نہیں۔"},
        ],
    },
}

lang_label = st.session_state.get("lang_label", "English")
lang = "ur" if lang_label == "اردو" else "en"
t = {**TEXT[lang], **EXTRA[lang]}

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


@st.cache_resource(show_spinner="Loading the photo model...")
def load_vision():
    """DermaVC-Net, loaded once and only when the first photo arrives. Returns (model or None, reason)."""
    if not skin_model.is_available():
        return None, skin_model.why_unavailable()
    try:
        return skin_model.SkinModel(), ""
    except skin_model.SkinModelError as e:
        return None, str(e)


@st.cache_resource(show_spinner="Loading the symptom classifier...")
def load_text_classifier():
    """DermaVC-Text, loaded once. Returns (model or None, reason)."""
    if not text_model.is_available():
        return None, text_model.why_unavailable()
    try:
        return text_model.TextModel(), ""
    except text_model.TextModelError as e:
        return None, str(e)

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


def render_vision(v):
    """Photo analysis card: top-3 possible matches, an honest note and the Grad-CAM heatmap."""
    st.markdown(f"**{t['vision_title']}**")
    if not v.get("confident"):
        st.caption(t["vision_unclear"])
    else:
        st.caption(t["vision_possible"])
        key = "label_ur" if lang == "ur" else "label_en"
        for item in v["top"]:
            st.progress(item["probability"], text=f"{item[key]}: {round(item['probability'] * 100)}%")
    if v.get("heatmap_png"):
        with st.expander(t["vision_heatmap"]):
            st.image(v["heatmap_png"])
    st.caption(t["vision_note"])


def confidence_level(p):
    return "hi" if p >= 0.75 else "mid" if p >= 0.5 else "lo"


def render_text_pred(tp):
    """Symptom analysis card: closest match with a confidence badge, then the other possibilities."""
    if not tp.get("confident"):
        st.markdown(f"**{t['text_model_title']}**")
        st.caption(t["text_model_unclear"])
        st.caption(t["text_model_note"])
        return
    name_key = "name_ur" if lang == "ur" else "name"
    top, others = tp["top"][0], tp["top"][1:]
    pct = round(top["probability"] * 100)
    st.markdown(
        f'<div class="topmatch"><div class="lbl">{html.escape(t["top_label"])}</div>'
        f'<div class="name">{html.escape(top[name_key])}</div>'
        f'<span class="badge {confidence_level(top["probability"])}">{pct}% {html.escape(t["conf"])}</span>'
        f'<div class="bar"><span style="width:{pct}%"></span></div></div>', unsafe_allow_html=True)
    if others:
        rows = "".join(
            f'<div class="row"><span class="t">{html.escape(o[name_key])}</span>'
            f'<span class="b"><span style="width:{round(o["probability"] * 100)}%"></span></span>'
            f'<span class="p">{round(o["probability"] * 100)}%</span></div>' for o in others)
        st.markdown(f'<div class="others"><div class="lbl" style="font-size:.74rem;color:var(--muted)">'
                    f'{html.escape(t["others_label"])}</div>{rows}</div>', unsafe_allow_html=True)
    st.caption(f"{t['text_model_title']}. {t['text_model_possible']}")


def render_message(m):
    if m["role"] == "user":
        render_user(m["content"], m.get("photo"))
    elif m.get("kind") == "alert":
        st.markdown(
            f'<div class="alert"><div class="ttl">🚨 {html.escape(t["alert_title"])}</div>{html.escape(m["content"])}'
            f'<br><a class="call" href="tel:1122">{html.escape(t["call"])}</a></div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="🩺"):
            if m.get("text_pred"):
                render_text_pred(m["text_pred"])
            st.markdown(m["content"])
            if m.get("vision"):
                render_vision(m["vision"])
            elif m.get("photo_note"):
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
    if is_too_vague(prompt) and not photo:
        steps[-1]["edge"] = "safety-resolution"
        steps.append(skipped(["photo", "retriever", "ai", "output"], "The message is too vague to search."))
        steps.append(trace_step("resolution", "warn", sub="Need details", inn="Message text",
                                out="NEEDS_DETAILS - asked the user for more information",
                                log="Message too vague: asked for more details. Knowledge base not searched."))
        finish(prompt, steps, "warning", t["need_details"],
               {"role": "assistant", "kind": "info", "content": t["need_details"]})
        return

    # 2) photo analysis: our own model DermaVC-Net reads the photo that was cleaned earlier
    vision, vision_error = None, ""
    if photo:
        t0 = time.perf_counter()
        vmodel, vision_error = load_vision()
        if vmodel is not None:
            try:
                vision = vmodel.predict(photo)
            except skin_model.SkinModelError as e:
                vision_error = str(e)
        if vision:
            top = vision["top"][0]
            verdict = "confident" if vision["confident"] else f"unclear (top below {round(vision['min_confidence'] * 100)}%)"
            out = (f"Top match: {top['code']} {round(top['probability'] * 100)}%, {verdict}. "
                   f"Melanoma probability {round(vision['mel_probability'] * 100)}%"
                   f"{' (warning shown)' if vision['melanoma_flag'] else ''}.")
            steps.append(trace_step("photo", "done" if vision["confident"] else "warn", ms=ms_since(t0),
                                    inn=f"Photo, {len(photo)} bytes after cleanup", out=out,
                                    log=f"{vision['model']}: {out}"))
        else:
            steps.append(trace_step("photo", "warn", sub="unavailable", ms=ms_since(t0),
                                    inn=f"Photo, {len(photo)} bytes after cleanup",
                                    out="Photo model not available. Text only.",
                                    log=f"Photo model not used: {vision_error[:200]}"))
    else:
        steps.append(trace_step("photo", "skip", sub="no photo", inn="No photo attached",
                                out="Step skipped.", log="No photo attached, so this step is skipped."))
    steps[-1]["edge"] = "photo-retriever"

    # 3) symptom classification (DermaVC-Text) & knowledge base search
    t0 = time.perf_counter()
    text_pred = None
    tmodel, terror = load_text_classifier()
    if tmodel is not None:
        try:
            text_pred = tmodel.predict(prompt)
        except Exception:
            text_pred = None

    sources, matches = [], None
    if text_pred and text_pred["is_clinical"]:
        from pathlib import Path
        kb_file = Path("data/dermatology_kb.txt")
        if kb_file.exists():
            blocks = [b.strip() for b in kb_file.read_text(encoding="utf-8").split("\n\n") if b.strip()]
            kb_map = {b.split(":", 1)[0].strip().lower(): b for b in blocks if ":" in b}
            for item in text_pred["top"]:
                kt = item.get("kb_title")
                if kt and kt.lower() in kb_map:
                    full_text = kb_map[kt.lower()]
                    sources.append({"title": full_text.split(":", 1)[0].strip(), "text": full_text})
            matches = [[s["title"], item["probability"]] for s, item in zip(sources, text_pred["top"])]

    # Fallback to vector search if text model produced no clinical matches
    if not sources and backend["retrieve"] is not None:
        try:
            scored = backend["retrieve_scored"](prompt)
            sources = to_sources([doc for doc, _ in scored])
            matches = [[s["title"], score] for s, (_, score) in zip(sources, scored)]
            if not scored or max(score for _, score in scored) < MIN_MATCH_SCORE:
                sources = []          # nothing relevant: ask the user to describe the problem instead
        except Exception:
            sources, matches = [], None
    elif not sources and backend["retrieve"] is None:
        steps.append(trace_step("retriever", "warn", sub="offline", inn=f"Search text: {prompt[:50]}",
                                out="Knowledge base unavailable.", log="Knowledge base not available."))
        steps.append(skipped(["ai", "output"], "Answer and output check need the knowledge base."))
        steps.append(trace_step("resolution", "warn", sub="Unavailable", inn="Results from all agents",
                                out="KB_UNAVAILABLE", log="No answer given: knowledge base offline."))
        finish(prompt, steps, "warning", t["kb_offline"], {"role": "assistant", "kind": "error", "content": t["kb_offline"]})
        return

    ms = ms_since(t0)
    best = ", ".join(s["title"] for s in sources[:3]) if sources else "none"
    model_tag = f"DermaVC-Text ({text_pred['top_name']})" if (text_pred and text_pred["is_clinical"]) else "Vector search"
    step_kwargs = {"matches": matches} if (matches and sources) else {
        "out": f"No relevant match (best score below {MIN_MATCH_SCORE}). Asking the user to describe the problem."}
    steps.append(trace_step("retriever", "done" if sources else "warn", ms=ms, inn=f"Search text: {prompt[:60]}",
                            log=f"{len(sources)} matches found via {model_tag}. Best: {best}.", **step_kwargs))
    steps[-1]["edge"] = "retriever-ai"

    # a mole-type photo result adds the ABCDE mole advice from the knowledge base
    if vision and vision["mole_advice"] and backend["retrieve"] is not None:
        try:
            extra = [c for c in backend["retrieve"]("Melanoma warning signs ABCDE mole") if c.startswith("Melanoma")]
            have = {s["title"] for s in sources}
            sources += [s for s in to_sources(extra) if s["title"] not in have]
        except Exception:
            pass

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
    if vision and vision["melanoma_flag"]:
        text = t["vision_mel"].format(p=round(vision["mel_probability"] * 100)) + "\n\n" + text
    msg = {
        "role": "assistant", "kind": "answer", "content": text, "sources": sources,
        "photo_note": bool(photo) and not vision, "vision": vision
    }
    if text_pred and text_pred["is_clinical"]:
        msg["text_pred"] = text_pred
    finish(prompt, steps, tone, end, msg)


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
    text_ok = text_model.is_available()
    st.markdown(
        pill(t["safety"], True)
        + pill("DermaVC-Text (28 classes)", text_ok)
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

chat_tab, workflow_tab = st.tabs([t["chat_tab"], t["workflow_tab"]])

with chat_tab:
    st.markdown(f'<div class="notice">{t["notice"]}</div>', unsafe_allow_html=True)

    if not st.session_state.messages and not prompt:
        st.markdown(f'<div class="hero-title">{t["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="hero-sub">{t["sub"]}</p>', unsafe_allow_html=True)
        chips = "".join(f'<span class="chip">{c}</span>' for c in t["chips"])
        st.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)
        ui.grid(t["features"])
        st.markdown(f'<p class="hint">{t["hint"]}</p>', unsafe_allow_html=True)
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
