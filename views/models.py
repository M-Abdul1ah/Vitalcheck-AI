"""Models / results page. Numbers are read from the result files in training/results, not typed by hand."""
import csv

import streamlit as st

from src import ui

lang = ui.current_lang()
RES = ui.ROOT / "training" / "results"

TXT = {
    "en": {
        "eyebrow": "Models and results", "title": "Our numbers, including the weak ones",
        "sub": "Both models were trained by us. Results are on held-out test data, with the limits stated next to them.",
        "tab_net": "DermaVC-Net (photo)", "tab_text": "DermaVC-Text (symptoms)",
        "acc": "Accuracy", "f1": "Macro F1", "mel": "Melanoma recall", "auc": "AUC",
        "deployed": "Deployed model: EfficientNet-B0 fine-tuned (seed 7)",
        "bench_t": "Three models, three seeds each (mean ± std)",
        "model": "Model", "params": "Params (M)", "size": "Size (MB)",
        "chart": "Accuracy and macro F1 (mean of 3 seeds)",
        "calib": "Calibration: expected error 0.070 before and 0.029 after temperature scaling.",
        "cal_img": "Calibration curve", "cam": "Grad-CAM: where the model looked",
        "limits_t": "Limits you should know",
        "limits": [
            "Trained on dermoscopy images (HAM10000), mostly moles. Ordinary phone photos are harder; this gap is not measured yet.",
            "It knows 7 classes only. It cannot recognise acne, eczema or rashes, so low confidence means 'see a doctor'.",
            "Melanoma recall is about 65%, which is weak. That is why the app shows the top 3, adds a warning rule and always advises a doctor.",
            "HAM10000 is mostly lighter skin. A skin-tone fairness test is still to do.",
        ],
        "text_t": "Test results by language",
        "text_cols": ["Model", "Accuracy", "Macro F1", "English", "Roman Urdu", "Urdu script"],
        "text_note": "Caution: the text data is partly synthetic, and these scores come from our own held-out split, so they are likely higher than real-world accuracy. A human-written test set is planned.",
        "missing": "Result file not found on this server.",
    },
    "ur": {
        "eyebrow": "ماڈلز اور نتائج", "title": "ہمارے اعداد، کمزور اعداد سمیت",
        "sub": "دونوں ماڈل ہم نے خود تربیت دیے۔ نتائج الگ رکھے گئے ٹیسٹ ڈیٹا پر ہیں، اور حدود ساتھ لکھی ہیں۔",
        "tab_net": "DermaVC-Net (تصویر)", "tab_text": "DermaVC-Text (علامات)",
        "acc": "درستگی", "f1": "میکرو F1", "mel": "میلانوما ریکال", "auc": "AUC",
        "deployed": "استعمال میں ماڈل: EfficientNet-B0 فائن ٹیون (سیڈ 7)",
        "bench_t": "تین ماڈل، ہر ایک تین سیڈز (اوسط ± انحراف)",
        "model": "ماڈل", "params": "پیرامیٹرز (M)", "size": "سائز (MB)",
        "chart": "درستگی اور میکرو F1 (3 سیڈز کا اوسط)",
        "calib": "کیلیبریشن: متوقع غلطی ٹیمپریچر اسکیلنگ سے پہلے 0.070 اور بعد میں 0.029۔",
        "cal_img": "کیلیبریشن کرو", "cam": "Grad-CAM: ماڈل نے کہاں دیکھا",
        "limits_t": "وہ حدود جو جاننا ضروری ہیں",
        "limits": [
            "تربیت ڈرموسکوپی تصاویر (HAM10000) پر ہوئی، زیادہ تر تل۔ عام موبائل تصاویر مشکل ہیں؛ یہ فرق ابھی ناپا نہیں گیا۔",
            "یہ صرف 7 اقسام جانتا ہے۔ کیل مہاسے، ایگزیما یا خارش نہیں پہچان سکتا، اس لیے کم اعتماد کا مطلب ہے 'ڈاکٹر سے ملیں'۔",
            "میلانوما ریکال تقریباً 65% ہے جو کمزور ہے۔ اسی لیے ایپ ٹاپ 3 دکھاتی ہے، انتباہی اصول لگاتی ہے اور ہمیشہ ڈاکٹر کا مشورہ دیتی ہے۔",
            "HAM10000 زیادہ تر ہلکی رنگت کی جلد پر ہے۔ رنگت کے لحاظ سے منصفانہ پن کی جانچ باقی ہے۔",
        ],
        "text_t": "زبان کے لحاظ سے ٹیسٹ نتائج",
        "text_cols": ["ماڈل", "درستگی", "میکرو F1", "انگریزی", "رومن اردو", "اردو رسم الخط"],
        "text_note": "احتیاط: ٹیکسٹ ڈیٹا جزوی طور پر مصنوعی ہے اور یہ اسکور ہمارے اپنے الگ کیے گئے حصے پر ہیں، اس لیے حقیقی دنیا کی درستگی سے زیادہ ہو سکتے ہیں۔ انسانی لکھا ٹیسٹ سیٹ منصوبے میں ہے۔",
        "missing": "اس سرور پر نتائج کی فائل نہیں ملی۔",
    },
}
t = TXT[lang]


def read_csv(path):
    return list(csv.DictReader(path.open(encoding="utf-8"))) if path.exists() else []


def first_number(cell):
    """'0.821 ± 0.009' -> 0.821"""
    try:
        return float(str(cell).split("±")[0].strip())
    except ValueError:
        return None


def metrics_row(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.markdown(f'<div class="card stat"><b>{ui.esc(value)}</b><span>{ui.esc(label)}</span></div>', unsafe_allow_html=True)


ui.hero(t["eyebrow"], t["title"], t["sub"])
tab_net, tab_text = st.tabs([t["tab_net"], t["tab_text"]])

with tab_net:
    ui.section(t["deployed"])
    metrics_row([(t["acc"], "0.826"), (t["f1"], "0.758"), (t["mel"], "0.649"), (t["auc"], "0.967")])
    ui.section(t["bench_t"])
    bench = read_csv(RES / "benchmark_mean_std.csv")
    if bench:
        names = {"A_scratch": "A: scratch CNN", "B_mobilenet_frozen": "B: MobileNetV2 frozen", "C_effnet_finetune": "C: EfficientNet-B0 fine-tuned"}
        rows = [{t["model"]: names.get(r["model"], r["model"]), t["acc"]: r["accuracy"], t["f1"]: r["macro_f1"],
                 t["mel"]: r["melanoma_recall"], t["auc"]: r["auc"], t["params"]: r["params_m"].split("±")[0].strip(),
                 t["size"]: r["size_mb"].split("±")[0].strip()} for r in bench]
        st.dataframe(rows, hide_index=True)
        st.caption(t["chart"])
        st.bar_chart({t["acc"]: {names.get(r["model"], r["model"]): first_number(r["accuracy"]) for r in bench},
                      t["f1"]: {names.get(r["model"], r["model"]): first_number(r["macro_f1"]) for r in bench}})
    else:
        st.info(t["missing"])
    st.caption(t["calib"])
    c1, c2 = st.columns(2)
    for col, fname, cap in ((c1, "calibration_C.png", t["cal_img"]), (c2, "gradcam_C.png", t["cam"])):
        if (RES / fname).exists():
            col.image(str(RES / fname), caption=cap)
    ui.section(t["limits_t"])
    for item in t["limits"]:
        st.markdown(f"- {item}")

with tab_text:
    ui.section(t["text_t"])
    rows = read_csv(RES / "text_results" / "test_benchmark_results.csv")
    if rows:
        keys = ["Model", "Test_Accuracy", "Test_Macro_F1", "English_Acc", "Roman_Urdu_Acc", "Urdu_Script_Acc"]
        table = [{label: r[k] for label, k in zip(t["text_cols"], keys)} for r in rows]
        st.dataframe(table, hide_index=True)
        st.warning(t["text_note"])
    else:
        st.info(t["missing"])
