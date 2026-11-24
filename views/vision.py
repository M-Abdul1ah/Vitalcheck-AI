"""Our Vision page."""
import streamlit as st

from src import ui

lang = ui.current_lang()

TXT = {
    "en": {
        "eyebrow": "Our vision",
        "title": "Your skin. Your language. Clearer next steps.",
        "sub": "Skin concerns can be confusing. We are building practical AI to make general skin-health information easier to understand in Urdu and English — with safety, honesty and people at the centre.",
        "quote": "Good technology does more than give an answer. It helps people understand what to do next — and when to ask a professional.",
        "problem_t": "The problem",
        "problem": "Many people in Pakistan search skin problems online and get confusing or unsafe answers, often only in English. A rash is not always serious, but some skin signs are, and people need to know the difference.",
        "mission_t": "Our mission",
        "mission": "Give simple, safe, general guidance in Urdu and English, using our own trained models, and always send serious or unclear cases to a doctor.",
        "principles_t": "What we stand for",
        "principles": [
            {"icon": "🛡️", "title": "Safety first", "body": "An emergency check runs before anything else, and a second check runs on every answer. No diagnosis, no medicine names, no doses."},
            {"icon": "🗣️", "title": "Urdu and English", "body": "People should be able to describe a problem in the language they think in, including Roman Urdu."},
            {"icon": "🔬", "title": "Honest numbers", "body": "We publish our results and our limits, including where the model is weak. Confidence is calibrated, and low confidence means 'see a doctor'."},
            {"icon": "🎓", "title": "Learning in public", "body": "This is a student project. We build our own models, measure them properly and document what we learn."},
        ],
        "credit_t": "Who is behind it",
        "credit": "The idea, system architecture and workflow were designed by Muhammad Abdullah Nawaz. He brought in teammates to complete it, under the supervision of Mam Saba Ramzan, University of Lahore.",
        "next_t": "Where we are going",
        "next": [
            {"num": 1, "title": "More conditions", "body": "Train on common skin problems like acne and eczema, not only moles."},
            {"num": 2, "title": "Real-world photos", "body": "Test on ordinary phone photos and different skin tones, and report the gap."},
            {"num": 3, "title": "Clearer explanations", "body": "A language model that explains the result in simple Urdu and English, using only checked knowledge."},
        ],
    },
    "ur": {
        "eyebrow": "ہمارا وژن",
        "title": "آپ کی جلد۔ آپ کی زبان۔ بہتر رہنمائی۔",
        "sub": "جلد کے مسائل کے بارے میں درست معلومات سمجھنا مشکل ہو سکتا ہے۔ ہم ایسی عملی اے آئی بنا رہے ہیں جو جلد کی صحت سے متعلق عمومی معلومات اردو اور انگریزی میں آسان بنائے — حفاظت اور سچائی کے ساتھ۔",
        "quote": "اچھی ٹیکنالوجی صرف جواب نہیں دیتی؛ یہ اگلا قدم سمجھنے اور ضرورت پڑنے پر ماہر سے رجوع کرنے میں مدد دیتی ہے۔",
        "problem_t": "مسئلہ",
        "problem": "پاکستان میں بہت سے لوگ جلد کے مسائل آن لائن تلاش کرتے ہیں اور اکثر صرف انگریزی میں الجھے یا غیر محفوظ جواب ملتے ہیں۔ ہر خارش سنگین نہیں ہوتی، مگر کچھ علامات سنگین ہوتی ہیں، اور فرق جاننا ضروری ہے۔",
        "mission_t": "ہمارا مقصد",
        "mission": "اپنے تربیت یافتہ ماڈلز کے ذریعے اردو اور انگریزی میں سادہ، محفوظ اور عمومی رہنمائی دینا، اور سنگین یا غیر واضح کیسز کو ہمیشہ ڈاکٹر کے پاس بھیجنا۔",
        "principles_t": "ہمارے اصول",
        "principles": [
            {"icon": "🛡️", "title": "پہلے حفاظت", "body": "سب سے پہلے ہنگامی جانچ ہوتی ہے اور ہر جواب پر دوسری جانچ۔ نہ تشخیص، نہ دوا کا نام، نہ خوراک۔"},
            {"icon": "🗣️", "title": "اردو اور انگریزی", "body": "لوگ اپنی زبان میں مسئلہ بیان کر سکیں، رومن اردو سمیت۔"},
            {"icon": "🔬", "title": "سچے اعداد", "body": "ہم اپنے نتائج اور حدود دونوں دکھاتے ہیں۔ اعتماد کی شرح کیلیبریٹڈ ہے، اور کم اعتماد کا مطلب ہے 'ڈاکٹر سے ملیں'۔"},
            {"icon": "🎓", "title": "کھلے عام سیکھنا", "body": "یہ طلبہ کا پروجیکٹ ہے۔ ہم اپنے ماڈل بناتے ہیں، انہیں ٹھیک سے ناپتے ہیں اور جو سیکھتے ہیں لکھتے ہیں۔"},
        ],
        "credit_t": "اس کے پیچھے کون ہے",
        "credit": "آئیڈیا، سسٹم آرکیٹیکچر اور ورک فلو محمد عبداللہ نواز نے ڈیزائن کیا۔ انہوں نے اسے مکمل کرنے کے لیے ساتھیوں کو شامل کیا، زیرِ نگرانی میم صبا رمضان، یونیورسٹی آف لاہور۔",
        "next_t": "آگے کا سفر",
        "next": [
            {"num": 1, "title": "مزید بیماریاں", "body": "صرف تل نہیں، کیل مہاسوں اور ایگزیما جیسے عام مسائل پر بھی تربیت۔"},
            {"num": 2, "title": "حقیقی تصاویر", "body": "عام موبائل تصاویر اور مختلف رنگتوں پر جانچ، اور فرق کی رپورٹ۔"},
            {"num": 3, "title": "واضح وضاحت", "body": "ایک لینگویج ماڈل جو صرف جانچے ہوئے علم سے نتیجہ سادہ اردو اور انگریزی میں سمجھائے۔"},
        ],
    },
}
t = TXT[lang]
direction = "rtl" if lang == "ur" else "ltr"

st.markdown("""
<style>
.vc-vision-hero {
  position:relative; isolation:isolate; overflow:hidden; margin:1.35rem 0 1.15rem;
  padding:clamp(1.7rem,4.2vw,3.2rem); border-radius:26px; color:#fff;
  background:radial-gradient(circle at 88% 14%,rgba(255,255,255,.17),transparent 27%),
             linear-gradient(125deg,#083f3b 0%,#0b625a 55%,#21877b 100%);
  box-shadow:0 18px 42px rgba(11,79,74,.15);
}
.vc-vision-hero:after {
  content:""; position:absolute; z-index:-1; width:260px; height:260px; right:-105px; top:-145px;
  border:1px solid rgba(255,255,255,.24); border-radius:50%;
  box-shadow:0 0 0 24px rgba(255,255,255,.045),0 0 0 54px rgba(255,255,255,.03);
}
.vc-vision-kicker { font-size:.75rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; opacity:.78; }
.vc-vision-title { max-width:17ch; margin:.7rem 0 .85rem; font-size:clamp(2.1rem,4.4vw,3.45rem);
  line-height:1.08; letter-spacing:-.035em; font-weight:800; }
.vc-vision-sub { max-width:60ch; margin:0; font-size:1.04rem; line-height:1.75; opacity:.92; }
.vc-vision-quote { display:flex; align-items:center; gap:.8rem; margin:1.1rem 0 1.8rem;
  padding:1rem 1.15rem; border:1px solid #d8e5e0; border-radius:16px;
  background:linear-gradient(110deg,#fff,#f1f7f4); color:#164c46; font-weight:650; line-height:1.7; }
.vc-vision-spark { display:grid; place-items:center; flex:0 0 2.25rem; height:2.25rem;
  border-radius:12px; background:#dceee8; color:#0b625a; font-size:1.1rem; }
.vc-vision-credit { padding:1.15rem 1.3rem; border-left:4px solid #e9b9a8; border-radius:0 14px 14px 0;
  background:#fff; color:#425c56; line-height:1.8; }
.vc-vision-roadmap { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.85rem; margin:.5rem 0 1.2rem; }
.vc-vision-step { padding:1.1rem; background:#fff; border:1px solid #d5e0dc; border-radius:16px;
  transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease; }
.vc-vision-step:hover { transform:translateY(-4px); border-color:#1d7a70; box-shadow:0 12px 24px rgba(22,48,43,.08); }
.vc-vision-number { display:inline-grid; place-items:center; width:2rem; height:2rem; border-radius:10px;
  background:#e3efec; color:#0b4f4a; font-weight:800; margin-bottom:.7rem; }
.vc-vision-step h4 { margin:0 0 .4rem; color:#0b4f4a; font-size:1rem; }
.vc-vision-step p { margin:0; color:#526b65; font-size:.9rem; line-height:1.65; }
[dir="rtl"].vc-vision-hero,[dir="rtl"].vc-vision-quote,[dir="rtl"].vc-vision-credit { direction:rtl; text-align:right; }
[dir="rtl"].vc-vision-quote { flex-direction:row-reverse; }
[dir="rtl"].vc-vision-title { letter-spacing:0; line-height:1.8; max-width: none; }
[dir="rtl"].vc-vision-credit { border-left:0; border-right:4px solid #e9b9a8; border-radius:14px 0 0 14px; }
@media(max-width:700px) { .vc-vision-roadmap { grid-template-columns:1fr; } .vc-vision-title { max-width:none; } }
@media(prefers-reduced-motion:reduce) { .vc-vision-step { transition:none; } .vc-vision-step:hover { transform:none; } }
</style>
""", unsafe_allow_html=True)

st.markdown(
    f'<section class="vc-vision-hero" dir="{direction}">'
    f'<div class="vc-vision-kicker">{ui.esc(t["eyebrow"])}</div>'
    f'<h1 class="vc-vision-title">{ui.esc(t["title"])}</h1>'
    f'<p class="vc-vision-sub">{ui.esc(t["sub"])}</p></section>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="vc-vision-quote" dir="{direction}"><span class="vc-vision-spark">✦</span>'
    f'<span>{ui.esc(t["quote"])}</span></div>',
    unsafe_allow_html=True,
)
ui.grid([{"icon": "❗", "title": t["problem_t"], "body": t["problem"]},
         {"icon": "🎯", "title": t["mission_t"], "body": t["mission"]}])
ui.section(t["principles_t"])
ui.grid(t["principles"])
ui.section(t["credit_t"])
st.markdown(
    f'<div class="vc-vision-credit" dir="{direction}">{ui.esc(t["credit"])}</div>',
    unsafe_allow_html=True,
)
ui.section(t["next_t"])
roadmap = "".join(
    f'<article class="vc-vision-step" dir="{direction}">'
    f'<span class="vc-vision-number">{ui.esc(item["num"])}</span>'
    f'<h4>{ui.esc(item["title"])}</h4><p>{ui.esc(item["body"])}</p></article>'
    for item in t["next"]
)
st.markdown(f'<div class="vc-vision-roadmap">{roadmap}</div>', unsafe_allow_html=True)
