import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# --- RTL & UI Fixes ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: bold; }
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stDataFrame, .stTable { 
        direction: RTL !important; text-align: right !important; 
    }
    /* עיצוב כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; }
    .med-card { background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 20px; border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור לגוגל שיטס ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    return conn.read(worksheet="Sheet1", ttl=0)

def sync_user(user_info):
    """בודק אם המשתמש קיים בשיטס, אם לא - מוסיף אותו"""
    df = get_db()
    email = user_info.email
    if email not in df['email'].values:
        new_user = pd.DataFrame([{"name": user_info.name, "email": email, "score": 0, "date": str(datetime.date.today())}])
        df = pd.concat([df, new_user], ignore_index=True)
        conn.update(worksheet="Sheet1", data=df)
        return 0
    return int(df[df['email'] == email]['score'].values[0])

def add_points(points):
    df = get_db()
    email = st.experimental_user.email
    idx = df[df['email'] == email].index[0]
    df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
    conn.update(worksheet="Sheet1", data=df)
    st.session_state.points = int(df.at[idx, 'score'])

# --- מערכת התחברות (Google Native) ---
if not st.experimental_user.is_logged_in:
    st.write("# 🏥 PICU Learning System")
    st.markdown("### ברוכים הבאים למערכת התרגול המחלקתית.\nלכניסה ושמירת ניקוד, אנא התחברו עם חשבון הגוגל שלכם:")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.login("google") # פקודת הקסם של Streamlit
    st.stop()

# --- אם הגענו לכאן, המשתמש מחובר ---
if 'points' not in st.session_state:
    st.session_state.points = sync_user(st.experimental_user)

# --- תפריט צדי ---
with st.sidebar:
    st.image(st.experimental_user.picture, width=100)
    st.write(f"שלום, **{st.experimental_user.name}**")
    st.metric("XP - הניקוד שלך", f"{st.session_state.points}")
    if st.button("התנתק"):
        st.logout()
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "מרכז ידע", "מבחן אישי", "ספריית תרופות ABC", "בקשת תוכן"])

# --- דאשבורד ---
if page == "דאשבורד":
    st.header("לוח בקרה מחלקתי")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🏆 טבלת שיאים (Live)")
        df = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "ניקוד"}))
    with col2:
        st.markdown(f'<div class="med-card"><h3>💊 תרופת היום</h3><b>Propofol</b><br>משמשת להרדמה קצרת טווח. דגש: עלולה לגרום לירידת לחץ דם משמעותית. זכור: "Propofol Infusion Syndrome" במתן ממושך.</div>', unsafe_allow_html=True)

# (שאר חלקי הקוד מהגרסה הקודמת - מרכז ידע, תרופות וכו')
