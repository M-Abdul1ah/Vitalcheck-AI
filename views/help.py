"""Help page: common questions and answers."""
import streamlit as st

from src import ui

lang = ui.current_lang()

TXT = {
    "en": {"eyebrow": "Help", "title": "Questions people ask", "sub": "Short, honest answers.", "qa": [
        ("Is VitalCheck AI a doctor?", "No. It gives general information and possible matches, never a diagnosis or a prescription. If you are worried, see a doctor."),
        ("Which languages can I use?", "English, Urdu script and Roman Urdu (Urdu typed in English letters). The page itself switches between English and Urdu."),
        ("Is my photo saved?", "No. The photo is cleaned (metadata removed, resized), used in memory for the analysis and never written to disk. Please avoid faces and ID documents."),
        ("What can the photo model recognise?", "DermaVC-Net knows 7 types of skin lesions, mostly moles, because it was trained on dermoscopy images. It cannot recognise rashes, eczema or acne, and ordinary phone photos are harder for it."),
        ("What does the confidence number mean?", "It is how sure the model is, adjusted (calibrated) so that 80% should be right about 8 times in 10. Below 50% for a photo, the app says it is unclear and advises a doctor."),
        ("What happens in an emergency?", f"If your message has a red-flag phrase (for example trouble breathing or chest pain), the app stops and shows a warning to call Rescue 1122."),
        ("Why does it sometimes ask for more details?", "A very short message like 'help' cannot be matched to a skin problem. Tell us where it is, how long you have had it, and whether it itches or hurts."),
        ("Who built it?", "Muhammad Abdullah Nawaz (idea and lead) with three teammates, supervised by Mam Saba Ramzan at the University of Lahore."),
    ]},
    "ur": {"eyebrow": "سوالات", "title": "لوگ کیا پوچھتے ہیں", "sub": "مختصر اور سچے جواب۔", "qa": [
        ("کیا VitalCheck AI ڈاکٹر ہے؟", "نہیں۔ یہ عمومی معلومات اور ممکنہ مماثلتیں دیتا ہے، تشخیص یا نسخہ نہیں۔ فکر ہو تو ڈاکٹر سے ملیں۔"),
        ("میں کون سی زبانیں استعمال کر سکتا ہوں؟", "انگریزی، اردو رسم الخط اور رومن اردو۔ صفحہ خود بھی انگریزی اور اردو میں بدل جاتا ہے۔"),
        ("کیا میری تصویر محفوظ کی جاتی ہے؟", "نہیں۔ تصویر صاف کی جاتی ہے (میٹا ڈیٹا ہٹایا جاتا ہے، سائز چھوٹا ہوتا ہے)، تجزیے کے لیے صرف میموری میں استعمال ہوتی ہے اور ڈسک پر نہیں لکھی جاتی۔ چہرے اور شناختی کاغذات سے پرہیز کریں۔"),
        ("تصویر والا ماڈل کیا پہچان سکتا ہے؟", "DermaVC-Net جلد کے 7 قسم کے نشانات جانتا ہے، زیادہ تر تل، کیونکہ اسے ڈرموسکوپی تصاویر پر تربیت دی گئی۔ یہ خارش، ایگزیما یا کیل مہاسے نہیں پہچان سکتا، اور عام موبائل تصاویر اس کے لیے مشکل ہیں۔"),
        ("اعتماد کی شرح کا کیا مطلب ہے؟", "یہ ماڈل کا یقین ہے، جسے کیلیبریٹ کیا گیا ہے تاکہ 80% کا مطلب تقریباً 10 میں سے 8 بار درست ہو۔ تصویر پر 50% سے کم ہو تو ایپ کہتی ہے کہ واضح نہیں اور ڈاکٹر کا مشورہ دیتی ہے۔"),
        ("ایمرجنسی میں کیا ہوتا ہے؟", "اگر پیغام میں خطرے کی علامت ہو (مثلاً سانس کی تکلیف یا سینے میں درد) تو ایپ رک جاتی ہے اور Rescue 1122 پر کال کرنے کا انتباہ دکھاتی ہے۔"),
        ("یہ کبھی مزید تفصیل کیوں مانگتا ہے؟", "'مدد' جیسے بہت مختصر پیغام کو جلد کے مسئلے سے نہیں ملایا جا سکتا۔ بتائیں کہ مسئلہ کہاں ہے، کتنے عرصے سے ہے اور خارش یا درد ہے یا نہیں۔"),
        ("اسے کس نے بنایا؟", "محمد عبداللہ نواز (آئیڈیا اور لیڈ) نے تین ساتھیوں کے ساتھ، زیرِ نگرانی میم صبا رمضان، یونیورسٹی آف لاہور۔"),
    ]},
}
t = TXT[lang]
ui.hero(t["eyebrow"], t["title"], t["sub"])
for i, (q, a) in enumerate(t["qa"]):
    with st.expander(q, expanded=(i == 0)):
        st.write(a)
