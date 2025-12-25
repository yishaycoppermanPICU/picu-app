import streamlit as st
import random
import json
import os
import time

# --- קובץ נתונים ---
DB_FILE = "content_db.json"

# --- תוכן לימודי מלא (מבוסס על הקבצים שהעלית) ---
DEFAULT_CONTENT = {
    "מצבי חירום והחייאה": {
        "icon": "🚑",
        "topics": {
            "שוק היפוולמי (Hypovolemic)": {
                "text": """## 🩸 שוק היפוולמי / המורגי
**הגדרה:** מצב המאופיין בפרפוזיה לקויה לרקמות עקב אובדן נפח דם או נוזלים.

### 📉 סימנים קליניים לפי שלבים
1. **שלב 1 (פיצוי):** ל"ד תקין, דופק ונשימה סדירים. הילד עשוי להיות אי-שקט.
2. **שלב 2:** טכיקרדיה, טכיפניאה, מילוי קפילרי איטי, ירידה בשתן.
3. **שלב 3 (Decompensated):** ירידת לחץ דם (סימן מאוחר ומסוכן!), שינוי בהכרה.
4. **שלב 4:** קריסה. [cite_start]עור חיוור/שיש, חוסר הכרה, אנוריה [cite: 886-889].

### ⚡ טיפול בחירום
* **גישה ורידית:** רצוי שני ונפלונים עבים או IO.
* **נוזלים:** בולוס קריסטלואידים (סליין/הרטמן) **20 מ"ל/ק"ג** בהזרקה מהירה (5-10 דק').
* **הערכה חוזרת:** ניתן לחזור על הבולוס עד 3 פעמים (סה"כ 60 מ"ל/ק"ג).
* [cite_start]**שוק המורגי:** אם אין שיפור לאחר נוזלים -> מתן דם (PC) לפי 10 מ"ל/ק"ג [cite: 904-906].""",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Capillary_refill.gif/220px-Capillary_refill.gif",
                "video": ""
            },
            "ספסיס (Sepsis)": {
                "text": """## 🦠 ספסיס ושוק ספטי
**הגדרה:** זיהום + SIRS (חום, טכיקרדיה, טכיפניאה, לויקוציטוזיס).

### ⏳ הטיפול בשעה הראשונה (Golden Hour)
1. **תרביות דם:** לקחת לפני אנטיביוטיקה (אלא אם מעכב מתן).
2. [cite_start]**אנטיביוטיקה:** רחבת טווח (למשל Meropenem 20mg/kg) - **תוך שעה!** [cite: 840-843].
3. **נוזלים:** בולוס 20 מ"ל/ק"ג (עד 60 מ"ל/ק"ג).
4. **בדיקת לקטט:** מדד לפרפוזיה.

### 💉 טיפול בשוק עמיד (Refractory)
* אם אין תגובה לנוזלים -> התחלת אמינים (**נוראדרנלין** לשוק חם, **אדרנלין** לשוק קר).
* [cite_start]שוק עמיד לקטכולמינים -> לשקול **הידרוקורטיזון** [cite: 848-850].""",
                "image": "",
                "video": ""
            },
            "אנפילקסיס (Anaphylaxis)": {
                "text": """## 🐝 אנפילקסיס
תגובה אלרגית מסכנת חיים.
[cite_start]**סימנים:** אורטיקריה, נפיחות (אנגיואדמה), סטרידור, צפצופים, ירידת ל"ד[cite: 930].

### 🚀 טיפול מציל חיים (קו ראשון)
1. **אדרנלין IM:** הטיפול החשוב ביותר!
   * **מינון:** 0.01 מ"ג/ק"ג (מקס' 0.5 מ"ג).
   * **מיקום:** ירך (Vastus Lateralis).
   * [cite_start]**חזרה:** כל 5-15 דקות אם אין שיפור [cite: 936-937].

### 💊 טיפול תומך
* **נוזלים:** 20 מ"ל/ק"ג בולוס.
* **ונטולין:** אינהלציה לברונכוספאזם.
* [cite_start]**סטרואידים ואנטיהיסטמינים:** רק לאחר התייצבות (למניעת תגובה מאוחרת) [cite: 942-946].""",
                "image": "",
                "video": ""
            }
        }
    },
    "תרופות ופרוטוקולים": {
        "icon": "💊",
        "topics": {
            "אדרנלין (Adrenaline)": {
                "text": """## ⚡ אדרנלין (Epinephrine)
**אינדיקציות:** החייאה, ברדיקרדיה, אנפילקסיס, סטרידור.

### 📏 מינונים ודרך מתן
* **החייאה (IV/IO):**
  * מינון: **0.01 מ"ג/ק"ג** (0.1 מ"ל/ק"ג מדילול 1:10,000).
  * [cite_start]מקס': 1 מ"ג [cite: 38-40].
* **אנפילקסיס (IM):**
  * מינון: **0.01 מ"ג/ק"ג** (מדילול 1:1,000).
* **אינהלציה (סטרידור):**
  * [cite_start]מינון: 0.5 מ"ל/ק"ג (מקס' 5 מ"ל)[cite: 48].""",
                "image": "",
                "video": ""
            },
            "אדנוזין (SVT)": {
                "text": """## 💓 אדנוזין (Adenosine)
**אינדיקציה:** SVT (Supraventricular Tachycardia).

### ⚠️ דגש קריטי למתן
זמן מחצית חיים קצר מאוד (<10 שניות).
[cite_start]חובה לתת בשיטת **Push-Flush**: הזרקה מהירה בברז הכי קרוב ללב -> מיד שטיפה ב-5-10 מ"ל סליין[cite: 72].

### 📏 מינונים
1. **מנה ראשונה:** 0.1 מ"ג/ק"ג (מקס' 6 מ"ג).
2. [cite_start]**מנה שניה:** 0.2 מ"ג/ק"ג (מקס' 12 מ"ג) [cite: 60-62].""",
                "image": "",
                "video": ""
            },
            "אלקטרוליטים (אשלגן/מגנזיום)": {
                "text": """## 🧪 תיקון אלקטרוליטים
### אשלגן (Potassium)
* **ערכים תקינים:** 3.5-5.0 mEq/L.
* [cite_start]**חוק ברזל:** בחולים עם היפוקלמיה והיפומגנזמיה -> **יש לתקן מגנזיום תחילה!**[cite: 10].
* **קצב מתן IV:**
  * פריפרי: מקס' 10 mEq/h.
  * [cite_start]מרכזי: מקס' 40 mEq/h [cite: 31-35].

### היפרקלמיה (טיפול חירום)
1. [cite_start]**קלציום גלוקונט:** הגנה על הלב (Cardioprotection)[cite: 74].
2. [cite_start]**אינסולין + גלוקוז:** הכנסת אשלגן לתאים[cite: 528].
3. **ונטולין:** אינהלציה.""",
                "image": "",
                "video": ""
            }
        }
    },
    "טראומה ונוירולוגיה": {
        "icon": "🧠",
        "topics": {
            "חבלת ראש (TBI)": {
                "text": """## 🤕 חבלת ראש (TBI)
**יעד:** שמירה על CPP (לחץ זילוח מוחי).
`CPP = MAP - ICP`

### 🚩 טריאדה ע"ש קושינג (Cushing Triad)
סימנים לעליית ICP ולחץ על גזע המוח:
1. **יתר לחץ דם** (עם לחץ דופק רחב).
2. **ברדיקרדיה**.
3. [cite_start]**נשימה לא סדירה**[cite: 1142].

### 📉 טיפול ב-ICP מוגבר
* הרמת מראשות המיטה (30 מעלות).
* [cite_start]**סליין היפרטוני 3%:** 3-5 מ"ל/ק"ג[cite: 1152].
* [cite_start]**מניטול:** 0.5-1 גרם/ק"ג (אם אוסמולריות < 320)[cite: 1156].""",
                "image": "",
                "video": ""
            }
        }
    }
}

# --- מאגר שאלות ---
ALL_QUESTIONS = [
    {"q": "מה המינון של אדרנלין IV בהחייאה?", "opts": ["0.01 מ\"ג/ק\"ג", "0.1 מ\"ג/ק\"ג", "1 מ\"ג/ק\"ג", "0.5 מ\"ג/ק\"ג"], "a": "0.01 מ\"ג/ק\"ג", "exp": "המינון הוא 0.01 מ\"ג/ק\"ג (1:10,000). [cite_start]מינון גבוה יותר מסוכן ב-IV[cite: 40]."},
    [cite_start]{"q": "איך נותנים אדנוזין ל-SVT?", "opts": ["פוש מהיר + שטיפה", "דריפ איטי", "IM בירך", "PO"], "a": "פוש מהיר + שטיפה", "exp": "בגלל זמן מחצית חיים קצר, חובה לתת בשיטת Push-Flush[cite: 72]."},
    [cite_start]{"q": "מהו בולוס הנוזלים הראשוני בשוק?", "opts": ["20 מ\"ל/ק\"ג", "50 מ\"ל/ק\"ג", "5 מ\"ל/ק\"ג", "10 מ\"ל/ק\"ג"], "a": "20 מ\"ל/ק\"ג", "exp": "מתחילים ב-20 מ\"ל/ק\"ג קריסטלואידים תוך 5-10 דקות[cite: 906]."},
    [cite_start]{"q": "מה כוללת הטריאדה ע\"ש קושינג?", "opts": ["ברדיקרדיה, ית\"ל, נשימה לא סדירה", "טכיקרדיה, תת\"ל, חום", "כאבי ראש והקאות", "אישונים צרים"], "a": "ברדיקרדיה, ית\"ל, נשימה לא סדירה", "exp": "סימן לעליית ICP ולחץ על גזע המוח[cite: 1142]."},
    [cite_start]{"q": "בטיפול באנפילקסיס, איזו תרופה ניתנת ראשונה?", "opts": ["אדרנלין IM", "סטרואידים IV", "ונטולין", "אנטיהיסטמין"], "a": "אדרנלין IM", "exp": "הטיפול היחיד המציל חיים מיידית ומונע קריסה[cite: 933]."},
    [cite_start]{"q": "מה תפקיד הקלציום בהיפרקלמיה?", "opts": ["הגנה על הלב", "הורדת אשלגן", "השתנה מרובה", "הרגעת המטופל"], "a": "הגנה על הלב", "exp": "קלציום מייצב את הממברנה ומונע הפרעות קצב, אך לא מוריד אשלגן[cite: 74]."}
]

# --- פונקציות ניהול ---
def load_db():
    if not os.path.exists(DB_FILE):
        return DEFAULT_CONTENT
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- הגדרת עמוד ---
st.set_page_config(page_title="אֲחָיוּת - למידה חכמה", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# --- CSS לעיצוב יוקרתי (Cards, Icons, RTL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Rubik', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #f0f2f6;
    }
    
    /* כותרות מעוצבות */
    h1, h2, h3 { color: #0d47a1; font-weight: 700; text-align: right !important; }
    p, li, div { text-align: right !important; font-size: 1.1rem; }
    
    /* כרטיסיות (Cards) לתפריט */
    .topic-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s;
        border-top: 5px solid #1976d2;
        cursor: pointer;
        margin-bottom: 20px;
    }
    .topic-card:hover { transform: translateY(-5px); }
    
    /* כרטיסיית תוכן */
    .content-box {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border-right: 6px solid #0d47a1;
        margin-top: 20px;
    }
    
    /* סרגל התקדמות */
    .stProgress > div > div > div > div { background-color: #4caf50; }
    
    /* כפתורים */
    .stButton button { width: 100%; border-radius: 10px; font-weight: bold; }
    
    /* הסתרת אלמנטים מיותרים */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'db' not in st.session_state: st.session_state.db = load_db()
if 'completed_topics' not in st.session_state: st.session_state.completed_topics = set()
if 'completed_questions' not in st.session_state: st.session_state.completed_questions = set()

# --- חישוב התקדמות ---
total_topics = sum(len(cat['topics']) for cat in st.session_state.db.values())
completed_count = len(st.session_state.completed_topics)
progress = completed_count / total_topics if total_topics > 0 else 0

# --- סרגל צד ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/nurse-male--v1.png", width=80)
    st.markdown(f"### 📊 התקדמות: {int(progress*100)}%")
    st.progress(progress)
    st.markdown("---")
    menu = st.radio("ניווט:", ["🏠 דף הבית", "📖 מרכז למידה", "📝 מבחן ידע"])

# --- עמודים ---

if menu == "🏠 דף הבית":
    st.title("אֲחָיוּת - טיפול נמרץ ילדים")
    st.subheader("מערכת למידה אינטראקטיבית לצוות הרפואי")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="topic-card"><h3>🚑 מצבי חירום</h3><p>שוק, החייאה וטראומה</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="topic-card"><h3>💊 תרופות</h3><p>מינונים, דגשים ופרוטוקולים</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="topic-card"><h3>📝 מבחנים</h3><p>תרגול ידע ובחינה עצמית</p></div>""", unsafe_allow_html=True)

    st.info(f"עד כה השלמת **{completed_count}** מתוך **{total_topics}** נושאי לימוד.")

elif menu == "📖 מרכז למידה":
    st.title("📖 מרכז למידה")
    
    # בחירת קטגוריה ראשית (טאבים)
    categories = list(st.session_state.db.keys())
    selected_cat = st.selectbox("בחר נושא ראשי:", categories)
    
    current_cat_data = st.session_state.db[selected_cat]
    
    # הצגת תתי הנושאים ככרטיסיות בחירה (ולא רשימה)
    st.markdown(f"### {current_cat_data.get('icon', '')} נושאים בפרק זה:")
    
    subtopics = list(current_cat_data['topics'].keys())
    
    # יצירת "גריד" של כפתורים לנושאים
    cols = st.columns(3)
    for i, sub in enumerate(subtopics):
        is_done = "✅" if sub in st.session_state.completed_topics else "⭕"
        if cols[i % 3].button(f"{is_done} {sub}", key=sub):
            st.session_state.selected_subtopic = sub

    # הצגת התוכן הנבחר
    if 'selected_subtopic' in st.session_state and st.session_state.selected_subtopic in subtopics:
        selected_sub = st.session_state.selected_subtopic
        data = current_cat_data['topics'][selected_sub]
        
        st.markdown("---")
        st.markdown(f"""<div class="content-box">{data['text']}</div>""", unsafe_allow_html=True)
        
        if data.get('image'): st.image(data['image'], width=400)
        
        # כפתור סימון "סיימתי"
        if st.checkbox("סיימתי ללמוד נושא זה ✅", value=(selected_sub in st.session_state.completed_topics), key=f"chk_{selected_sub}"):
            st.session_state.completed_topics.add(selected_sub)
        else:
            st.session_state.completed_topics.discard(selected_sub)

elif menu == "📝 מבחן ידע":
    st.title("📝 מבחן ידע")
    st.write("שאלות אקראיות מתוך מאגר הידע.")
    
    if 'quiz_pool' not in st.session_state:
        st.session_state.quiz_pool = random.sample(ALL_QUESTIONS, 5)

    if st.button("🔄 הגרל שאלות חדשות"):
        st.session_state.quiz_pool = random.sample(ALL_QUESTIONS, 5)
        st.rerun()

    score = 0
    with st.form("quiz"):
        for i, q in enumerate(st.session_state.quiz_pool):
            q_key = f"q_{i}_{q['q']}"
            is_solved = q_key in st.session_state.completed_questions
            
            st.markdown(f"**{i+1}. {q['q']}**")
            ans = st.radio("בחר תשובה:", q['opts'], key=q_key, index=None)
            st.markdown("---")
            
            if ans == q['a']:
                score += 1

        if st.form_submit_button("הגש מבחן 🏁"):
            st.success(f"הציון שלך: {score}/5")
            for i, q in enumerate(st.session_state.quiz_pool):
                q_key = f"q_{i}_{q['q']}"
                user_ans = st.session_state.get(q_key)
                if user_ans == q['a']:
                    st.session_state.completed_questions.add(q_key)
                    st.caption(f"שאלה {i+1}: ✅ נכון!")
                else:
                    st.error(f"שאלה {i+1}: ❌ טעות. התשובה היא: {q['a']}")
                    st.info(f"הסבר: {q['exp']}")
