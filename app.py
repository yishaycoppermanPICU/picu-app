import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- 1. הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- 2. איתחול משתנים למניעת קריסות ---
if 'u_score' not in st.session_state: st.session_state.u_score = 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0

# --- 3. עיצוב RTL ומרכוז (Manus Style) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    html, body, [class*='css'] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; background-color: #f8fafc; }
    h1, h2, h3 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; }
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { direction: RTL !important; text-align: right !important; }
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }
    .clinical-card { background: white; border-radius: 16px; padding: 30px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8; line-height: 2; font-size: 19px; }
    .icu-monitor { background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace; padding: 30px; border-radius: 15px; direction: ltr; text-align: left; box-shadow: 0 15px 45px rgba(0,0,0,0.6); margin: 25px 0; }
    .mon-val { font-size: 45px; font-weight: bold; }
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. חיבור לנתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    email = st.session_state.get('user_email')
    if email and email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = int(df.at[idx, 'score'])

# --- 5. כניסה מאובטחת ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1>🏥 PICU Master Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        try:
            # מנסה להשתמש בכניסת גוגל אוטומטית
            st.login("google")
            if st.user.is_logged_in:
                st.session_state.logged_in = True
                st.session_state.user_name = st.user.name
                st.session_state.user_email = st.user.email
                st.rerun()
        except:
            # אם גוגל לא מוגדר, מציג כניסה ידנית ששומרת להם את הניקוד
            st.warning("נורת אזהרה: חיבור גוגל לא הוגדר ב-Secrets. נכנס במצב ידני:")
            name = st.text_input("שם מלא:")
            email = st.text_input("אימייל:")
            if st.button("כניסה"):
                st.session_state.logged_in = True
                st.session_state.user_name, st.session_state.user_email = name, email
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 6. ניווט ותוכן ---
with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_name}")
    st.metric("XP ניקוד למידה", st.session_state.u_score)
    st.divider()
    page = st.radio("תפריט:", ["דאשבורד", "פרוטוקולי למידה", "ספריית תרופות", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה"): st.logout()

if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה ושיאים</h1>", unsafe_allow_html=True)
    db = get_db().sort_values(by="score", ascending=False).head(10)
    st.table(db[["name", "score"]].rename(columns={"name": "שם", "score": "ניקוד"}))

elif page == "פרוטוקולי למידה":
    curr = st.tabs(["המטולוגיה", "שוק וספסיס", "TBI", "אלקטרוליטים"])
    with curr[0]: st.markdown("<div class='clinical-card'><h3>מוצרי דם</h3>טסיות (PLT): מתן מתחת ל-10,000. <b>בלי IVAC!</b></div>", unsafe_allow_html=True)
    with curr[1]: st.markdown("<div class='clinical-card'><h3>שוק וספסיס</h3>ספסיס: טיפול תוך שעה. בולוסים של 20ml/kg.</div>", unsafe_allow_html=True)

elif page == "ספריית תרופות":
    meds = {"א": ["אדרנלין: 0.01mg/kg", "אדנוזין: פלאש מהיר"], "ד": ["דופמין: 1-20mcg"]}
    letter = st.selectbox("בחר אות:", sorted(meds.keys()))
    drug = st.selectbox("בחר תרופה:", meds[letter])
    st.markdown(f"<div class='clinical-card'>{drug}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה קלינית</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("תינוק עם AML, לבנים 810,000. הילד חיוור ואפטי.")
        st.markdown("<div class='icu-monitor'><div class='mon-val'>HR: 196 | BP: 68/40 | SpO2: 89%</div></div>", unsafe_allow_html=True)
        if st.button("חשד ל-Leukostasis"): st.success("נכון! +30 XP"); update_xp(30); st.session_state.sc_idx = 1; st.rerun()
