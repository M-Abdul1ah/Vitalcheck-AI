"""Our Vision page."""
import streamlit as st

from src import ui

lang = ui.current_lang()

TXT = {
    "en": {
        "eyebrow": "Our vision",
        "title": "Learn by building. Help people while we do it.",
        "sub": "VitalCheck AI started as one idea: build real AI models, and make them useful for people who search skin problems online and get confusing answers.",
        "quote": "We learn AI best by building models that people can actually use, and by being honest about what they cannot do.",
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
        "title": "بنا کر سیکھیں۔ سیکھتے ہوئے لوگوں کی مدد کریں۔",
        "sub": "VitalCheck AI ایک خیال سے شروع ہوا: حقیقی اے آئی ماڈلز بنانا اور انہیں ان لوگوں کے لیے مفید بنانا جو جلد کے مسائل آن لائن تلاش کرتے ہیں اور الجھے ہوئے جواب پاتے ہیں۔",
        "quote": "ہم اے آئی بہترین طریقے سے ایسے ماڈل بنا کر سیکھتے ہیں جو لوگوں کے کام آئیں، اور یہ بتا کر کہ وہ کیا نہیں کر سکتے۔",
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

ui.hero(t["eyebrow"], t["title"], t["sub"])
st.markdown(f'<div class="quote">{ui.esc(t["quote"])}</div>', unsafe_allow_html=True)
ui.grid([{"icon": "❗", "title": t["problem_t"], "body": t["problem"]},
         {"icon": "🎯", "title": t["mission_t"], "body": t["mission"]}])
ui.section(t["principles_t"])
ui.grid(t["principles"])
ui.section(t["credit_t"])
ui.grid([{"icon": "💡", "title": "Muhammad Abdullah Nawaz", "body": t["credit"]}])
ui.section(t["next_t"])
ui.grid(t["next"])
