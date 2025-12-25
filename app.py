import streamlit as st
import pandas as pd
import random
from docx import Document
import io

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Learning Hub", layout="wide", page_icon="🏥")

# --- הזרקת CSS ל-RTL ועיצוב רפואי ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stHeader { direction: RTL !important; text-align: right !important; }
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; }
    .med-card { background-color: #f8f9fa; border-right: 5px solid #2e59a8; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2e59a8; color: white; }
    div[data-testid="stMetricValue"] { text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול נתונים (Session State) ---
if 'points' not in st.session_state: st.session_state.points = 0
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'scenario_step' not in st.session_state: st.session_state.scenario_step = 0
if 'db_questions' not in st.session_state:
    st.session_state.db_questions = [
        {"cat": "המטולוגיה", "q": "מדוע אין לתת טרומבוציטים ב-IVAC?", "a": "הלחץ המכני הורס את התאים", "options": ["מהירות נמוכה", "הלחץ המכני הורס את התאים", "הפילטר נסתם"]},
        {"cat": "TBI", "q": "מהו ה-GCS שמתחתיו נבצע אינטובציה?", "a": "8", "options": ["10", "8", "12"]},
        {"cat": "DKA", "q": "מהו הסיבוך המפחיד ביותר בתיקון מהיר של DKA בילדים?", "a": "בצקת מוחית", "options": ["היפוגליקמיה", "בצקת מוחית", "אי ספיקת כליות"]}
    ]

# --- תפריט צדי ---
with st.sidebar:
    st.title("🏥 PICU Train & Play")
    if not st.session_state.user_name:
        st.subheader("כניסת משתמש")
        name = st.text_input("שם מלא:")
        email = st.text_input("אימייל:")
        if st.button("התחל ללמוד"):
            if name and email:
                st.session_state.user_name = name
                st.rerun()
    else:
        st.success(f"שלום, **{st.session_state.user_name}**")
        st.metric("XP - ניקוד מצטבר", st.session_state.points)
    
    st.divider()
    page = st.radio("תפריט ראשי:", ["דאשבורד", "מרכז ידע (Content)", "מבחן אישי", "תרחיש מתגלגל 🎢", "מאגר תרופות", "ניהול (Admin)"])

# --- דאשבורד ---
if page == "דאשבורד":
    st.header("לוח בקרה יומי")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""<div class="med-card"><h3>💊 תרופת היום: Propranolol</h3><p><b>עובדה מעניינת:</b> ב-PICU משמשת לטיפול ב<b>המאנגיומות</b>. היא גורמת לנסיגת כלי דם ע"י עיכוב גורמי צמיחה (VEGF). בתחומים אחרים משמשת למניעת מגרנות וחרדת ביצוע!</p></div>""", unsafe_allow_html=True)
    with col2:
        st.subheader("🏆 טבלת שיאים")
        st.table(pd.DataFrame({"שם": ["אחות אחראית", "דנה", "יוסי"], "XP": [1500, 1200, 900]}))

# --- מרכז ידע ---
elif page == "מרכז ידע (Content)":
    st.header("ספריה קלינית (UpToDate)")
    topic = st.selectbox("בחר נושא:", ["המטואונקולוגיה", "TBI ו-ICP", "שוק וספסיס", "DKA"])
    if topic == "המטואונקולוגיה":
        st.info("דגשים למתן מוצרי דם")
        st.write("- **טסיות:** מינון 5mg/kg. תמיד מוקרן. לא ב-IVAC.")
        st.write("- **קריו:** לשימוש במחסור בפיברינוגן. מכיל פקטור 8 ו-13.")
    # כאן ניתן להוסיף עוד תוכן מה-PDF בקלות

# --- מנוע מבחנים (צד א' וצד ב') ---
elif page == "מבחן אישי":
    st.header("מערכת מבחנים")
    mode = st.radio("סוג מבחן:", ["מבחן נושאי", "מבחן מעורב (Mixed)"])
    num_q = st.slider("כמות שאלות:", 1, 10, 5)
    
    if st.button("התחל מבחן"):
        questions = st.session_state.db_questions
        if mode == "מבחן נושאי":
            # לוגיקה לסינון לפי נושא (למשל המטולוגיה)
            pass
        random.shuffle(questions)
        for i in range(min(num_q, len(questions))):
            st.subheader(f"שאלה {i+1}")
            q = questions[i]
            user_ans = st.radio(q["q"], q["options"], key=f"q_{i}")
            if st.button(f"בדוק שאלה {i+1}", key=f"btn_{i}"):
                if user_ans == q["a"]:
                    st.success("נכון!")
                    st.session_state.points += 10
                else:
                    st.error(f"טעות. התשובה הנכונה: {q['a']}")

# --- תרחיש מתגלגל ---
elif page == "תרחיש מתגלגל 🎢":
    st.header("סימולציית תרחיש מתגלגל")
    scenario = st.selectbox("בחר תרחיש:", ["קבלת ילד לאחר T&A", "התדרדרות המטולוגית (TLS)"])
    
    if scenario == "קבלת ילד לאחר T&A":
        st.subheader("שלב 1: הכנת החדר")
        q1 = st.multiselect("מה חייב להיות מוכן בחדר לקבלת ילד לאחר ניתוח שקדים (T&A)?", ["מקור חמצן", "סקשן עובד", "ערכת נקז חזה", "מנת דם O-Neg"])
        if st.button("בדוק מוכנות"):
            if "מקור חמצן" in q1 and "סקשן עובד" in q1:
                st.success("מצוין! סקשן הוא קריטי במקרה של דימום פוסט-אופ כדי למנוע אספירציה.")
                st.session_state.points += 20
        
        st.subheader("שלב 2: סימני אזהרה")
        st.warning("הילד הגיע, הוא בולע רוק בתדירות גבוהה מאוד ונראה חיוור.")
        q2 = st.radio("מה החשד המיידי שלך?", ["כאב לא מאוזן", "דימום פעיל בלוע", "תגובה לחומרי הרדמה"])
        if q2 == "דימום פעיל בלוע":
            st.success("נכון! בליעה מרובה היא סימן קלאסי לדימום פוסט-אופ בילדים.")

# --- מאגר תרופות ---
elif page == "מאגר תרופות":
    st.header("בנק תרופות PICU")
    meds = {
        "Adrenaline": "מינון החייאה: 0.01mg/kg. עובדה: במינונים נמוכים משפיע בעיקר על בטא, במינונים גבוהים על אלפא.",
        "Dexamethasone": "ב-PICU משמש רבות למניעת סטרידור לאחר אקסטובציה (Post-extubation stridor).",
        "Milrinone": "Inodilator - משפר כיווץ ומרחיב כלי דם. זהירות מהיפוטנסיביות!"
    }
    for m, d in meds.items():
        st.markdown(f"""<div class="med-card"><b>{m}</b><br>{d}</div>""", unsafe_allow_html=True)

# --- ניהול (Admin) ---
elif page == "ניהול (Admin)":
    pwd = st.text_input("סיסמת מנהל:", type="password")
    if pwd == "PICU123":
        st.success("גישת מנהל אושרה")
        tab_admin1, tab_admin2 = st.tabs(["העלאת שאלות", "רשימת תפוצה"])
        with tab_admin1:
            file = st.file_uploader("העלה קובץ Word עם שאלות", type="docx")
            if file:
                st.info("מנתח קובץ... (כאן תבוא לוגיקת ה-docx)")
        with tab_admin2:
            st.write("מיילים רשומים: admin@hospital.org, user1@picu.com")
