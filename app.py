import streamlit as st
import random
import json
import os
import time

# --- הגדרת קובץ נתונים ---
DB_FILE = "picu_encyclopedia.json"

# --- תוכן מלא: הועתק ועובד מתוך הקבצים ששלחת ---
DEFAULT_CONTENT = {
    "תרופות: סדציה ואנלגזיה": {
        "icon": "😴",
        "description": "הרגעה, שיכוך כאב ושיתוק שרירים.",
        "topics": {
            "מידזולם (Dormicum)": {
                "text": """### מידזולם (Midazolam)
ממשפחת הבנזודיאזפינים. הרגעה, נוגד חרדה, אנטי-פרכוסי.

#### 💉 מינונים ודרך מתן
* **IV/IM (ילדים):** 0.05-0.1 מ"ג/ק"ג.
    * מקס' מנה בודדת: 6 מ"ג (מתחת גיל 6), 10 מ"ג (מעל גיל 6).
* **פוש (IV):** לתת לאט. השפעה תוך דקות.
* **דריפ מתמשך (סדציה):** 0.8-2 מק"ג/ק"ג/דקה (מקס' 10 מ"ג/שעה).
* **מתן נאזלי (Intranasal):** 0.2 מ"ג/ק"ג (מקס' 10 מ"ג).

#### ⚠️ דגשים
* **זהירות:** בתינוקות < 6 חודשים (סיכון לדיכוי נשימתי משמעותי).
* [cite_start]**אנטידוט:** פלומזניל (Flumazenil) [cite: 93-116].""",
                "image": ""
            },
            "קטמין (Ketamine)": {
                "text": """### קטמין (Ketamine)
הרדמה דיסוציאטיבית. משמר רפלקס נשימה ול"ד (מצוין לשוק).

#### 💉 מינונים
* **החייאה/אינטובציה (IV):** 1-2 מ"ג/ק"ג.
* **סדציה מתמשכת:** 5-20 מק"ג/ק"ג/דקה.
* **IM:** מינון 4-5 מ"ג/ק"ג.

#### ⚠️ תופעות לוואי ודגשים
* ריור מוגבר (אפשר לשלב אטרופין לייבוש).
* לרינגוספאזם.
* הזיות/סיוטים בהתעוררות.
* [cite_start]**לא מעלה ICP!** (בטוח לשימוש גם בטראומת ראש לפי פרוטוקולים חדשים) [cite: 121-132, 362-366].""",
                "image": ""
            },
            "פנטניל (Fentanyl)": {
                "text": """### פנטניל (Fentanyl)
אופיאט סינטטי חזק, קצר טווח. מתאים לייצוב המודינמי.

#### 💉 מינונים
* **בולוס (IV):** 1-2 מק"ג/ק"ג (ניתן לחזור כל 30-60 דק').
* **דריפ מתמשך:** 1-4 מק"ג/ק"ג/שעה.

#### ⚠️ תופעות לוואי
* **Chest Wall Rigidity:** "חזה אבן" במתן מהיר מדי (דורש הרפיית שרירים והנשמה).
* דיכוי נשימתי.
* [cite_start]פחות משחרר היסטמין ממורפין (עדיף באסטמה/היפוטנשן) [cite: 141-153].""",
                "image": ""
            },
            "פרופופול (Propofol)": {
                "text": """### פרופופול (Propofol)
הרדמה כללית קצרת טווח.

#### 💉 מינונים
* **אינדוקציה:** 2.5-3.5 מ"ג/ק"ג (מתן תוך 20-30 שניות).
* **אחזקה:** 125-300 מק"ג/ק"ג/דקה.

#### ⚠️ דגשים
* **שורף בווריד!** (ניתן לתת לידוקאין לפני).
* גורם לירידת ל"ד (וזודילציה) ודיכוי נשימתי. אסור בשוק לא יציב!
* [cite_start]**Propofol Infusion Syndrome:** בשימוש ממושך/מינון גבוה (חמצת, רבדומיוליזיס, אי ספיקת לב) [cite: 367-377].""",
                "image": ""
            },
            "רוקורוניום (Rocuronium)": {
                "text": """### רוקורוניום (Esmeron)
משתק שרירים (Non-depolarizing).

#### 💉 מינונים
* **אינטובציה (RSI):** 1 מ"ג/ק"ג (מתן מהיר).
* **אחזקה:** 0.6-1.2 מ"ג/ק"ג/שעה (או 7-12 מק"ג/ק"ג/דקה).

#### ⚠️ חוק ברזל
**חובה לתת סדציה/אנלגזיה לפני שיתוק!** (המטופל ער אך משותק ללא סדציה).
[cite_start]זמן השפעה: תוך 30-40 שניות [cite: 154-161].""",
                "image": ""
            }
        }
    },
    "תרופות: אינוטרופים וקרדיאלי": {
        "icon": "❤️",
        "description": "תמיכה בלב ולחץ דם.",
        "topics": {
            "אדרנלין (Adrenaline)": {
                "text": """### אדרנלין (Epinephrine)
אינוטרופ חיובי, מכווץ כלי דם (אלפא+בטא).

#### 💉 מינונים
* **החייאה (IV Push):** 0.01 מ"ג/ק"ג (דילול 1:10,000). כל 3-5 דק'.
* **אנפילקסיס (IM):** 0.01 מ"ג/ק"ג (דילול 1:1,000).
* **דריפ (שוק/תמיכה):** 0.05-1.0 מק"ג/ק"ג/דקה.
* **אינהלציה (סטרידור):** 0.5 מ"ל/ק"ג (מקס' 5 מ"ל).

#### ⚠️ דגש בטיחות
[cite_start]בלבול בין ריכוז 1:1,000 (לשריר/אינהלציה) ל-1:10,000 (לווריד) הוא קטלני! [cite: 37-51].""",
                "image": ""
            },
            "נוראדרנלין (Norepinephrine)": {
                "text": """### נוראדרנלין (Levophed)
מכווץ כלי דם פריפריים חזק (אלפא אגוניסט). תרופת הבחירה לשוק ספטי "חם" (וזודילטורי).

#### 💉 מינון
* **דריפ מתמשך:** 0.05 - 1.0 מק"ג/ק"ג/דקה (טיטרציה לפי ל"ד).

#### ⚠️ דגשים
* עלול לגרום לאיסכמיה פריפרית במינון גבוה.
* [cite_start]רצוי לתת בוריד מרכזי (סיכון לנמק בפריפרי) [cite: 287-290].""",
                "image": ""
            },
            "מילרינון (Milrinone)": {
                "text": """### מילרינון (Milrinone)
מעכב פוספודיאסטראז (PDE3). מגביר כיווץ (Inotrope) ומרחיב כלי דם (Vasodilator). "Ino-dilator".

#### 💉 מינון
* **דריפ מתמשך:** 0.25 - 0.75 מק"ג/ק"ג/דקה.
* (לעיתים נותנים מנת העמסה 50 מק"ג/ק"ג - בזהירות).

#### ⚠️ דגשים
* תופעת לוואי עיקרית: **תת לחץ דם** (בגלל הרחבת כלי דם).
* [cite_start]מתאים לטיפול ב-PHTN (יתר ל"ד ריאתי) וכשל לבבי [cite: 203-207, 283-286].""",
                "image": ""
            },
            "דופמין (Dopamine)": {
                "text": """### דופמין (Dopamine)
השפעה תלוית מינון:
* **נמוך (2-5 מק"ג/ק"ג/דקה):** דופמינרגי (כליתי - שנוי במחלוקת).
* **בינוני (5-10 מק"ג/ק"ג/דקה):** בטא (כיווץ לב).
* **גבוה (10-20 מק"ג/ק"ג/דקה):** אלפא (כיווץ כלי דם).

#### ⚠️ הערה
[cite_start]פחות בשימוש כיום כקו ראשון בשוק (נוראדרנלין/אדרנלין עדיפים) [cite: 268-276].""",
                "image": ""
            }
        }
    },
    "תרופות: נוירולוגיה ואנטי-פרכוסים": {
        "icon": "🧠",
        "description": "טיפול בפרכוסים ובצקת מוחית.",
        "topics": {
            "פניטואין (Epanutin/Phenytoin)": {
                "text": """### פניטואין (Phenytoin)
תרופה אנטי-אפילפטית (קו שני בסטטוס).

#### 💉 מינון העמסה
* **IV:** מינון 20 מ"ג/ק"ג.
* **קצב:** לאט! (מקס' 1 מ"ג/ק"ג/דקה) כדי למנוע הפרעות קצב ונפילת ל"ד.

#### ⚠️ דגש קריטי
* **תמיסה:** אך ורק בסליין (NS). מתגבש בגלוקוז!
* דורש פילטר 0.2 מיקרון במתן.
* [cite_start]תופעות לוואי: היפרפלזיה של חניכיים, הפרעות קצב [cite: 312-317].""",
                "image": ""
            },
            "לבטירצטם (Keppra)": {
                "text": """### קפרה (Levetiracetam)
אנטי-פרכוסי רחב טווח. בטוח יחסית המודינמית.

#### 💉 מינונים
* **העמסה (IV):** 20-60 מ"ג/ק"ג (משתנה לפי פרוטוקול).
* **אחזקה:** 10-30 מ"ג/ק"ג למנה (פעמיים ביום).

#### ⚠️ דגשים
* לא דורש ניטור רמות בדם כמו פניטואין.
* [cite_start]ת"ל: עצבנות/שינויי התנהגות [cite: 332-346].""",
                "image": ""
            },
            "טיפול בבצקת מוחית (ICP)": {
                "text": """### טיפול תרופתי ב-ICP מוגבר
**1. סליין היפרטוני (NaCl 3%):**
* מנגנון: מושך נוזלים מהמוח לדם (אוסמוזה).
* מינון בולוס: 3-5 מ"ל/ק"ג (בהרצה מהירה במצב הרניאציה).
* דריפ: 0.1-1 מ"ל/ק"ג/שעה.
* יעד נתרן: 145-155 (או יותר בטראומה קשה).

**2. מניטול (Mannitol 20%):**
* מינון: 0.5-1 גרם/ק"ג (כ-2.5-5 מ"ל/ק"ג).
* תנאי: אוסמולריות בדם < 320.
* [cite_start]חובה להשתמש בסט עם פילטר (מונע קריסטלים) [cite: 549-563, 1152-1158].""",
                "image": ""
            }
        }
    },
    "מצבי חירום: שוק וטראומה": {
        "icon": "🚑",
        "description": "פרוטוקולי החייאה מתקדמים.",
        "topics": {
            "שוק היפוולמי": {
                "text": """## שוק היפוולמי
**טיפול:**
1. **בולוס נוזלים:** 20 מ"ל/ק"ג קריסטלואידים (סליין/הרטמן).
2. חזרה עד 3 פעמים (60 מ"ל/ק"ג).
3. אם אין תגובה (שוק המורגי) -> **דם (PC):** 10 מ"ל/ק"ג.

[cite_start]**סימנים לקריסה:** ל"ד נמוך (מאוחר!), מילוי קפילרי איטי, טכיקרדיה, שינוי הכרה [cite: 869-925].""",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Shock_types.png/640px-Shock_types.png"
            },
            "אנפילקסיס": {
                "text": """## אנפילקסיס
**קו ראשון:** אדרנלין IM (0.01 מ"ג/ק"ג).
**קו שני:** נוזלים, ונטולין, סטרואידים (סולומדרול), אנטיהיסטמינים.
**דגש:** לא לחכות עם האדרנלין! [cite_start]זהו הטיפול היחיד המונע תמותה [cite: 926-951].""",
                "image": ""
            },
            "החייאה (PALS)": {
                "text": """## דגשי החייאה (PALS)
* **עיסויים:** עומק 1/3 בית חזה, קצב 100-120.
* **יחס:** 15:2 (שני מטפלים).
* **שוק חשמלי (VF/pVT):** 2 J/kg -> 4 J/kg -> 4-10 J/kg.
* **אדרנלין:** 0.01 מ"ג/ק"ג כל 3-5 דק'.
* [cite_start]**אמיאודורון:** 5 מ"ג/ק"ג (ב-VF עמיד) [cite: 37-43, 1031-1041].""",
                "image": ""
            }
        }
    },
    "המוטו-אונקולוגיה": {
        "icon": "🩸",
        "description": "מוצרי דם, TLS, מחלות חסר חיסוני.",
        "topics": {
            "Tumor Lysis Syndrome (TLS)": {
                "text": """## TLS - תסמונת פירוק הגידול
הרס מסיבי של תאים -> שחרור אשלגן, זרחן וחומצה אורית.
**סכנות:** אי ספיקת כליות, הפרעות קצב (היפרקלמיה).

### טיפול ומניעה
1. **הידרציה:** שטיפה אגרסיבית (ללא אשלגן!).
2. **אלופרינול:** מניעת ייצור חומצה אורית.
3. **רסבוריקז (Rasburicase):** מפרק חומצה אורית קיימת. (אסור ב-G6PD!).
4. [cite_start]טיפול בהיפרקלמיה (אינסולין+גלוקוז, קלציום, פוסיד) [cite: 719-755].""",
                "image": ""
            },
            "מוצרי דם ומתן": {
                "text": """## מתן מוצרי דם
### מנת דם (PC)
* **מינון:** 10-15 מ"ל/ק"ג.
* **זמן:** 2-4 שעות (אלא אם בשוק).
* חובה: פילטר דם, בדיקת סוג והצלבה.

### טסיות (Platelets)
* **מינון:** 5-10 מ"ל/ק"ג.
* **דגש:** לא ב-IVAC (הורס טסיות)! לתת בגרביטציה או פוש ידני עדין.

### פלזמה (FFP)
* **מינון:** 10-15 מ"ל/ק"ג.
* מכיל פקטורי קרישה. [cite_start]התוויה: DIC, דימום, מחלת כבד [cite: 603-637].""",
                "image": ""
            },
            "SCID & HLH": {
                "text": """## מצבי חסר חיסוני ודלקת
### SCID
* "ילדי בועה". חסר בתאי T ו-B.
* **סכנה:** זיהומים קטלניים (CMV, PCP).
* **טיפול:** בידוד מוחלט, IVIG, רספרים מניעתי, השתלת מח עצם.
* [cite_start]**חיסונים:** אסור לתת חיסון חי-מוחלש! [cite: 684-699].

### HLH
* שפעול יתר של מערכת החיסון (סערת ציטוקינים).
* [cite_start]**טיפול:** סטרואידים, כימותרפיה (אטופוזיד), השתלת מח עצם [cite: 700-718].""",
                "image": ""
            }
        }
    }
}

# --- מאגר שאלות מורחב (בהתאם לתוכן החדש) ---
ALL_QUESTIONS = [
    # סדציה
    {"q": "מה המינון של מידזולם (Dormicum) בוריד לילדים?", "opts": ["0.05-0.1 מ\"ג/ק\"ג", "0.5 מ\"ג/ק\"ג", "1 מ\"ג/ק\"ג", "0.01 מ\"ג/ק\"ג"], "a": "0.05-0.1 מ\"ג/ק\"ג", "topic": "מידזולם (Dormicum)", "exp": "מינון מקובל להרגעה. במינון גבוה יותר יש סכנת דיכוי נשימתי."},
    {"q": "מה היתרון העיקרי של קטמין בשוק?", "opts": ["שומר על ל\"ד ונשימה", "מוריד ל\"ד", "מונע הקאות", "מרפה שרירים"], "a": "שומר על ל\"ד ונשימה", "topic": "קטמין (Ketamine)", "exp": "קטמין הוא סימפטומימטי ולכן מעלה/שומר על ל\"ד, בניגוד לפרופופול/מידזולם שמורידים."},
    {"q": "מדוע אסור לתת טסיות דרך IVAC (משאבה)?", "opts": ["המשאבה הורסת את הטסיות", "זה גורם לזיהום", "זה מהיר מדי", "זה גורם לקרישה"], "a": "המשאבה הורסת את הטסיות", "topic": "מוצרי דם ומתן", "exp": "המנגנון המכאני של המשאבה מוחץ את הטסיות. יש לתת בגרביטציה."},
    {"q": "איזו תרופה דורשת פילטר 0.2 מיקרון ומיהול בסליין בלבד?", "opts": ["פניטואין (Epanutin)", "מידזולם", "פנטניל", "קפרה"], "a": "פניטואין (Epanutin)", "topic": "פניטואין (Epanutin/Phenytoin)", "exp": "פניטואין מתגבש בגלוקוז ודורש פילטר למניעת כניסת גבישים לוריד."},
    {"q": "מהו הטיפול התרופתי הראשון באנפילקסיס?", "opts": ["אדרנלין IM", "סטרואידים", "ונטולין", "אנטי-היסטמין"], "a": "אדרנלין IM", "topic": "אנפילקסיס", "exp": "היחיד שמציל חיים מיידית."},
    {"q": "מה המינון של בולוס נוזלים בשוק היפוולמי?", "opts": ["20 מ\"ל/ק\"ג", "50 מ\"ל/ק\"ג", "10 מ\"ל/ק\"ג", "5 מ\"ל/ק\"ג"], "a": "20 מ\"ל/ק\"ג", "topic": "שוק היפוולמי", "exp": "סטנדרט הטיפול הראשוני."},
    {"q": "מהי תופעת הלוואי המסוכנת של רסבוריקז (Rasburicase)?", "opts": ["המוליזה בחולי G6PD", "היפרקלמיה", "עצירות", "שיעול"], "a": "המוליזה בחולי G6PD", "topic": "Tumor Lysis Syndrome (TLS)", "exp": "אסור לתת לחולי G6PD מחשש לפירוק כדוריות דם."},
    {"q": "באיזה קצב נותנים שוק חשמלי ראשון ב-VF?", "opts": ["2 J/kg", "4 J/kg", "10 J/kg", "0.5 J/kg"], "a": "2 J/kg", "topic": "החייאה (PALS)", "exp": "מנה ראשונה 2 J/kg, שניה 4 J/kg."},
    {"q": "מה הטיפול המיידי בהרניאציה (קושינג) ב-TBI?", "opts": ["סליין היפרטוני/מניטול", "הורדת ראש", "מתן נוזלים", "חימום"], "a": "סליין היפרטוני/מניטול", "topic": "חבלת ראש (TBI)", "exp": "להורדת בצקת מוחית ו-ICP באופן מיידי."}
]

# --- פונקציות ניהול ---
def load_db():
    if not os.path.exists(DB_FILE):
        return DEFAULT_CONTENT
    # בפרודקשן נטען מהקובץ, כאן נחזיר דיפולט כדי לוודא שהתוכן החדש נטען
    return DEFAULT_CONTENT 

def save_db(data):
    # פונקציית דמי לשמירה
    pass

# --- הגדרת עמוד ---
st.set_page_config(page_title="אֲחָיוּת - טיפול נמרץ ילדים", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# --- CSS עיצוב ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Rubik', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #f4f7f6;
    }
    
    h1, h2, h3, h4 { color: #2c3e50; text-align: right !important; font-weight: 700; }
    p, li, div { text-align: right !important; font-size: 1.05rem; }
    
    .topic-btn {
        padding: 15px; border: 1px solid #ddd; border-radius: 10px;
        background: white; margin-bottom: 10px; text-align: right;
        transition: 0.3s; cursor: pointer;
    }
    .topic-btn:hover { background: #e3f2fd; border-color: #2196f3; }
    
    .content-card {
        background: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #3498db;
        margin-top: 20px;
    }
    
    .stProgress > div > div > div > div { background-color: #2ecc71; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: 600; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'db' not in st.session_state: st.session_state.db = load_db()
if 'user_info' not in st.session_state: st.session_state.user_info = {}
if 'completed_topics' not in st.session_state: st.session_state.completed_topics = set()
if 'scenario' not in st.session_state: st.session_state.scenario = None

# --- לוגיקה לתרחיש מתגלגל ---
def init_scenario():
    st.session_state.scenario = {
        "step": 1,
        "log": [],
        "status": {"HR": 175, "BP": "72/40", "Sat": "89%", "Condition": "Critical"},
        "score": 100
    }

# --- סרגל צד (התחברות) ---
with st.sidebar:
    st.title("🏥 אֲחָיוּת PICU")
    
    if not st.session_state.user_info:
        with st.form("auth"):
            name = st.text_input("שם מלא")
            email = st.text_input("אימייל")
            if st.form_submit_button("התחבר"):
                if email:
                    st.session_state.user_info = {"name": name, "email": email}
                    st.rerun()
    else:
        st.success(f"מחובר: {st.session_state.user_info['name']}")
        if st.button("יציאה"):
            st.session_state.user_info = {}
            st.rerun()
            
    st.markdown("---")
    
    if st.session_state.user_info:
        menu = st.radio("תפריט:", ["🏠 ראשי", "📚 מרכז למידה", "🚑 תרחיש מתגלגל", "⚙️ ניהול"])
        
        # חישוב התקדמות
        total = sum(len(c['topics']) for c in st.session_state.db.values())
        done = len(st.session_state.completed_topics)
        if total > 0:
            st.markdown(f"**התקדמות: {int(done/total*100)}%**")
            st.progress(done/total)
    else:
        menu = "login"

# --- עמודים ---

if menu == "login":
    st.title("ברוכים הבאים למערכת הלמידה")
    st.info("אנא התחבר בתפריט הצד כדי לגשת לתכנים ולסימולציות.")
    st.markdown("""
    ### מה במערכת?
    * **פרוטוקולים מלאים:** תרופות, החייאה, טראומה.
    * **סימולציות:** תרחישים קליניים בזמן אמת.
    * **מבחנים:** שאלות חזרה לכל נושא.
    """)

elif menu == "🏠 ראשי":
    st.title("מרכז ידע - טיפול נמרץ ילדים")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📢 **חדש:** נוספו פרוטוקולי סדציה ואינוטרופים מעודכנים.")
    with col2:
        st.warning("⚠️ **בטיחות:** שים לב לדילול פניטואין בסליין בלבד!")
        
    st.markdown("### נושאי לימוד עיקריים:")
    cols = st.columns(3)
    for i, (cat_name, val) in enumerate(st.session_state.db.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:white; padding:15px; border-radius:10px; border-top:4px solid #3498db; text-align:center; height:150px;">
                <div style="font-size:2rem;">{val['icon']}</div>
                <strong>{cat_name}</strong><br>
                <span style="font-size:0.8rem; color:gray;">{val.get('description','')}</span>
            </div>
            """, unsafe_allow_html=True)

elif menu == "📚 מרכז למידה":
    st.title("📚 הספרייה המקצועית")
    
    # בחירת קטגוריה
    cats = list(st.session_state.db.keys())
    sel_cat = st.selectbox("בחר נושא ראשי:", cats)
    cat_data = st.session_state.db[sel_cat]
    
    # תפריט נושאים (כפתורים)
    st.markdown("#### בחר פרוטוקול:")
    subtopics = list(cat_data['topics'].keys())
    
    # פריסת כפתורים
    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]
    
    for idx, sub in enumerate(subtopics):
        status = "✅" if sub in st.session_state.completed_topics else "⭕"
        if cols[idx % 3].button(f"{status} {sub}", use_container_width=True):
            st.session_state.curr_sub = sub
            
    # הצגת תוכן
    if 'curr_sub' in st.session_state and st.session_state.curr_sub in cat_data['topics']:
        sub = st.session_state.curr_sub
        data = cat_data['topics'][sub]
        
        st.markdown("---")
        st.markdown(f"""<div class="content-card">{data['text']}</div>""", unsafe_allow_html=True)
        
        if data.get('image'):
            st.image(data['image'], caption="תרשים", width=400)
            
        col_done, col_quiz = st.columns(2)
        with col_done:
            if st.checkbox("סיימתי ללמוד נושא זה ✅", value=(sub in st.session_state.completed_topics), key=sub):
                st.session_state.completed_topics.add(sub)
            else:
                st.session_state.completed_topics.discard(sub)
        
        with col_quiz:
            with st.expander(f"📝 בחן את עצמך על: {sub}"):
                qs = [q for q in ALL_QUESTIONS if q.get('topic') == sub]
                if qs:
                    q = random.choice(qs)
                    st.markdown(f"**{q['q']}**")
                    ans = st.radio("תשובה:", q['opts'], key=f"q_{sub}")
                    if st.button("בדוק", key=f"b_{sub}"):
                        if ans == q['a']:
                            st.success("נכון!")
                        else:
                            st.error(f"טעות. התשובה: {q['a']}")
                            st.info(q['exp'])
                else:
                    st.write("אין שאלות זמינות לנושא זה כרגע.")

elif menu == "🚑 תרחיש מתגלגל":
    st.title("🚑 סימולציה קלינית: שוק")
    
    if st.button("🔄 התחל מחדש"):
        init_scenario()
        st.rerun()
        
    if not st.session_state.scenario:
        init_scenario()
        
    s = st.session_state.scenario
    
    # מוניטור
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("דופק", s['status']['HR'])
    m2.metric("לחץ דם", s['status']['BP'])
    m3.metric("סטורציה", s['status']['Sat'])
    m4.metric("מצב", s['status']['Condition'])
    
    st.markdown("---")
    
    if s['step'] == 1:
        st.markdown("""
        ### שלב 1: קבלת חולה
        בן שנתיים, הגיע עקב ישנוניות וחום. בבדיקה: חיוור, גפיים קרות, מילוי קפילרי 4 שניות.
        **מה הפעולה הראשונה?**
        """)
        c1, c2 = st.columns(2)
        if c1.button("אקמול להורדת חום"):
            s['score'] -= 20
            s['log'].append("❌ אקמול לא דחוף בשוק. המצב הדרדר.")
            st.error("טעות. הילד בשוק!")
        
        if c2.button("חמצן + בולוס נוזלים 20 מ\"ל/ק\"ג"):
            s['status']['HR'] = 150
            s['status']['BP'] = "80/50"
            s['status']['Sat'] = "95%"
            s['log'].append("✅ טיפול ראשוני מצוין.")
            s['step'] = 2
            st.rerun()
            
    elif s['step'] == 2:
        st.markdown("""
        ### שלב 2: הערכה חוזרת
        הילד קיבל נוזלים. עדיין טכיקרדי.
        בדיקות דם: לויקוציטים 28,000, לקטט 5.
        **חשד לספסיס. מה כעת?**
        """)
        c1, c2 = st.columns(2)
        if c1.button("אנטיביוטיקה רחבת טווח + בולוס נוסף"):
            s['status']['HR'] = 120
            s['status']['BP'] = "95/60"
            s['status']['Condition'] = "Stable"
            s['log'].append("✅ ניהול ספסיס מעולה (Golden Hour).")
            s['step'] = 3
            st.rerun()
            
        if c2.button("להמתין לתרבית דם סופית"):
            s['score'] = 0
            s['status']['Condition'] = "Cardiac Arrest"
            s['log'].append("❌ עיכוב באנטיביוטיקה = תמותה.")
            s['step'] = 99
            st.rerun()
            
    elif s['step'] == 3:
        st.balloons()
        st.success(f"כל הכבוד! הצלת את הילד. ציון: {s['score']}")
        st.write("יומן אירועים:")
        for l in s['log']: st.write(l)
        
    elif s['step'] == 99:
        st.error("הילד קרס. הסימולציה נכשלה.")

elif menu == "⚙️ ניהול":
    st.title("ממשק מנהל")
    if st.session_state.user_info.get('email') == 'yishaycopp@gmail.com':
        st.success("גישה מאושרת ✔️")
        
        t1, t2 = st.tabs(["עריכה", "הוספה"])
        with t1:
            cat = st.selectbox("קטגוריה", list(st.session_state.db.keys()))
            sub = st.selectbox("נושא", list(st.session_state.db[cat]['topics'].keys()))
            txt = st.text_area("תוכן", value=st.session_state.db[cat]['topics'][sub]['text'], height=300)
            if st.button("שמור שינויים"):
                st.session_state.db[cat]['topics'][sub]['text'] = txt
                st.success("נשמר!")
    else:
        st.error("אין הרשאה.")
