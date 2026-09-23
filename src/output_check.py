"""
Output check: the last safety step, runs on every AI answer before it is kept.
Rule-based (plain Python), so it gives the same result every time.

- Medicine names or doses  -> the answer is held back and replaced with a safe message
- Definite-diagnosis wording -> the answer is held back and replaced with a safe message
- No advice to see a doctor -> a short reminder is added
The word lists are a starting point. Add more names when you find gaps.
"""
import re

MEDICINES = [
    "paracetamol", "acetaminophen", "ibuprofen", "aspirin", "diclofenac", "naproxen",
    "amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline", "cephalexin", "clindamycin",
    "prednisone", "prednisolone", "hydrocortisone", "betamethasone", "clobetasol", "mometasone",
    "clotrimazole", "terbinafine", "fluconazole", "ketoconazole", "miconazole", "griseofulvin",
    "tretinoin", "isotretinoin", "adapalene", "benzoyl peroxide", "minoxidil", "methotrexate",
    "cetirizine", "loratadine", "chlorpheniramine", "permethrin", "ivermectin", "calamine",
]
MEDICINE_RE = re.compile(r"\b(" + "|".join(re.escape(m) for m in MEDICINES) + r")\b", re.I)
DOSE_RE = re.compile(r"\b\d+(\.\d+)?\s?(mg|mcg|µg|ml|iu)\b|\b(tablets?|capsules?|syrup)\b", re.I)

DIAGNOSIS_RE = re.compile(
    r"\byou (definitely |certainly |clearly )have\b"
    r"|\byou are suffering from\b"
    r"|\byou (have been|are) diagnosed\b"
    r"|\bthis is (definitely|certainly|clearly)\b"
    r"|\b(i|we) diagnose\b"
    r"|\bthe diagnosis is\b"
    r"|آپ کو یقینی طور پر|تشخیص یہ ہے",
    re.I,
)

DOCTOR_RE = re.compile(r"\b(doctor|dermatologist|physician|healthcare professional|medical professional)\b|ڈاکٹر|معالج", re.I)

SAFE_EN = (
    "This answer was held back because it contained treatment or diagnosis wording that this app does not give. "
    "Please see a doctor about these symptoms. The knowledge base matches below may help you describe them."
)
SAFE_UR = (
    "یہ جواب روک دیا گیا کیونکہ اس میں علاج یا تشخیص کے الفاظ تھے جو یہ ایپ نہیں دیتی۔ "
    "براہ کرم ان علامات کے بارے میں ڈاکٹر سے ملیں۔ نیچے دی گئی معلومات آپ کو علامات بیان کرنے میں مدد دے سکتی ہیں۔"
)
REMINDER_EN = "\n\nPlease see a doctor if the symptoms last, spread or worry you."
REMINDER_UR = "\n\nاگر علامات برقرار رہیں، پھیلیں یا پریشانی ہو تو ڈاکٹر سے ملیں۔"


def _is_urdu(text: str) -> bool:
    return any("\u0600" <= ch <= "\u06FF" for ch in text)


def apply_output_check(text: str):
    """Return (final_text, report). report['action'] is passed, disclaimer_added or blocked."""
    medicine = sorted({m.group(0).lower() for m in MEDICINE_RE.finditer(text)} | {m.group(0).lower() for m in DOSE_RE.finditer(text)})
    diagnosis = sorted({m.group(0).lower() for m in DIAGNOSIS_RE.finditer(text)})
    doctor = bool(DOCTOR_RE.search(text))
    urdu = _is_urdu(text)
    report = {"medicine": medicine, "diagnosis": diagnosis, "doctor": doctor, "words": len(text.split())}

    if medicine or diagnosis:
        report["action"] = "blocked"
        return (SAFE_UR if urdu else SAFE_EN), report
    if not doctor:
        report["action"] = "disclaimer_added"
        return text.rstrip() + (REMINDER_UR if urdu else REMINDER_EN), report
    report["action"] = "passed"
    return text, report
