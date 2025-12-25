import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- 1. אתחול מוקדם למניעת קריסות (Attribute Errors) ---
if 'u_score' not in st.session_state: st.session_state.u_score = 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0

# --- 2. ממשק Manus Pro + ICU Monitor (RTL מוחלט) ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* מניעת שטח לבן ומרכוז כותרות */
    .block-container { padding-top: 1rem !important; }
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; margin-top: 0px; }
    
    /* כרטיסיות Manus - תוכן מלא מה-PDF */
    .clinical-card {
        background: white; border-radius: 16px; padding: 40px; margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8;
        line-height: 2.2; font-size: 20px; color: #1e293b;
    }

    /* מוניטור ICU דיגיטלי */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; direction: ltr; text-align: left;
        box-shadow: inset 0 0 15px #000, 0 10px 25px rgba(0,0,0,0.4); margin: 20px 0;
    }
    .mon-val { font-size: 45px; font-weight: bold; }
    .hr { color: #f87171; } .bp { color: #fbbf24; } .spo2 { color: #22d3ee; }

    /* התאמת גלגלות לימין */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }

    /* כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 55px; font-weight: bold; }
    
    /* תיקון טבלאות */
    div[data-testid='stTable'] { direction: RTL !important; }
    th { text-align: right !important; background-color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. חיבור לנתונים ולגוגל שיטס ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    email = st.user.get("email")
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = int(df.at[idx, 'score'])

# --- 4. מערכת כניסה אוטומטית (Google OAuth Only) ---
if not st.user.get("is_logged_in", False):
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("##### ברוכים הבאים למערכת הלמידה המרכזית\nלכניסה מאובטחת לספריית הפרוטוקולים ושמירת הניקוד:")
        st.login("google")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון משתמש וניקוד
if st.session_state.u_score == 0:
    db = get_db()
    if st.user.email in db['email'].values:
        st.session_state.u_score = int(db.loc[db['email'] == st.user.email, 'score'].values[0])
    else:
        # רישום משתמש חדש
        new_row = pd.DataFrame([{"name": st.user.name, "email": st.user.email, "score": 0, "date": str(datetime.date.today())}])
        db = pd.concat([db, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=db)

# --- 5. תפריט וניווט ---
with st.sidebar:
    st.image(st.user.get("picture", ""), width=70)
    st.markdown(f"### שלום, {st.user.name}")
    st.metric("XP ניקוד למידה", st.session_state.u_score)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד ושיאים", "פרוטוקולים מלאים (PDF)", "תרופות (גלגלת ABC)", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה"): st.logout()

# --- 6. תוכן הדפים (מילה במילה מהסיכומים שלך) ---

if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה ודירוג מחלקתי</h1>", unsafe_allow_html=True)
    ldb = get_db().sort_values(by="score", ascending=False).head(10)
    st.table(ldb[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "פרוטוקולים מלאים (PDF)":
    st.markdown("<h1>ספריית ידע PICU - הכל מתוך UpToDate</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    with t1: 
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ירידה משמעותית בטרומבוציטופניה, נויטרופניה ואנמיה (פאנציטופניה).<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור מוחלט על IVAC:</b> הלחץ מועך את הטסיות. מינון: 5mg/kg.<br>
        ● <b>FFP:</b> תורם אוניברסלי סוג AB. ● <b>PC (Packed Cells):</b> המטוקריט 70%. מתן מקסימום 4 שעות.</div>""", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול וזיהוי שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! SIRS: חום, טכיקרדיה, טכיפניאה. בולוסים 20ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש, כבד מוגדל (Liver drop). <b>להימנע מנוזלים!</b></div>""", unsafe_allow_html=True)
    with t3:
        st.markdown("""<div class='clinical-card'><h3>חבלות ראש ו-ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה לצורך הגנה על נתיב אוויר.</div>""", unsafe_allow_html=True)
    with t4:
        st.markdown("""<div class='clinical-card'><h3>אלקטרוליטים ואינסולין (שיב"א)</h3>
        ● <b>KCl:</b> תיקון פומי עדיף. מתן IV רק במקרים קשים. קצב מקסימלי: 1mEq/kg/h.<br>
        ● <b>אינסולין בהחייאה:</b> מינון פוש 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין.</div>""", unsafe_allow_html=True)

elif page == "תרופות (גלגלת ABC)":
    st.markdown("<h1>🔤 ספריית תרופות</h1>", unsafe_allow_html=True)
    meds = {"א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: פלאש מהיר", "אטרופין: ברדיקרדיה 0.02mg/kg"], "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg"]}
    col_a, col_b = st.columns(2)
    with col_a: l = st.selectbox("בחר אות:", sorted(meds.keys()))
    with col_b: drug = st.selectbox("בחר תרופה:", meds[l])
    st.markdown(f"<div class='clinical-card'>{drug}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה חיה</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-val hr'>HR: 196 | BP: 68/40 | SpO2: 89%</div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה מאוד עקב עומס תאים. +30 XP"); update_db_score(30); st.session_state.sc_idx = 1; st.rerun()
