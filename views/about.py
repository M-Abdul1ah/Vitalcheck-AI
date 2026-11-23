"""About page: how it works, our own models, safety and the tech stack."""
import streamlit as st

from src import ui

lang = ui.current_lang()

TXT = {
    "en": {
        "eyebrow": "About", "title": "How VitalCheck AI works",
        "sub": "A safety shell around two models we trained ourselves, and a knowledge base we wrote and sourced.",
        "flow_t": "What happens to every message",
        "flow": [
            {"num": 1, "title": "Emergency check", "body": "Fixed rules in English, Urdu and Roman Urdu look for red flags first. A match stops everything and shows the Rescue 1122 warning."},
            {"num": 2, "title": "Small talk and vague check", "body": "A greeting gets a friendly reply. A very short message gets a request for more details."},
            {"num": 3, "title": "Photo analysis", "body": "If you add a photo, DermaVC-Net returns the top 3 possible matches with calibrated confidence, a melanoma warning rule and a heatmap."},
            {"num": 4, "title": "Symptom analysis", "body": "DermaVC-Text reads your description (English, Urdu, Roman Urdu) and returns possible conditions with confidence."},
            {"num": 5, "title": "Knowledge base", "body": "Matching entries are shown with their sources, so you can check them."},
            {"num": 6, "title": "Output check", "body": "Rules block medicine names, doses and definite-diagnosis wording, and always add a doctor reminder."},
        ],
        "models_t": "Our own models",
        "models": [
            {"icon": "📷", "title": "DermaVC-Net (photo)", "body": "EfficientNet-B0 fine-tuned on HAM10000. 7 lesion classes. Test accuracy 0.821, macro F1 0.742, AUC 0.968 (mean of 3 seeds)."},
            {"icon": "⌨️", "title": "DermaVC-Text (symptoms)", "body": "Text classifier for 28 labels (24 skin conditions and 4 non-clinical) in English, Urdu and Roman Urdu."},
        ],
        "safety_t": "Safety and privacy",
        "safety": [
            {"icon": "🚨", "title": "No diagnosis", "body": "We show possible matches only, and always advise a doctor for serious or unclear cases."},
            {"icon": "🔒", "title": "Photos not stored", "body": "Photos are cleaned, used in memory and never written to disk."},
            {"icon": "⏱️", "title": "Limits", "body": "Message length and request rate are limited to protect the service."},
        ],
        "status_t": "Project status",
        "status": [
            {"icon": "✅", "title": "Built", "body": "Chat in English and Urdu, emergency gate, DermaVC-Net, DermaVC-Text, knowledge base with sources, workflow tab, PDF report."},
            {"icon": "🛠️", "title": "In progress", "body": "LLM explainer with a safe fallback, follow-up questions, a cleaner pipeline module."},
            {"icon": "🗺️", "title": "Planned", "body": "Phone-photo and skin-tone tests, more conditions, deployment on Hugging Face Spaces."},
        ],
        "stack_t": "Tech stack (all free)",
    },
    "ur": {
        "eyebrow": "تعارف", "title": "VitalCheck AI کیسے کام کرتا ہے",
        "sub": "دو ایسے ماڈلز کے گرد حفاظتی خول جو ہم نے خود تربیت دیے، اور ہمارا لکھا ہوا حوالہ جاتی علمی ذخیرہ۔",
        "flow_t": "ہر پیغام کے ساتھ کیا ہوتا ہے",
        "flow": [
            {"num": 1, "title": "ہنگامی جانچ", "body": "انگریزی، اردو اور رومن اردو میں طے شدہ اصول سب سے پہلے خطرے کی علامات دیکھتے ہیں۔ ملنے پر سب رک جاتا ہے اور Rescue 1122 کا انتباہ آتا ہے۔"},
            {"num": 2, "title": "عمومی گفتگو اور مبہم پیغام کی جانچ", "body": "سلام کا دوستانہ جواب ملتا ہے۔ بہت مختصر پیغام پر مزید تفصیل مانگی جاتی ہے۔"},
            {"num": 3, "title": "تصویر کا تجزیہ", "body": "تصویر دیں تو DermaVC-Net تین ممکنہ مماثلتیں، کیلیبریٹڈ اعتماد، میلانوما انتباہی اصول اور ہیٹ میپ دیتا ہے۔"},
            {"num": 4, "title": "علامات کا جائزہ", "body": "DermaVC-Text آپ کی تحریر (انگریزی، اردو، رومن اردو) پڑھ کر ممکنہ امراض اور اعتماد بتاتا ہے۔"},
            {"num": 5, "title": "علمی ذخیرہ", "body": "ملتی جلتی معلومات ذرائع کے ساتھ دکھائی جاتی ہیں تاکہ آپ خود جانچ سکیں۔"},
            {"num": 6, "title": "آؤٹ پٹ جانچ", "body": "اصول دوا کے نام، خوراک اور قطعی تشخیص کے الفاظ روکتے ہیں اور ڈاکٹر کی یاد دہانی ہمیشہ شامل کرتے ہیں۔"},
        ],
        "models_t": "ہمارے اپنے ماڈلز",
        "models": [
            {"icon": "📷", "title": "DermaVC-Net (تصویر)", "body": "HAM10000 پر فائن ٹیون کیا گیا EfficientNet-B0۔ 7 اقسام۔ ٹیسٹ درستگی 0.821، میکرو F1 0.742، AUC 0.968 (3 سیڈز کا اوسط)۔"},
            {"icon": "⌨️", "title": "DermaVC-Text (علامات)", "body": "28 لیبلز (24 جلدی امراض اور 4 غیر طبی) کے لیے ٹیکسٹ کلاسیفائر، انگریزی، اردو اور رومن اردو میں۔"},
        ],
        "safety_t": "حفاظت اور پرائیویسی",
        "safety": [
            {"icon": "🚨", "title": "تشخیص نہیں", "body": "ہم صرف ممکنہ مماثلتیں دکھاتے ہیں، اور سنگین یا غیر واضح کیس میں ہمیشہ ڈاکٹر کا مشورہ دیتے ہیں۔"},
            {"icon": "🔒", "title": "تصاویر محفوظ نہیں", "body": "تصاویر صاف کی جاتی ہیں، میموری میں استعمال ہوتی ہیں اور ڈسک پر نہیں لکھی جاتیں۔"},
            {"icon": "⏱️", "title": "حدود", "body": "سروس کی حفاظت کے لیے پیغام کی لمبائی اور درخواستوں کی رفتار محدود ہے۔"},
        ],
        "status_t": "پروجیکٹ کی صورتحال",
        "status": [
            {"icon": "✅", "title": "مکمل", "body": "اردو اور انگریزی چیٹ، ہنگامی گیٹ، DermaVC-Net، DermaVC-Text، ذرائع کے ساتھ علمی ذخیرہ، ورک فلو ٹیب، PDF رپورٹ۔"},
            {"icon": "🛠️", "title": "جاری", "body": "محفوظ فال بیک کے ساتھ LLM وضاحت کار، فالو اپ سوالات، صاف پائپ لائن ماڈیول۔"},
            {"icon": "🗺️", "title": "منصوبہ", "body": "موبائل تصاویر اور رنگت کی جانچ، مزید امراض، Hugging Face Spaces پر ڈیپلائے۔"},
        ],
        "stack_t": "ٹیکنالوجی (سب مفت)",
    },
}
t = TXT[lang]

ui.hero(t["eyebrow"], t["title"], t["sub"])
ui.section(t["flow_t"])
ui.grid(t["flow"])
ui.section(t["models_t"])
ui.grid(t["models"])
ui.section(t["safety_t"])
ui.grid(t["safety"])
ui.section(t["status_t"])
ui.grid(t["status"])
ui.section(t["stack_t"])
ui.chips(["Streamlit", "PyTorch", "EfficientNet-B0", "scikit-learn", "ChromaDB", "sentence-transformers",
          "Pillow", "fpdf2", "pytest", "GitHub Actions"])
