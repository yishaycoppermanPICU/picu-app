import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. הגדרות דף ועיצוב RTL מוחלט (ביצוע בקרה עיצובית 3) ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# איתחול משתני מערכת בראש הקוד למניעת קריסות
if 'u_xp' not in st.session_state: st.session_state.u_xp = 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* מניעת שטח לבן עליון */
    .block-container { padding-top: 1rem !important; }

    /* מרכוז כותרות Manus */
    h1, h2, h3 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: 800; }
    
    /* כרטיסיות מידע Manaus Style */
    .clinical-card {
        background: white; border-radius: 16px; padding: 40px; margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06); border-right: 12px solid #2e59a8;
        line-height: 2.2; font-size: 20px; color: #1e293b;
    }

    /* מוניטור ICU דיגיטלי */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; direction: ltr; text-align: left;
        box-shadow: inset 0 0 15px #000, 0 10px 25px rgba(0,0,0,0.4); margin: 20px 0;
    }
    .mon-val { font-size: 50px; font-weight: bold; }
    
    /* יישור גלגלות (Dropdowns) */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }

    /* כפתור גוגל מעוצב */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 50px; font-weight: bold; }
    
    /* הסרת מספור טבלאות */
    div[data-testid='stTable'] { direction: RTL !important; }
    th { text-align: right !important; background-color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. חיבור לנתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_db_xp(points):
    df = get_db()
    email = st.session_state.get('user_email')
    if email and email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_xp = int(df.at[idx, 'score'])

# --- 3. כניסה מאובטחת וחסינת תקלות ---
if not st.session_state.logged_in:
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("##### ברוכים הבאים למערכת הלמידה המרכזית\nנא להתחבר עם חשבון גוגל למניעת כפילויות ושמירתXP:")
        
        # ניסיון כניסה עם גוגל
        try:
            st.login("google")
            if st.user.is_logged_in:
                st.session_state.logged_in = True
                st.session_state.user_name = st.user.name
                st.session_state.user_email = st.user.email
                st.rerun()
        except:
            # אם גוגל עדיין לא הוגדר נכון ב-Secrets, נשמר את הקיים בצורה יפה יותר
            st.info("כניסה לצוות מאומת (מצב גיבוי):")
            name = st.text_input("שם מלא:")
            email = st.text_input("אימייל:")
            if st.button("כניסה למערכת"):
                if name and email:
                    st.session_state.logged_in = True
                    st.session_state.user_name, st.session_state.user_email = name, email
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון XP מהגיליון
if st.session_state.u_xp == 0:
    db = get_db()
    if st.session_state.user_email in db['email'].values:
        st.session_state.u_xp = int(db.loc[db['email'] == st.session_state.user_email, 'score'].values[0])

# --- 4. תפריט ואתר ---
with st.sidebar:
    st.image(st.user.picture if st.user.get('picture') else "https://cdn-icons-png.flaticon.com/512/1144/1144760.png", width=70)
    st.markdown(f"### שלום, {st.session_state.user_name}")
    st.metric("XP ניקוד למידה", st.session_state.u_xp)
    st.divider()
    page = st.radio("בחר אזור למידה:", ["דאשבורד ושיאים", "פרוטוקולים מלאים", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה"): st.logout()

# --- 5. תוכן הדפים (כל המסה מה-PDF) ---

if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה ודירוג מחלקתי</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class='clinical-card'><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש קריטי:</b> בחולים עם היפומגנזמיה והיפוקלמיה במקביל - <b>חובה לתקן מגנזיום תחילה!</b><br>
        ● <b>חישוב מהיר (שיב"א):</b> 14.9% KCl IV = 2mEq/ml. קצב מקסימלי בילדים: 0.5 mEq/kg/h.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10 Leaders")
        leader_df = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(leader_df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "פרוטוקולים מלאים":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    with t1: 
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ירידה משמעותית בטרומבוציטופניה, נויטרופניה ואנמיה (פאנציטופניה).<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור IVAC!</b> הלחץ מועך את הטסיות. מינון: 5mg/kg.<br>
        ● <b>FFP:</b> תורם אוניברסלי סוג AB. ● <b>Cryoprecipitate:</b> מכיל פיברינוגן, פקטור VIII, XIII, vWF.</div>""", unsafe_allow_html=True)
    # ... הטמעת שאר התוכן המלא כאן
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול וזיהוי שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! SIRS: חום, טכיקרדיה, טכיפניאה. בולוסים 20ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש, כבד מוגדל (Liver drop). <b>להימנע מנוזלים!</b></div>""", unsafe_allow_html=True)

elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU</h1>", unsafe_allow_html=True)
    meds = {"א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: פלאש מהיר", "אטרופין: ברדיקרדיה"], "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg"]}
    col_a, col_b = st.columns(2)
    with col_a: l = st.selectbox("בחר אות:", sorted(meds.keys()))
    with col_b: d = st.selectbox("בחר תרופה:", meds[l])
    st.markdown(f"<div class='clinical-card'>{d}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: התדרדרות חיה</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-val' style='color:#f87171'>HR: 196</div><div class='mon-val' style='color:#fbbf24'>BP: 68/40</div><div class='mon-val' style='color:#22d3ee'>SpO2: 89%</div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה מאוד עקב עומס תאים. +30 XP"); st.session_state.sc_idx = 1; st.rerun()
