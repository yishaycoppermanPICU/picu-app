import streamlit as st
import pandas as pd
import random
from datetime import datetime
import time
import json
import os

# --- קובץ נתונים ---
DB_FILE = "content_db.json"

# --- תוכן מלא (מועתק מהקבצים שלך) ---
DEFAULT_CONTENT = {
    "מצבי חירום והחייאה": {
        "שוק (Shock) - כללי": {
            "text": """## גישה לילד בשוק (Shock)
**הגדרה:** מצב פתופיזיולוגי דינמי ולא יציב המאופיין בפרפוזיה לקויה לרקמות.

### סוגי שוק עיקריים בילדים:
1. **שוק היפוולמי (Hypovolemic):** אובדן נוזלים/דם.
2. **שוק חלוקתי (Distributive):** ספסיס, אנפילקסיס, נוירוגני.
3. **שוק קרדיוגני (Cardiogenic):** כשל לבבי.
4. **שוק חסימתי (Obstructive):** טמפונדה, טנשן פנאומוטורקס.

### סימנים קליניים לפי שלבים:
* **שלב 1 (פיצוי):** ל"ד תקין, מילוי קפילרי תקין, דופק ונשימה סדירים. הילד עשוי להיות מעט עצבני.
* **שלב 2:** ל"ד תקין/נמוך, מילוי קפילרי איטי, זיעה קרה, טכיקרדיה, טכיפניאה, ירידה בשתן.
* **שלב 3 (Decompensated):** ל"ד סיסטולי צונח (Late Sign!), מילוי קפילרי איטי מאוד, שינוי במצב הכרה.
* **שלב 4:** ל"ד נמוך מאוד, עור חיוור/שיש, חוסר הכרה/קומה, אנוריה.
* **שלב 5:** ברדיקרדיה/אסיסטולה.

### טיפול ראשוני (כללי):
1. **נתיב אוויר (A):** חמצן 100%, אינטובציה במידת הצורך (קטמין בשוק לא יציב).
2. **נוזלים (C):** בולוס קריסטלואידים (סליין/הרטמן) **20 מ"ל/ק"ג** תוך 5-10 דקות.
   * ניתן לחזור עד 3 פעמים (סה"כ 60 מ"ל/ק"ג) תוך הערכה מחדש.
   * *חריג:* בשוק קרדיוגני - בזהירות! (5-10 מ"ל/ק"ג).""",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Shock_types.png/640px-Shock_types.png", # תמונה להמחשה
            "video": ""
        },
        "ספסיס (Sepsis)": {
            "text": """## ספסיס ושוק ספטי (Sepsis & Septic Shock)
**הגדרה:** זיהום (חשוד/מאוכחן) + תגובה דלקתית סיסטמית (SIRS).

### קריטריונים ל-SIRS (שניים או יותר):
1. חום > 38.5 או < 36.
2. טכיקרדיה (או ברדיקרדיה בתינוקות).
3. טכיפניאה.
4. לויקוציטוזיס או לויקופניה.

### "חבילת הטיפול" בשעה הראשונה (The Golden Hour):
1. **גישה ורידית/IO:** תוך דקות.
2. **תרביות דם:** לפני אנטיביוטיקה (אם לא מעכב משמעותית).
3. **אנטיביוטיקה רחבת טווח:** (למשל Meropenem 20mg/kg) - *לא לעכב!*
4. **נוזלים:** בולוס 20 מ"ל/ק"ג (עד 60 מ"ל/ק"ג) עד לשיפור פרפוזיה.
5. **בדיקת לקטט:** מדד לפרפוזיה רקמתית.

### טיפול בשוק עמיד לנוזלים (Refractory Shock):
* **שוק קר (Cold Shock):** פרפוזיה ירודה, ל"ד נמוך -> **אדרנלין** (Dose: 0.05-0.3 mcg/kg/min).
* **שוק חם (Warm Shock):** דפקים הולמים, ל"ד נמוך (הרחבת כלי דם) -> **נוראדרנלין**.
* **חשד לאי ספיקת אדרנל:** הידרוקורטיזון.""",
            "image": "",
            "video": ""
        },
        "אנפילקסיס (Anaphylaxis)": {
            "text": """## אנפילקסיס
תגובה אלרגית מסכנת חיים. הופעה מהירה של תסמינים עוריים (אורטיקריה) + נשימתיים/קרדיוווסקולריים.

### טיפול מיידי (Life Saving):
1. **אדרנלין (IM):** הטיפול היחיד שמוכח כמציל חיים מיידית.
   * **מינון:** 0.01 מ"ג/ק"ג (תמיסה 1:1,000). מקסימום 0.5 מ"ג.
   * **מיקום:** ירך (Vastus Lateralis).
   * **חזרה:** כל 5-15 דקות אם אין שיפור.
2. **השכבה:** הרמת רגליים (Trendelenburg) לשיפור החזר ורידי.
3. **חמצן:** 100%.
4. **נוזלים:** 20 מ"ל/ק"ג בולוס מהיר.

### טיפול קו שני (לאחר התייצבות):
* **ונטולין (אינהלציה):** לברונכוספאזם.
* **סטרואידים (IV/PO):** למניעת תגובה מאוחרת (Biphasic).
* **אנטיהיסטמינים:** להקלת גרד/פריחה.""",
            "image": "",
            "video": ""
        }
    },
    "תרופות (פרוטוקול מחלקה)": {
        "אדרנלין (Adrenaline)": {
            "text": """## אדרנלין (Epinephrine)
אינדיקציות: החייאה (Asystole, PEA, VF), ברדיקרדיה סימפטומטית, אנפילקסיס, סטרידור (אינהלציה).

### מינונים ודרך מתן:
* **החייאה (IV/IO):**
  * מינון: **0.01 מ"ג/ק"ג** (0.1 מ"ל/ק"ג מתמיסת 1:10,000).
  * מקסימום: 1 מ"ג.
  * תדירות: כל 3-5 דקות.
* **אנפילקסיס (IM):**
  * מינון: **0.01 מ"ג/ק"ג** (תמיסת 1:1,000).
* **אינהלציה (סטרידור):**
  * מינון: 0.5 מ"ל/ק"ג (מקס' 5 מ"ל).
* **דריפ מתמשך (Inotropes):**
  * טווח: 0.05 - 1.0 mcg/kg/min.

> **שים לב:** קיים בלבול נפוץ בין ריכוזים (1:1,000 מול 1:10,000). בהחייאה משתמשים בדילול הגבוה!""",
            "image": "",
            "video": ""
        },
        "אדנוזין (Adenosine)": {
            "text": """## אדנוזין
אינדיקציה: **SVT** (Supraventricular Tachycardia).

### אופן מתן (קריטי!):
* זמן מחצית חיים קצר מאוד (<10 שניות).
* חובה לתת בשיטת **Push-Flush**: הזרקה מהירה מאוד בברז הקרוב ביותר ללב, ומיד אחריה שטיפה בולוס של 5-10 מ"ל סליין.

### מינונים:
1. **מנה ראשונה:** 0.1 מ"ג/ק"ג (מקסימום 6 מ"ג).
2. **מנה שניה:** 0.2 מ"ג/ק"ג (מקסימום 12 מ"ג).

*תופעות לוואי מיידיות:* תחושת "בעיטה" בחזה, הסמקה, אסיסטולה רגעית במוניטור (מפחיד אך צפוי).""",
            "image": "",
            "video": ""
        },
        "אלקטרוליטים (אשלגן/מגנזיום)": {
            "text": """## תיקון אלקטרוליטים
### אשלגן (Potassium)
* **ערכים תקינים:** 3.5-5.0 mEq/L.
* **חוק הברזל:** בחולים עם היפוקלמיה והיפומגנזמיה -> **יש לתקן מגנזיום תחילה!** (אחרת האשלגן יופרש בשתן ולא יעלה).
* **קצב מתן IV:**
  * פריפרי: מקס' 10 mEq/h.
  * מרכזי: מקס' 40 mEq/h (או 1 mEq/kg/h). תמיד במוניטור!

### מגנזיום (Magnesium Sulfate)
* אינדיקציות: היפומגנזמיה, Torsades de Pointes, אסטמה קשה (IV).
* מינון לאסטמה: 25-50 מ"ג/ק"ג (מקס' 2 גרם) במשך 20 דקות.""",
            "image": "",
            "video": ""
        }
    },
     "טראומה": {
        "חבלת ראש (TBI)": {
            "text": """## חבלת ראש טראומטית (TBI)
**מדד גלזגו (GCS):**
* קל: 13-15
* בינוני: 9-12
* קשה: < 9 (אינדיקציה לאינטובציה להגנה על נתיב אוויר).

### לחץ תוך גולגולתי (ICP):
המטרה: שמירה על לחץ זילוח מוחי (**CPP**).
הנוסחה: **CPP = MAP - ICP**.
בילדים נשאף ל-CPP מעל 40-50.

### טריאדה ע"ש קושינג (Cushing Triad):
סימנים לעליית ICP ולחץ על גזע המוח (Pre-herniation):
1. **יתר לחץ דם** (עם לחץ דופק רחב).
2. **ברדיקרדיה**.
3. **נשימה לא סדירה** (Cheyne-Stokes).

### טיפול ב-ICP מוגבר:
1. הרמת מראשות המיטה (30 מעלות).
2. ראש במנח ישר (לא חוסם ורידי צוואר).
3. סליין היפרטוני 3% (3-5 מ"ל/ק"ג) או מניטול.
4. היפרוונטילציה מתונה (PCO2 30-35) - רק במצב חירום של הרניאציה!""",
            "image": "",
            "video": ""
        }
    }
}

# --- פונקציות ניהול ---
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONTENT, f, ensure_ascii=False, indent=4)
        return DEFAULT_CONTENT
    else:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- הגדרת עמוד ---
st.set_page_config(page_title="אֲחָיוּת - עם ישי קופרמן", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# --- CSS עיצוב ויישור לימין ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Rubik', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #f4f6f9;
    }
    
    /* כותרות */
    h1, h2, h3, h4, h5 {
        font-family: 'Rubik', sans-serif;
        text-align: right !important;
        color: #0d47a1; /* כחול כהה רפואי */
        font-weight: 700;
        margin-top: 10px;
    }
    
    h1 { font-size: 2.5rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }
    h2 { font-size: 1.8rem; color: #1565c0; border-right: 5px solid #ffca28; padding-right: 10px; margin-top: 30px;}
    h3 { font-size: 1.4rem; color: #1976d2; margin-top: 20px;}
    
    /* טקסט גוף */
    p, div, span, li {
        font-size: 1.1rem;
        line-height: 1.6;
        text-align: right !important;
        direction: rtl !important;
        color: #333;
    }
    
    /* רשימות */
    ul {
        direction: rtl !important;
        text-align: right !important;
        margin-right: 20px !important;
    }
    li { margin-bottom: 5px; }

    /* כרטיסיית תוכן */
    .content-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-top: 5px solid #0d47a1;
        margin-top: 20px;
        margin-bottom: 40px;
    }
    
    /* טיפים ואזהרות */
    .stAlert { direction: rtl; text-align: right; font-weight: bold; }
    
    /* הסתרת אלמנטים מיותרים */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* כפתורים וטפסים */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div { direction: rtl; text-align: right; }
    
</style>
""", unsafe_allow_html=True)

# --- ניהול Session ---
if 'content_db' not in st.session_state: st.session_state.content_db = load_data()
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- סרגל צד ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/nurse-male--v1.png", width=80)
    st.title("פרופיל אישי")
    
    if not st.session_state.user_info:
        with st.form("login"):
            name = st.text_input("שם מלא")
            email = st.text_input("אימייל")
            if st.form_submit_button("כניסה למערכת"):
                st.session_state.user_info = {"name": name, "email": email}
                st.rerun()
    else:
        st.success(f"מחובר: {st.session_state.user_info['name']}")
        if st.button("יציאה"):
            st.session_state.user_info = {}
            st.rerun()
    
    st.markdown("---")
    menu = st.radio("ניווט:", ["🏠 דף הבית", "📚 פרוטוקולים וחומר לימוד", "⚙️ ניהול תוכן"])

# --- עמודים ---

if menu == "🏠 דף הבית":
    # כותרת ראשית מעוצבת
    st.markdown("<h1 style='text-align: center; color: #0d47a1;'>אֲחָיוּת - עם ישי קופרמן</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #546e7a; margin-top:0;'>טיפול נמרץ ילדים - PICU</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_text, col_img = st.columns([2, 1])
    with col_text:
        st.markdown("""
        <div class="content-box" style="padding: 20px;">
        <strong>ברוכים הבאים למערכת הלמידה והפרוטוקולים.</strong><br>
        המערכת מרכזת את כל המידע הקליני הדרוש למשמרת בטיפול נמרץ:
        <ul>
            <li>🚑 <strong>החייאה ושוק:</strong> אלגוריתמים ומינונים.</li>
            <li>💊 <strong>תרופות:</strong> פרוטוקולי מתן, דילולים ודגשים.</li>
            <li>🧠 <strong>טראומה:</strong> TBI וניטור נוירולוגי.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_img:
        st.info("💡 **טיפ יומי:**\nבחשד לשוק ספטי, יש לתת אנטיביוטיקה תוך שעה (Golden Hour) ולא לחכות לתוצאות מעבדה.")
        st.warning("⚠️ **בטיחות:**\nאדנוזין נותנים ב-Push מהיר בלבד, בברז הכי קרוב למטופל!")

elif menu == "📚 פרוטוקולים וחומר לימוד":
    st.title("📚 הספרייה המקצועית")
    
    db = st.session_state.content_db
    topics = list(db.keys())
    
    if not topics:
        st.error("המאגר ריק. יש להזין תוכן בממשק הניהול.")
    else:
        # פריסה של 2 עמודות: תפריט (צר) ותוכן (רחב)
        col_menu, col_content = st.columns([1, 3])
        
        with col_menu:
            st.markdown("### נושא ראשי")
            selected_topic = st.selectbox("בחר קטגוריה:", topics, label_visibility="collapsed")
            
            st.markdown("### תת-נושא")
            subtopics = list(db[selected_topic].keys())
            selected_sub = st.radio("בחר פרוטוקול:", subtopics)
        
        with col_content:
            data = db[selected_topic][selected_sub]
            
            # --- אזור התוכן המעוצב ---
            st.markdown(f"""
            <div class="content-box">
            {data['text']}
            </div>
            """, unsafe_allow_html=True) # כאן מוזרק המרקדאון של התוכן
            
            # הצגת מדיה אם קיימת
            if data.get('image'):
                st.image(data['image'], caption="תרשים/תמונה להמחשה", use_container_width=True)
            if data.get('video'):
                st.video(data['video'])

elif menu == "⚙️ ניהול תוכן":
    st.title("ממשק ניהול (Admin)")
    
    if st.session_state.user_info.get('email') != 'yishaycopp@gmail.com':
        st.error("⛔ גישה למנהלים בלבד.")
    else:
        db = st.session_state.content_db
        tab1, tab2 = st.tabs(["עריכה", "הוספה"])
        
        with tab1:
            if db:
                main = st.selectbox("נושא ראשי:", list(db.keys()))
                sub = st.selectbox("תת-נושא:", list(db[main].keys()))
                curr = db[main][sub]
                
                with st.form("edit"):
                    txt = st.text_area("תוכן (Markdown)", value=curr['text'], height=400)
                    img = st.text_input("תמונה (URL)", value=curr.get('image',''))
                    vid = st.text_input("וידאו (URL)", value=curr.get('video',''))
                    if st.form_submit_button("שמור שינויים"):
                        st.session_state.content_db[main][sub] = {"text": txt, "image": img, "video": vid}
                        save_data(st.session_state.content_db)
                        st.success("עודכן!")
                        st.rerun()
            else:
                st.warning("אין תוכן.")
                
        with tab2:
            new_main = st.text_input("נושא ראשי חדש (או השאר ריק כדי להוסיף לקיים)")
            exist_main = st.selectbox("או בחר קיים:", list(db.keys()) if db else [])
            
            with st.form("add"):
                new_sub = st.text_input("שם הפרוטוקול החדש")
                new_txt = st.text_area("תוכן הפרוטוקול")
                if st.form_submit_button("הוסף"):
                    target = new_main if new_main else exist_main
                    if target and new_sub:
                        if target not in st.session_state.content_db:
                            st.session_state.content_db[target] = {}
                        st.session_state.content_db[target][new_sub] = {"text": new_txt, "image": "", "video": ""}
                        save_data(st.session_state.content_db)
                        st.success("נוסף!")
                        st.rerun()
