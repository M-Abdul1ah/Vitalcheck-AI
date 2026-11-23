"""
Content for the extra pages (Team, footer links). No Streamlit import here, so tests can load it.
To change a name, role, bio or link, edit this file only. To add a photo, save it as
assets/team/<slug>.jpg (or .png) and it shows up automatically.
"""

GITHUB_URL = "https://github.com/M-Abdul1ah/Vitalcheck-AI"
ISSUES_URL = GITHUB_URL + "/issues"
EMAIL = "mabdullahnawaz2006@gmail.com"
EMERGENCY_NUMBER = "1122"

SUPERVISOR = {
    "slug": "saba-ramzan",
    "name": "Mam Saba Ramzan",
    "title_en": "Lecturer, Department of Computer Science",
    "title_ur": "لیکچرر، شعبہ کمپیوٹر سائنس",
    "university_en": "University of Lahore (UOL)",
    "university_ur": "یونیورسٹی آف لاہور (UOL)",
}

# role / bio are placeholders taken from the project docs. Replace them when the team sends its details.
TEAM = [
    {
        "slug": "abdullah",
        "name": "Muhammad Abdullah Nawaz",
        "role_en": "Team Lead and ML Engineer",
        "role_ur": "ٹیم لیڈ اور ایم ایل انجینئر",
        "bio_en": "Idea, architecture, model training, evaluation and app integration.",
        "bio_ur": "آئیڈیا، آرکیٹیکچر، ماڈل ٹریننگ، جانچ اور ایپ انٹیگریشن۔",
        "github": "https://github.com/M-Abdul1ah",
        "linkedin": "",   # paste the LinkedIn profile link here
    },
    {
        "slug": "yousaf",
        "name": "M. Yousaf",
        "role_en": "Data Lead",
        "role_ur": "ڈیٹا لیڈ",
        "bio_en": "Datasets and symptom-text models (DermaVC-Text).",
        "bio_ur": "ڈیٹا سیٹس اور علامات کے ٹیکسٹ ماڈلز (DermaVC-Text)۔",
        "github": "",
        "linkedin": "",
    },
    {
        "slug": "izhan",
        "name": "Izhan",
        "role_en": "Training Lead",
        "role_ur": "ٹریننگ لیڈ",
        "bio_en": "Model training and calibration for DermaVC-Text.",
        "bio_ur": "DermaVC-Text کی ٹریننگ اور کیلیبریشن۔",
        "github": "",
        "linkedin": "",
    },
    {
        "slug": "abdul-rehman",
        "name": "Abdul Rehman",
        "role_en": "Knowledge Base and Evaluation",
        "role_ur": "نالج بیس اور جانچ",
        "bio_en": "Knowledge-base sources, test sets and model card.",
        "bio_ur": "نالج بیس کے ذرائع، ٹیسٹ سیٹ اور ماڈل کارڈ۔",
        "github": "",
        "linkedin": "",
    },
]


def initials(name):
    """'Muhammad Abdullah Nawaz' -> 'MN' (first and last word). One word -> first two letters."""
    parts = [p for p in name.replace(".", " ").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()
