import streamlit as st
import pandas as pd
import random
from docx import Document
import io

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Learning Hub", layout="wide", page_icon="🏥")

# --- הזרקת CSS לתיקון RTL, יישור כותרות לאמצע ועיצוב מקצועי ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: RTL;
        text-align: right;
    }
    
    /* יישור כותרות לאמצע */
    h1, h2, h3 {
        text-align: center !important;
        direction: RTL !important;
        color: #1e3d59;
    }
    
    /* יישור טקסט כללי לימין */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric {
        direction: RTL !important;
        text-align: right !important;
    }

    /* כפתורים מיושרים ונוחים */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #2e59a8;
        color: white;
        font-weight: bold;
    }

    /* עיצוב כרטיסיות (Cards) */
    .med-card {
        background-color: #f8f9fa;
        border-right: 6px solid #2e59a8;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* תיקון לסיידבר */
    [data-testid="stSidebar"] {
        direction: RTL !important;
        text-align: right !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- בסיס נתונים פנימי (מבוסס על ה-PDF שלך) ---
if 'points' not in st.session_state: st.session_state.points = 0
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'scenario_step' not in st.session_state: st.session_state.scenario_step = 0

# --- תפריט צדי ---
with st.sidebar:
    st.title("🏥 PICU Train & Play")
    if not st.session_state.user_name:
        name = st.text_input("שם מלא:")
        email = st.text_input("אימייל:")
        if st.button("התחל ללמוד"):
            if name: st.session_state.user_name = name; st.rerun()
    else:
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.metric("XP - ניקוד", st.session_state.points)
    
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "מרכז ידע (הסיכומים שלך)", "מבחן אישי", "התרחיש המתגלגל", "בנק תרופות", "ניהול"])

# --- דאשבורד ---
if page == "דאשבורד":
    st.header("לוח בקרה לימודי")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""<div class="med-card"><h3>💊 תרופת היום: Propranolol (דרלין)</h3><p><b>דגש PICU:</b> משמשת לטיפול ב<b>המאנגיומות</b> אינפנטיליות. <b>עובדה מעניינת:</b> התגלה במקרה שטיפול בדרלין לבעיית לב בתינוק גרם לנסיגת המאנגיומה. משמשת גם למניעת מגרנות וחרדת ביצוע.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.subheader("🏆 טבלת שיאים")
        st.table(pd.DataFrame({"שם": ["אחות אחראית", "דנה", "ערן"], "XP": [1500, 1100, 850]}))

# --- מרכז ידע (כל התוכן מה-PDF) ---
elif page == "מרכז ידע (הסיכומים שלך)":
    st.header("ספריה קלינית (מבוסס על הסיכום שלך)")
    cat = st.tabs(["המטואונקולוגיה", "שוק וספסיס", "TBI ו-ICP", "צנתרים מרכזיים"])
    
    with cat[0]:
        st.subheader("פאנציטופניה ומוצרי דם")
        st.markdown("""
        - **טסיות (PLT):** התוויה מתחת ל-10,000 או ב-HIT/TTP. **איסור מוחלט:** מתן ב-IVAC (הלחץ הורס את הטסיות).
        - **Cryoprecipitate:** מכיל פיברינוגן (פקטור I), פקטור VIII, פקטור XIII, vWF ופיברונקטין.
        - **FFP:** מנה של 200 מ"ל. סוג AB הוא ה-Universal Donor (אין בו אנטיגנים).
        - **TLS (Tumor Lysis Syndrome):** מצב חירום אונקולוגי. מאופיין בהיפרקלמיה, היפרפוספטמיה, היפוקלצמיה והיפראוריצמיה.
        """)
        
    with cat[1]:
        st.subheader("שוק (Shock) וספסיס")
        st.markdown("""
        - **שוק ספטי:** טיפול תוך שעה! מתחילים בולוסים של 10-20 מ"ל/ק"ג עד 60 מ"ל/ק"ג. 
        - **שוק קרדיוגני:** נזהרים מנוזלים! סימנים: כבד מוגדל (Liver drop), חרחורים בריאות.
        - **שוק אנפילקטי:** הטיפול הראשון והחשוב ביותר - **אפינפרין IM** (מינון 0.01mg/kg).
        """)

    with cat[2]:
        st.subheader("TBI (פגיעת ראש) ו-ICP")
        st.markdown("""
        - **CPP:** מחושב כ-MAP מינוס ICP. יעד בילדים: 40-60.
        - **Cushing Triad:** ברדיקרדיה, ירידה בנשימה, יתר לחץ דם - מעיד על לחץ תוך גולגולתי גבוה מאוד.
        - **ניהול:** הרמת ראש ל-30 מעלות, שמירה על נורמותרמיה, מתן סליין היפרטוני או מניטול להורדת בצקת.
        """)

# --- בנק תרופות (מעודכן עם סיכום התרופות) ---
elif page == "בנק תרופות":
    st.header("מאגר תרופות טיפול נמרץ ילדים")
    meds = [
        {"name": "Adrenaline (Epinephrine)", "dose": "0.01mg/kg (1:10,000)", "pearl": "במינון נמוך פועל בעיקר על רצפטורי Beta (שיפור כיווץ), במינון גבוה פועל על Alpha (כיווץ כלי דם)."},
        {"name": "Milrinone", "dose": "0.25-0.75 mcg/kg/min", "pearl": "Inodilator - משפר כיווץ ומרחיב כלי דם. חשוב לנטר לחץ דם בגלל סכנת היפוטנסיביות."},
        {"name": "Rasburicase", "dose": "0.2 mg/kg", "pearl": "תרופת הבחירה ב-TLS פעיל. מפרקת חומצה אורית קיימת (בשונה מאלופורינול שרק מונע יצירה חדשה)."},
        {"name": "Midazolam (Dormicum)", "dose": "0.1-0.2 mg/kg IV", "pearl": "סדציה קלאסית. זהירות בשילוב עם אופיואידים בגלל דיכוי נשימתי."}
    ]
    for m in meds:
        st.markdown(f"""<div class="med-card"><b>{m['name']}</b><br>מינון: {m['dose']}<br><i>{m['pearl']}</i></div>""", unsafe_allow_html=True)

# --- התרחיש המתגלגל ---
elif page == "התרחיש המתגלגל":
    st.header("🎢 סימולציה: התדרדרות מהירה")
    if st.session_state.scenario_step == 0:
        st.subheader("שלב 1: הודעה מהשטח")
        st.info("ילד בן 6 בדרך אליכם לאחר תאונת דרכים קשה. GCS 7, אישונים שווים.")
        ans = st.radio("מהי הפעולה הדחופה ביותר עם הגעתו?", ["צילום רנטגן", "אינטובציה להגנה על נתיב אוויר", "מתן מנת דם"])
        if st.button("בצע פעולה"):
            if "אינטובציה" in ans: st.success("נכון מאוד! GCS מתחת ל-8 מחייב הגנה על נתיב אוויר."); st.session_state.points += 20; st.session_state.scenario_step = 1; st.rerun()
            else: st.error("טעות. קודם כל נתיב אוויר (ABC).")
