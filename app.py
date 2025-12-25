import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. אתחול מוקדם (חובה למנועAttributeError) ---
if 'u_score' not in st.session_state: st.session_state.u_score = 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 2. ממשק Manus Pro + RTL (בקרת איכות עיצובית) ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    /* יישור לימין אבסולוטי כולל כותרות צד ותפריטים */
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* מרכוז כותרות Manus */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; margin-top: 0px; }
    
    /* ניקוי שטח לבן עליון */
    .block-container { padding-top: 2rem !important; }

    /* כרטיסיות מידע מקצועיות */
    .clinical-card {
        background: white; border-radius: 16px; padding: 40px; margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8;
        line-height: 2.2; font-size: 20px; color: #1e293b;
    }

    /* מוניטור ICU */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; direction: ltr; text-align: left;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4); margin: 20px 0;
    }
    .mon-val { font-size: 45px; font-weight: bold; }
    .hr { color: #f87171; } .bp { color: #fbbf24; } .spo2 { color: #22d3ee; }

    /* יישור גלגלות (Dropdowns) */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }
    
    /* כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 55px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. לוגיקת מסד נתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points, email):
    db = get_db()
    if email in db['email'].values:
        idx = db[db['email'] == email].index[0]
        db.at[idx, 'score'] = int(db.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=db)
        st.session_state.u_score = int(db.at[idx, 'score'])

# --- 4. מערכת כניסה חסינת תקלות (בקרת איכות טכנית) ---
if not st.session_state.logged_in:
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("##### ברוכים הבאים למערכת הלמידה המרכזית")
        
        # בלם זעזועים: אם גוגל לא מגיב, עוברים לידני כדי שלא תהיה תקוע
        try:
            st.login("google")
            if st.user.is_logged_in:
                st.session_state.logged_in = True
                st.session_state.u_name, st.session_state.u_email = st.user.name, st.user.email
                st.rerun()
        except:
            st.info("כניסה לצוות הרשום (מצב גיבוי):")
            n = st.text_input("שם מלא:")
            m = st.text_input("אימייל:")
            if st.button("כניסה"):
                if n and m: 
                    st.session_state.logged_in = True
                    st.session_state.u_name, st.session_state.u_email = n, m
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# טעינת XP לאחר כניסה
if st.session_state.u_score == 0:
    db = get_db()
    if st.session_state.u_email in db['email'].values:
        st.session_state.u_score = int(db.loc[db['email'] == st.session_state.u_email, 'score'].values[0])

# --- 5. תפריט ואתר ---
with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.u_name}")
    st.metric("XP ניקוד למידה", st.session_state.u_score)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "פרוטוקולים מלאים", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה"): st.logout()

# --- 6. תוכן קליני מלא (בקרת איכות תוכנית) ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה ושיאים</h1>", unsafe_allow_html=True)
    db = get_db().sort_values(by="score", ascending=False).head(10)
    st.table(db[["name", "score"]].rename(columns={"name": "שם", "score": "ניקוד"}))

elif page == "פרוטוקולים מלאים":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    with t1: 
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ירידה משמעותית בטרומבוציטופניה (PLT), נויטרופניה ואנמיה.<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור IVAC!</b> الהלחץ מועך את הטסיות. <br>
        ● <b>FFP:</b> תורם אוניברסלי סוג AB. ● <b>Cryoprecipitate:</b> מקורו בפלסמה. מכיל פיברינוגן, פקטור VIII, XIII, vWF.</div>""", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול וזיהוי שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! SIRS: חום, טכיקרדיה, טכיפניאה. בולוסים 20ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש, כבד מוגדל (Liver drop). <b>להימנע מנוזלים המעמיסים על הלב!</b></div>""", unsafe_allow_html=True)
    with t3:
        st.markdown("""<div class='clinical-card'><h3>חבלות ראש (TBI) וניהול ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה לצורך הגנה על נתיב אוויר. <br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד (סימן להרניאציה).</div>""", unsafe_allow_html=True)

elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות - גלגלת בחירה</h1>", unsafe_allow_html=True)
    meds = {"א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: פלאש מהיר", "אטרופין: ברדיקרדיה"], "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg"]}
    col_a, col_b = st.columns(2)
    with col_a: letter = st.selectbox("בחר אות:", sorted(meds.keys()))
    with col_b: drug = st.selectbox("בחר תרופה:", meds[letter])
    st.markdown(f"<div class='clinical-card'>{drug}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: התדרדרות חיה</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-val hr'>HR: 196 | BP: 68/40 | SpO2: 89%</div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! +30 XP"); update_xp(30, st.session_state.u_email); st.session_state.sc_idx = 1; st.rerun()
