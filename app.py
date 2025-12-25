import streamlit as st
import random
import time
from datetime import datetime

# ==============================================================================
# 1. הגדרות מערכת ופונקציות עזר
# ==============================================================================

st.set_page_config(
    page_title="PICU Pro - מערכת מומחה לטיפול נמרץ",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_clean_html(text):
    """מנוע תצוגה: הופך טקסט רגיל ל-HTML מעוצב עם ריווח נכון."""
    if not text: return ""
    html = text.replace("\n", "<br>")
    lines = html.split("<br>")
    formatted = []
    in_list = False
    
    for line in lines:
        cl = line.strip()
        if not cl: continue
        
        if cl.startswith("###"):
            if in_list: formatted.append("</ul>"); in_list = False
            cl = f"<h3 style='color:#0277bd; border-bottom:2px solid #e1f5fe; margin-top:25px; padding-bottom:5px;'>{cl.replace('###','')}</h3>"
        elif cl.startswith("##"):
            if in_list: formatted.append("</ul>"); in_list = False
            cl = f"<h2 style='color:#1565c0; background:#e3f2fd; padding:12px; border-radius:8px; border-right:5px solid #1565c0; margin-top:30px;'>{cl.replace('##','')}</h2>"
        elif "**" in cl and cl.startswith("**"): # טיפול בכותרות משנה מודגשות
            parts = cl.split("**")
            if len(parts) >= 3:
                cl = f"<div style='margin-bottom:8px; margin-top:12px;'><span style='font-weight:900; color:#b71c1c; font-size:1.1em;'>📌 {parts[1]}</span> <span style='color:#37474f;'>{parts[2]}</span></div>"
        elif cl.startswith("* ") or cl.startswith("- "):
            if not in_list: formatted.append("<ul style='margin-right:25px; list-style-type:disc;'>"); in_list = True
            content = cl[2:]
            if "**" in content: content = content.replace("**", "<b>").replace("**", "</b>")
            cl = f"<li style='margin-bottom:6px; line-height:1.6;'>{content}</li>"
        else:
            if in_list: formatted.append("</ul>"); in_list = False
            cl = f"<div style='margin-bottom:6px; line-height:1.6;'>{cl}</div>"
        formatted.append(cl)
    
    if in_list: formatted.append("</ul>")
    return "".join(formatted)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;700&display=swap');
    html, body, .stApp { font-family: 'Rubik', sans-serif !important; direction: rtl; text-align: right; background-color: #f4f6f9; }
    h1, h2, h3, h4, p, div, span, button { text-align: right !important; }
    .nav-card { background: white; border-radius: 15px; padding: 20px; text-align: center !important; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #1976d2; transition: 0.3s; cursor: pointer; height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
    .nav-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-color: #0d47a1; }
    .nav-icon { font-size: 3rem; margin-bottom: 10px; }
    .nav-title { font-size: 1.3rem; font-weight: bold; color: #1565c0; }
    .content-box { background: white; padding: 50px; border-radius: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.03); border-right: 8px solid #1565c0; margin-bottom: 30px; }
    .sim-monitor { background: #000; color: #0f0; padding: 20px; border-radius: 10px; font-family: 'Courier New', monospace; display: flex; justify-content: space-around; border: 4px solid #333; margin-bottom:20px; text-shadow: 0 0 5px #0f0; }
    .sim-val { font-size: 2.5rem; font-weight: bold; }
    .sim-label { font-size: 0.9rem; color: #888; }
    .stButton button { width: 100%; font-weight: 600; border-radius: 10px; padding: 12px; height: auto; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. האנציקלופדיה הרפואית (FULL DATABASE)
# ==============================================================================

FULL_DB = {
    "💊 תרופות ופרמקולוגיה": {
        "icon": "💊",
        "description": "אינדקס מלא: סדציה, החייאה, אינוטרופים, אלקטרוליטים.",
        "topics": {
            "אדנוזין (Adenosine)": {
                "text": """## אדנוזין (Adenosine)
**אינדיקציה:** SVT.
**אופן מתן קריטי:** זמן מחצית חיים קצר מאוד (<10 שניות). חובה לתת בשיטת **Push-Flush**: הזרקה מהירה בברז הכי קרוב ללב -> מיד שטיפה בולוס 5-10 מ"ל סליין -> הרמת הגפה.
**מינונים:**
* מנה 1: 0.1 מ"ג/ק"ג (מקס' 6 מ"ג).
* מנה 2: 0.2 מ"ג/ק"ג (מקס' 12 מ"ג).
**תופעות לוואי:** תחושת מועקה בחזה, הסמקה, Asystole רגעית (מפחיד אך צפוי).""", "image": ""},
            "אדרנלין (Epinephrine)": {
                "text": """## אדרנלין (Epinephrine)
**ריכוזים ומינונים (בטיחות!):**
**1. החייאה (IV/IO):** מינון **0.01 מ"ג/ק"ג**. ריכוז 1:10,000 (כלומר 0.1 מ"ל לק"ג). מקס' 1 מ"ג. כל 3-5 דק'.
**2. אנפילקסיס (IM):** מינון **0.01 מ"ג/ק"ג**. ריכוז 1:1,000 (לא מדולל). מקס' 0.5 מ"ג.
**3. דריפ (Inotrope):** 0.05-1.0 מק"ג/ק"ג/דקה.
**4. אינהלציה (סטרידור):** 0.5 מ"ל/ק"ג (מקס' 5 מ"ל).""", "image": ""},
            "אשלגן (Potassium)": {
                "text": """## אשלגן (K)
**ערכים:** 3.5-5.0 mEq/L.
**היפוקלמיה:** חובה לתקן **מגנזיום** קודם! (אחרת אשלגן בורח בשתן). קצב IV מקסימלי 0.5-1 mEq/kg/h.
**היפרקלמיה (חירום):**
1. **קלציום גלוקונט:** הגנה על הלב (Cardioprotection). לא מוריד אשלגן!
2. **אינסולין (0.1 יח'/ק"ג) + גלוקוז:** הכנסת אשלגן לתאים.
3. **ונטולין:** אינהלציה.
4. **פוסיד / Kayexalate:** פינוי מהגוף.""", "image": ""},
            "דופמין (Dopamine)": {
                "text": """## דופמין
אינוטרופ (פחות בשימוש כיום).
**מינונים:** * 2-5 מק"ג/ק"ג/דק': "כליתי" (שנוי במחלוקת).
* 5-10 מק"ג/ק"ג/דק': בטא (לבבי).
* 10-20 מק"ג/ק"ג/דק': אלפא (ווסקולרי - מעלה ל"ד).""", "image": ""},
            "הידרוקורטיזון": {
                "text": """## הידרוקורטיזון (Hydrocortisone)
פעילות מינרלו+גלוקוקורטיקואידית.
**אינדיקציה:** שוק ספטי עמיד (חשד לאי ספיקת אדרנל).
**מינון:** בולוס 50-100 מ"ג/מ"ר גוף (או 1-2 מ"ג/ק"ג). אח"כ 50-100 מ"ג/מ"ר/24 שעות.""", "image": ""},
            "ונטולין (Salbutamol)": {
                "text": """## ונטולין (Ventolin)
מרחיב סימפונות.
**אינהלציה:** 0.15 מ"ג/ק"ג (מינימום 2.5 מ"ג). בהתקף קשה ניתן לתת ברצף.
**IV:** במצבי קיצון, בולוס 10 מק"ג/ק"ג ואז דריפ.
**ת"ל:** טכיקרדיה, רעד, היפוקלמיה.""", "image": ""},
            "מידזולם (Dormicum)": {
                "text": """## מידזולם (Midazolam)
בנזודיאזפין. סדציה/פרכוס.
**מינון IV:** 0.1-0.2 מ"ג/ק"ג. דריפ: 1-5 מק"ג/ק"ג/דקה.
**דגש:** זהירות בתינוקות מתחת לחצי שנה (דיכוי נשימתי).
**אנטידוט:** פלומזניל.""", "image": ""},
            "נוראדרנלין (Levophed)": {
                "text": """## נוראדרנלין (Norepinephrine)
מכווץ כלי דם חזק (אלפא). תרופת בחירה בשוק ספטי ("שוק חם").
**מינון:** 0.05-1.0 מק"ג/ק"ג/דקה.
**מתן:** רצוי בוריד מרכזי (סכנת נמק בפריפרי).""", "image": ""},
            "פניטואין (Epanutin)": {
                "text": """## פניטואין (Phenytoin)
אנטי-אפילפטי.
**חובה:** לדלל ב-Normal Saline בלבד! (מתגבש בגלוקוז).
**פילטר:** חובה להשתמש בסט עם פילטר 0.2 מיקרון.
**קצב:** איטי! (מקס' 1 מ"ג/ק"ג/דקה) למניעת הפרעות קצב ונפילת ל"ד.""", "image": ""},
            "קטמין (Ketamine)": {
                "text": """## קטמין (Ketamine)
הרדמה דיסוציאטיבית.
**יתרון:** שומר ל"ד ונשימה (מצוין לשוק/אסטמה).
**מינון:** 1-2 מ"ג/ק"ג (IV), 4-5 מ"ג/ק"ג (IM).
**ת"ל:** ריור (אפשר לשלב אטרופין), הזיות בהתעוררות.""", "image": ""},
            "רוקורוניום (Esmeron)": {
                "text": """## רוקורוניום
משתק שרירים.
**אינטובציה (RSI):** 1 מ"ג/ק"ג. משך השפעה 30-45 דק'.
**אזהרה:** המטופל משותק אך ער! חובה לתת סדציה לפני.""", "image": ""}
        }
    },
    "🚑 מצבי חירום והחייאה": {
        "icon": "🚑",
        "description": "שוק, ספסיס, טראומה, כוויות, הרעלות.",
        "topics": {
            "החייאה (PALS)": {
                "text": """## החייאת ילדים (PALS)
**עיסויים:** עומק 1/3 בית חזה, קצב 100-120. יחס 15:2 (שני מטפלים).
**דפיברילציה (VF/pVT):** מנה ראשונה **2 J/kg**. מנה שניה **4 J/kg**. המשך עד 10 J/kg.
**תרופות:** אדרנלין (כל 3-5 דק'), אמיאודורון 5 מ"ג/ק"ג (ב-VF עמיד).""", "image": ""},
            "שוק היפוולמי": {
                "text": """## שוק היפוולמי
השכיח ביותר (התייבשות/דימום).
**קליניקה:** טכיקרדיה (ראשון), מילוי קפילרי איטי, ל"ד נמוך (מאוחר!).
**טיפול:**
1. בולוס נוזלים 20 מ"ל/ק"ג (איזוטוני).
2. חזרה עד 3 פעמים (60 מ"ל/ק"ג).
3. דם (10 מ"ל/ק"ג) אם אין שיפור.""", "image": ""},
            "שוק ספטי": {
                "text": """## ספסיס ושוק ספטי
**טיפול Golden Hour:**
1. חמצן וגישה ורידית.
2. נוזלים (20-60 מ"ל/ק"ג).
3. **אנטיביוטיקה:** תוך 60 דקות! (Meropenem/Ceftriaxone).
4. אינוטרופים (אדרנלין לשוק קר, נוראדרנלין לשוק חם).""", "image": ""},
            "אנפילקסיס": {
                "text": """## אנפילקסיס
**טיפול מיידי:** אדרנלין IM (0.01 מ"ג/ק"ג). לא לחכות!
**טיפול תומך:** נוזלים (דליפה קפילרית), ונטולין.
**קו שני:** סטרואידים ואנטיהיסטמינים.""", "image": ""},
            "כוויות (Burns)": {
                "text": """## כוויות ונוסחת פרקלנד
**חישוב נוזלים:** `4 מ"ל * משקל * % כוויה`.
* 50% ב-8 שעות ראשונות. 50% ב-16 הבאות.
* **ילדים:** להוסיף נוזלי אחזקה (Maintenance) עם סוכר!
**שאיפת עשן:** אינטובציה מוקדמת לפני בצקת דרכי אוויר.""", "image": ""},
            "הרעלות": {
                "text": """## הרעלות נפוצות
**אקמול:** פגיעה כבדית. אנטידוט: NAC (Mucomyst).
**אופיאטים:** אישוני סיכה, דיכוי נשימתי. אנטידוט: נלוקסון (0.1 מ"ג/ק"ג).
**זרחנים אורגניים:** ריור, דמעת, ברדיקרדיה. טיפול: אטרופין.""", "image": ""},
            "הכשות נחש": {
                "text": """## הכשת נחש (צפע)
**עקרונות:** מנוחה, קיבוע גפה, סימון גבול נפיחות.
**אסור:** למצוץ ארס, לחסום עורקים, לקרר.
**טיפול:** אנטי-סרום (בסימנים סיסטמיים/התפשטות מהירה), נוזלים, אנלגזיה.""", "image": ""}
        }
    },
    "🧠 נוירולוגיה": {
        "icon": "🧠",
        "description": "TBI, פרכוסים, מנינגיטיס, DI/SIADH.",
        "topics": {
            "חבלת ראש (TBI)": {
                "text": """## חבלת ראש (TBI)
**יעד:** CPP (לחץ זילוח) תקין.
**Cushing Triad:** ית"ל + ברדיקרדיה + נשימה לא סדירה (סימן להרניאציה).
**טיפול ב-ICP:**
1. הרמת ראש 30 מעלות.
2. סליין היפרטוני 3% (3-5 מ"ל/ק"ג) או מניטול.
3. היפרוונטילציה (רק כמוצא אחרון).""", "image": ""},
            "סטטוס אפילפטיקוס": {
                "text": """## סטטוס אפילפטיקוס
**פרוטוקול:**
1. ABC, סוכר.
2. **מיידי:** מידזולם (IV/IM).
3. **העמסה:** פניטואין (בסליין!), קפרה, או פנוברביטל.
4. **הרדמה:** מידזולם דריפ/פרופופול.""", "image": ""},
            "מנינגיטיס": {
                "text": """## מנינגיטיס
**סימנים:** חום, קשיון עורף, פוטופוביה, פטכיות.
**טיפול:** רוצפין (מינון מנינגיאלי 100 מ"ג/ק"ג) + ואנקומיצין.
**בידוד:** מגע + נשימתי.""", "image": ""},
            "DI vs SIADH": {
                "text": """## מאזן מלחים מוחי
**DI:** חסר ADH. שתן מרובה ובהיר, **היפרנתרמיה**. טיפול: נוזלים, DDAVP.
**SIADH:** עודף ADH. מיעוט שתן, **היפונתרמיה** (דילול). טיפול: הגבלת נוזלים.""", "image": ""},
            "ADEM": {
                "text": """## ADEM
דלקת אוטואימונית של המוח וחוט השדרה (לרוב פוסט-ויראלי).
**טיפול:** סטרואידים (Pulse), IVIG, פלזמפרזיס.""", "image": ""}
        }
    },
    "🩸 המטו-אונקולוגיה": {
        "icon": "🩸",
        "description": "לוקמיה, TLS, מוצרי דם.",
        "topics": {
            "לוקמיה ונויטרופניה": {
                "text": """## לוקמיה ונויטרופניה
**חום ונויטרופניה:** מצב חירום! סכנת ספסיס.
**טיפול:** אנטיביוטיקה רחבת טווח (כולל פסאודומונס) תוך שעה!""", "image": ""},
            "TLS (פירוק גידול)": {
                "text": """## Tumor Lysis Syndrome
**מעבדה:** היפרקלמיה, היפר-אוריצמיה, היפר-פוספטמיה, היפוקלצמיה.
**טיפול:** הידרציה (בלי אשלגן!), אלופרינול, Rasburicase (**אסור ב-G6PD!**).""", "image": ""},
            "מתן מוצרי דם": {
                "text": """## מוצרי דם
**PC:** מינון 10-15 מ"ל/ק"ג. חובה פילטר.
**טסיות:** 5-10 מ"ל/ק"ג. **אסור במשאבה (IVAC)!** (הרס מכאני). לתת בגרביטציה.
**הקרנה:** חובה במדוכאי חיסון.""", "image": ""},
            "אנמיה אפלסטית": {
                "text": """## אנמיה אפלסטית
כשל של מח העצם (ירידה בכל השורות).
**טיפול:** תמיכה בדם, אימונוסופרסיה (ATG), השתלת מח עצם.""", "image": ""}
        }
    },
    "🍏 גסטרו ותזונה": {
        "icon": "🍏",
        "description": "TPN, כבד, מטבולי.",
        "topics": {
            "TPN והזנה": {
                "text": """## TPN
הזנה תוך ורידית.
**סיבוכים:** זיהום צנתר (CLABSI), הפרעות אלקטרוליטים.
**Refeeding Syndrome:** נפילת זרחן ואשלגן בהזנה מהירה לאחר רעב. סכנת חיים!""", "image": ""},
            "אי ספיקת כבד": {
                "text": """## אי ספיקת כבד
**סימנים:** צהבת, הפרעת קרישה (INR גבוה), אנצפלופתיה.
**טיפול:** ויטמין K, פלזמה, מניעת בצקת מוחית, שמירה על סוכר.""", "image": ""},
            "מחלות מטבוליות": {
                "text": """## משבר מטבולי
**חשד:** חמצת לא מוסברת, היפוגליקמיה, אמוניה גבוהה.
**טיפול:** הפסקת כלכלה (חלבון), מתן גלוקוז גבוה (מניעת קטבוליזם).""", "image": ""},
            "דימום עיכול": {
                "text": """## דימום GI
**טיפול:** זונדה (שטיפה), נוזלים/דם, PPI, אוקטריאוטיד (לדליות).""", "image": ""},
            "FTT": {
                "text": """## FTT (Failure to Thrive)
חוסר עלייה במשקל. בירור תזונתי ומטבולי. טיפול: העשרה קלורית.""", "image": ""}
        }
    }
}

ALL_QUESTIONS = [
    {"q": "מה המינון של אדרנלין IV בהחייאה?", "opts": ["0.01 מ\"ג/ק\"ג (1:10,000)", "0.1 מ\"ג/ק\"ג", "1 מ\"ג/ק\"ג", "0.5 מ\"ג"], "a": "0.01 מ\"ג/ק\"ג (1:10,000)", "exp": "דילול 1:10,000."},
    {"q": "באיזה תמיסה מדללים פניטואין?", "opts": ["סליין (NS)", "גלוקוז 5%", "מים מזוקקים", "הרטמן"], "a": "סליין (NS)", "exp": "שוקע בגלוקוז."},
    {"q": "מה הטיפול המיידי בהיפרקלמיה עם אק\"ג לא תקין?", "opts": ["קלציום גלוקונט", "פוסיד", "קייקסלאט", "ונטולין"], "a": "קלציום גלוקונט", "exp": "מייצב לב."},
    {"q": "Cushing Triad כולל:", "opts": ["ית\"ל, ברדיקרדיה, נשימה לא סדירה", "תת\"ל, טכיקרדיה, חום", "אישונים צרים, הזעה", "כאב ראש, הקאה"], "a": "ית\"ל, ברדיקרדיה, נשימה לא סדירה", "exp": "סימן ל-ICP מוגבר."},
    {"q": "תרופה אסורה ב-TLS עם G6PD?", "opts": ["Rasburicase", "Allopurinol", "Furosemide", "Calcium"], "a": "Rasburicase", "exp": "סכנת המוליזה."},
    {"q": "טיפול ראשון באנפילקסיס?", "opts": ["אדרנלין IM", "סטרואידים", "ונטולין", "אנטיביוטיקה"], "a": "אדרנלין IM", "exp": "מציל חיים."},
    {"q": "איך נותנים אדנוזין?", "opts": ["Push-Flush מהיר", "דריפ איטי", "IM", "PO"], "a": "Push-Flush מהיר", "exp": "זמן מחצית חיים קצר."},
    {"q": "נוסחת פרקלנד לכוויות:", "opts": ["4 מ\"ל * ק\"ג * % כוויה", "2 מ\"ל * ק\"ג", "100 מ\"ל/ק\"ג", "לפי גיל"], "a": "4 מ\"ל * ק\"ג * % כוויה", "exp": "נוזלים ל-24 שעות."},
    {"q": "סימן ל-Diabetes Insipidus:", "opts": ["שתן בהיר מרובה, היפרנתרמיה", "מיעוט שתן, היפונתרמיה", "סוכר גבוה", "חום"], "a": "שתן בהיר מרובה, היפרנתרמיה", "exp": "חסר ADH."},
    {"q": "מתן טסיות:", "opts": ["גרביטציה בלבד", "משאבה (IVAC)", "דריפ איטי", "קירור"], "a": "גרביטציה בלבד", "exp": "משאבה הורסת טסיות."}
]# ==============================================================================
# 3. מנוע סימולטור (10 שלבים)
# ==============================================================================

class SimEngine:
    def __init__(self):
        self.reset()
    def reset(self):
        self.step = 0
        self.score = 100
        self.log = []
        self.dead = False
        self.data = [
            ("ילד בן 4, הגיע עם חום, הקאות וקוצר נשימה. בבדיקה: חיוור, מילוי קפילרי 4 שניות. דופק 160, ל\"ד 90/50.",
             {"HR": 160, "BP": "90/50", "Sat": "92%"},
             [("חמצן, וריד, נוזלים 20 מ\"ל/ק\"ג", 10, "✅ התחלה מצוינת. זיהוי שוק וטיפול בנפח."), ("אקמול וניטור", -10, "⚠️ לא מספיק, הילד בסיכון לשוק."), ("אינטובציה מיידית", -30, "💀 אגרסיבי ומסוכן כרגע ללא החייאת נוזלים."), ("אנטיביוטיקה בלבד", -5, "⚠️ צריך גם נוזלים דחוף.")]),
            ("אחרי בולוס ראשון: דופק 150. ל\"ד ירד ל-80/40. הכרה ירודה מעט. לקטט 4.5.",
             {"HR": 150, "BP": "80/40", "Sat": "93%"},
             [("בולוס נוסף 20 מ\"ל/ק\"ג + אנטיביוטיקה", 10, "✅ טיפול נכון בספסיס (Golden Hour)."), ("מתן פוסיד", -50, "💀 יהרוג אותו! הוא מיובש ובשוק."), ("CT ראש", -20, "❌ החולה לא יציב להעברה."), ("רק אנטיביוטיקה", -5, "⚠️ צריך עוד נפח.")]),
            ("נשימה מאומצת מאוד (60 לדקה). סטורציה יורדת ל-88% עם חמצן. נראה תשוש.",
             {"HR": 160, "BP": "75/35", "Sat": "88%"},
             [("אינטובציה (RSI) עם קטמין ורוקורוניום", 10, "✅ אינדיקציה להנשמה. קטמין שומר ל\"ד."), ("אינטובציה עם פרופופול", -40, "💀 יפיל את לחץ הדם לקריסה."), ("אינהלציית ונטולין", -10, "❌ לא יעזור לבעיה של שוק/עייפות."), ("הגברת חמצן בלבד", -10, "❌ הוא מתעייף ויקרוס.")]),
            ("מיד אחרי האינטובציה, ל\"ד צונח ל-50/30. דופק עולה.",
             {"HR": 170, "BP": "50/30", "Sat": "98%"},
             [("דריפ אדרנלין/נוראדרנלין", 10, "✅ תמיכה אינוטרופית נדרשת."), ("עוד מידזולם", -20, "❌ יחמיר את הנפילה."), ("אקסטובציה מיידית", -50, "💀 אסור! יגרום לדום לב."), ("רק נוזלים", 0, "⚠️ אפשרי, אבל כנראה צריך אמינים.")]),
            ("דום לב פתאומי! אסיסטולה במוניטור.",
             {"HR": 0, "BP": "0/0", "Sat": "0%"},
             [("עיסויים + אדרנלין 0.01 מ\"ג/ק\"ג", 10, "✅ PALS באסיסטולה."), ("שוק חשמלי", -20, "❌ אסור לתת שוק באסיסטולה."), ("אטרופין", -10, "❌ לא בפרוטוקול."), ("בדיקת דופק דקה שלמה", -30, "💀 בדיקה מקסימום 10 שניות!")]),
            ("חזר דופק (ROSC). ל\"ד 70/40. אישונים שווים.",
             {"HR": 150, "BP": "70/40", "Sat": "95%"},
             [("ייצוב: אמינים, סדציה, קירור?", 10, "✅ Post-arrest care."), ("מתן ביקרבונט", 0, "⚠️ רק אם יש חמצת קשה מוכחת."), ("הפסקת תרופות", -20, "❌ מסוכן."), ("אקסטובציה", -50, "💀 לא.")] ),
            ("מצב יציב יותר. חום 39. פרכוס כללי קצר.",
             {"HR": 140, "BP": "85/50", "Sat": "96%"},
             [("העמסת פניטואין/קפרה", 10, "✅ מניעת פרכוסים חוזרים."), ("עוד אדרנלין", -20, "❌ יגרום להפרעות קצב."), ("התעלמות", -30, "❌ סכנה לנזק מוחי."), ("מתן סוכר", 0, "⚠️ רק אם יש היפוגליקמיה.")] ),
            ("בדיקות דם: היפוקלמיה (2.8). מגנזיום נמוך.",
             {"HR": 130, "BP": "90/60", "Sat": "98%"},
             [("תיקון מגנזיום ואז אשלגן", 10, "✅ הסדר הנכון."), ("רק אשלגן", -10, "❌ האשלגן לא יעלה בלי מגנזיום."), ("בולוס אשלגן מהיר", -50, "💀 דום לב! אסור לתת אשלגן מהר."), ("פוסיד", -10, "❌ יחמיר את המצב.")] ),
            ("שתן כהה ומועט. קריאטינין עולה. חשד ל-AKI.",
             {"HR": 120, "BP": "95/65", "Sat": "99%"},
             [("הגבלת נוזלים ומאזן מדויק", 10, "✅ מניעת גודש."), ("העמסת נוזלים", -20, "❌ סכנת בצקת ריאות."), ("דיאליזה מיד", -10, "⚠️ מוקדם מדי."), ("מתן אשלגן", -30, "💀 מסוכן בכשל כליתי.")] ),
            ("סיום: הילד יציב, מונשם, פרפוזיה טובה.",
             {"HR": 110, "BP": "100/70", "Sat": "100%"},
             [("המשך מעקב וטיפול תומך", 10, "✅ סיימת בהצלחה."), ("-", 0, ""), ("-", 0, ""), ("-", 0, "")] )
        ]

if 'sim' not in st.session_state: st.session_state.sim = SimEngine()

# ==============================================================================
# 4. לוגיקת אפליקציה ראשית
# ==============================================================================

if 'user_info' not in st.session_state: st.session_state.user_info = {}
if 'completed' not in st.session_state: st.session_state.completed = set()
if 'page' not in st.session_state: st.session_state.page = "home"

def nav(p): st.session_state.page = p; st.rerun()

# Sidebar
with st.sidebar:
    st.title("PICU Pro")
    if not st.session_state.user_info:
        name = st.text_input("שם")
        email = st.text_input("מייל")
        if st.button("כנס"):
            if email: st.session_state.user_info = {"n": name, "e": email}; st.rerun()
    else:
        st.success(f"מחובר: {st.session_state.user_info['n']}")
        if st.button("יציאה"): st.session_state.user_info = {}; st.rerun()
    
    st.markdown("---")
    if st.session_state.user_info:
        st.button("🏠 בית", on_click=lambda: nav("home"))
        st.button("📚 למידה", on_click=lambda: nav("learn"))
        st.button("🚑 סימולטור", on_click=lambda: nav("sim"))
        st.button("📝 מבחן", on_click=lambda: nav("quiz"))
        if st.session_state.user_info.get('e') == 'yishaycopp@gmail.com':
            st.button("⚙️ ניהול", on_click=lambda: nav("admin"))

# דף חסימה
if not st.session_state.user_info:
    st.header("ברוכים הבאים למערכת הלמידה PICU")
    st.info("נא להתחבר כדי לגשת לתוכן.")
    st.stop()

# ניתוב דפים
if st.session_state.page == "home":
    st.title("מרכז ידע וסימולציה")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='nav-card'><div class='nav-icon'>💊</div><div>תרופות</div></div>", unsafe_allow_html=True)
        if st.button("פתח תרופות"): st.session_state.cat_filter = "💊 תרופות ופרמקולוגיה"; nav("learn")
    with c2:
        st.markdown("<div class='nav-card'><div class='nav-icon'>🚑</div><div>חירום</div></div>", unsafe_allow_html=True)
        if st.button("פתח חירום"): st.session_state.cat_filter = "🚑 מצבי חירום והחייאה"; nav("learn")
    with c3:
        st.markdown("<div class='nav-card'><div class='nav-icon'>🧠</div><div>נוירולוגיה</div></div>", unsafe_allow_html=True)
        if st.button("פתח נוירולוגיה"): st.session_state.cat_filter = "🧠 נוירולוגיה"; nav("learn")
    
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("<div class='nav-card'><div class='nav-icon'>🩸</div><div>המטולוגיה</div></div>", unsafe_allow_html=True)
        if st.button("פתח המטולוגיה"): st.session_state.cat_filter = "🩸 המטו-אונקולוגיה"; nav("learn")
    with c5:
        st.markdown("<div class='nav-card'><div class='nav-icon'>🍏</div><div>גסטרו</div></div>", unsafe_allow_html=True)
        if st.button("פתח גסטרו"): st.session_state.cat_filter = "🍏 גסטרו ומטבולי"; nav("learn")
    with c6:
        st.markdown("<div class='nav-card'><div class='nav-icon'>🩺</div><div>כללי</div></div>", unsafe_allow_html=True)
        if st.button("כל הנושאים"): st.session_state.cat_filter = None; nav("learn")

elif st.session_state.page == "learn":
    st.title("ספרייה מקצועית")
    
    cats = list(FULL_DB.keys())
    default_ix = 0
    if st.session_state.get('cat_filter') in cats:
        default_ix = cats.index(st.session_state.cat_filter)
    
    cat = st.selectbox("תחום:", cats, index=default_ix)
    
    # לוגיקה לתרופות (מיון א-ת) מול שאר הנושאים
    if "תרופות" in cat:
        # איסוף כל התרופות מכל תתי הקטגוריות לרשימה אחת ממוינת
        all_d = {}
        for sub in FULL_DB[cat]['topics'].values():
            # בדיקה אם המבנה הוא ישיר או מקונן
            # במבנה הנוכחי FULL_DB[cat]['topics'] מכיל ישירות את התרופות
            pass 
        # במבנה הנתונים שבנינו, 'topics' מכיל ישירות את הפרוטוקולים.
        # אם נרצה לאחד תתי-קטגוריות בעתיד נצטרך לולאה כפולה. כרגע זה שטוח בתוך topics.
        drugs = sorted(FULL_DB[cat]['topics'].keys())
        choice = st.selectbox("בחר תרופה (א-ת):", drugs)
        data = FULL_DB[cat]['topics'][choice]
    else:
        # נושאים אחרים: חלוקה לתתי נושאים (אם יש) או רשימה שטוחה
        # בקוד זה, חלק מהקטגוריות ב-FULL_DB הן עם 'subcategories' וחלק עם 'topics' ישירות.
        # כדי למנוע קריסה, נבדוק את המבנה:
        if 'subcategories' in FULL_DB[cat]:
            subcats = list(FULL_DB[cat]['subcategories'].keys())
            sc = st.radio("נושא:", subcats, horizontal=True)
            prots = list(FULL_DB[cat]['subcategories'][sc].keys())
            choice = st.selectbox("פרוטוקול:", prots)
            data = FULL_DB[cat]['subcategories'][sc][choice]
        else:
            # מבנה שטוח (כמו תרופות בחלק מהגרסאות, או נושאים פשוטים)
            prots = list(FULL_DB[cat]['topics'].keys())
            choice = st.selectbox("פרוטוקול:", prots)
            data = FULL_DB[cat]['topics'][choice]
        
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.markdown(render_clean_html(data['text']), unsafe_allow_html=True)
    if data['image']: st.image(data['image'], width=400)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.checkbox("סיימתי ללמוד ✅", key=choice):
        st.session_state.completed.add(choice)

elif st.session_state.page == "sim":
    st.title("סימולטור")
    s = st.session_state.sim
    if st.button("התחל מחדש"): s.reset(); st.rerun()
    
    if s.step < len(s.data):
        d = s.data[s.step]
        st.markdown(f"""
        <div class='sim-monitor'>
            <div>HR: <span class='sim-val'>{d[1]['HR']}</span></div>
            <div>BP: <span class='sim-val'>{d[1]['BP']}</span></div>
            <div>SAT: <span class='sim-val'>{d[1]['Sat']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(d[0])
        
        cols = st.columns(2)
        opts = d[2]
        # אנחנו לא מערבבים את הרשימה המקורית כדי לא לשבור לוגיקה אם הייתה תלויית אינדקס
        # אבל כאן הכל בתוך ה-tuple אז אפשר להציג מעורבב
        shuffled_opts = random.sample(opts, len(opts))
        
        for i, opt in enumerate(shuffled_opts):
            if cols[i%2].button(opt[0], key=f"o{s.step}{i}"):
                s.score += opt[1]
                s.log.append(f"שלב {s.step+1}: {opt[0]} ({opt[2]})")
                if opt[1] <= -30: s.dead = True
                s.step += 1
                st.rerun()
    else:
        if s.dead:
            st.error("💀 המטופל קרס. הסימולציה נכשלה.")
        else:
            st.success(f"🎉 סיימת! ציון: {s.score}")
            if s.score > 80: st.balloons()
        
        with st.expander("סיכום מהלך הטיפול"):
            for l in s.log: st.write(l)

elif st.session_state.page == "quiz":
    st.title("מבחן ידע")
    num = st.number_input("מספר שאלות:", 1, len(ALL_QUESTIONS), 5)
    if st.button("צור מבחן"):
        st.session_state.q_curr = random.sample(ALL_QUESTIONS, num)
        st.session_state.q_res = None
        
    if 'q_curr' in st.session_state:
        score = 0
        with st.form("qf"):
            for i, q in enumerate(st.session_state.q_curr):
                st.write(f"**{i+1}. {q['q']}**")
                # ערבוב תשובות
                # אנו צריכים לשמור על הקשר בין הטקסט לתשובה הנכונה
                # q['opts'] היא רשימה. q['a'] היא התשובה הנכונה (טקסט)
                ops = q['opts'].copy()
                random.shuffle(ops)
                
                sel = st.radio(f"תשובה {i}", ops, key=f"q{i}", label_visibility="collapsed")
                if sel == q['a']: score += 1
                st.markdown("---")
            
            if st.form_submit_button("הגש"):
                st.session_state.q_res = score
                
        if st.session_state.q_res is not None:
            final = int(st.session_state.q_res/len(st.session_state.q_curr)*100)
            st.metric("ציון", f"{final}%")
            if final > 80: st.success("כל הכבוד!")
            else: st.warning("כדאי לחזור על החומר.")
            
            for i, q in enumerate(st.session_state.q_curr):
                with st.expander(f"הסבר לשאלה {i+1}"):
                    st.info(f"התשובה הנכונה: {q['a']}")
                    st.write(q['exp'])

elif st.session_state.page == "admin":
    st.title("ניהול")
    st.info("ממשק עריכה מלא יחובר למסד נתונים חיצוני בגרסת הפרודקשן.")
