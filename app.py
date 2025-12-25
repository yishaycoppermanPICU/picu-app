import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. הגדרות דף ו-CSS (Manus Pro Style) ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# הזרקת CSS לביצוע יישור RTL מושלם, מרכוז כותרות וניקוי שטחים לבנים
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*='css'] { 
        font-family: 'Assistant', sans-serif; 
        direction: RTL !important; 
        text-align: right !important; 
        background-color: #f8fafc; 
    }
    
    /* מניעת שטח לבן למעלה */
    .block-container { padding-top: 2rem !important; }
    
    /* כותרות Manus - ממורכזות */
    h1, h2, h3 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; margin-top: 0px; }
    
    /* יישור רכיבים לימין */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stMetric, .stExpander, label { 
        direction: RTL !important; text-align: right !important; 
    }
    
    /* כרטיסיות מידע מקצועיות */
    .clinical-card {
        background: white; border-radius: 16px; padding: 35px; margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8;
        line-height: 2.2; font-size: 19px; color: #1e293b;
    }

    /* מוניטור ICU שחור-ניאון */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; direction: ltr; text-align: left;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5); margin: 20px 0;
    }
    .mon-val { font-size: 45px; font-weight: bold; }
    .hr { color: #f87171; } .bp { color: #fbbf24; } .spo2 { color: #22d3ee; }

    /* עיצוב כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 55px; font-size: 1.1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. לוגיקת נתונים (GSheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

# --- 3. ניהול כניסה (אוטומטי עם גוגל) ---
if not st.user.is_logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
        st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("### שלום לצוות PICU")
        st.write("אנא התחברו עם חשבון הגוגל המאומת שלכם לצד שמירה על הניקוד בטבלת השיאים:")
        
        # כניסת גוגל סופית
        st.login("google")
        
        if "auth" not in st.secrets:
            st.warning("🔄 המערכת ממתינה להגדרת מפתחות גוגל ב-Secrets.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. אתחול נתונים לאחר כניסה ---
if 'u_score' not in st.session_state:
    db = get_db()
    st.session_state.u_score = int(db.loc[db['email'] == st.user.email, 'score'].values[0]) if st.user.email in db['email'].values else 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0

# --- 5. תפריט צד ---
with st.sidebar:
    st.image(st.user.picture, width=70)
    st.markdown(f"### שלום, {st.user.name}")
    st.metric("XP - ניקוד למידה", st.session_state.u_score)
    st.divider()
    page = st.radio("בחר אזור למידה:", ["דאשבורד", "פרוטוקולי למידה", "תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה מהחשבון"): st.logout()

# --- 6. תוכן הדפים (מבוסס PDF) ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה ושיאים</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class='clinical-card'><h3>💊 תרופת היום: דקסמתזון</h3>
        ● <b>דגש קריטי:</b> ב-PICU משמשת למניעת בצקת דרכי נשימה לאחר אקסטובציה.<br>
        ● <b>פרוטוקול:</b> מינון 0.5-1 mg/kg. מומלץ לתת מנה ראשונה 6-12 שעות לפני הפעולה.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10 Leaders")
        leader_df = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(leader_df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "פרוטוקולי למידה":
    t1, t2, t3 = st.tabs(["המטולוגיה", "שוק וספסיס", "TBI ו-ICP"])
    with t1:
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור IVAC!</b> גורם להרס פיזי של הטסיות. מינון: 5mg/kg.<br>
        ● <b>FFP:</b> תורם אוניברסלי - סוג AB (ללא נוגדנים). נשמר שנה במינוס 20.</div>""", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול שוק</h3>
        ● <b>ספסיס:</b> טיפול ב'שעת הזהב'. בולוסים של 20ml/kg. <br>
        ● <b>קרדיוגני:</b> סימני גודש (Liver drop), חרחורים. <b>אסור לתת בולוסים!</b></div>""", unsafe_allow_html=True)

elif page == "תרופות ABC":
    meds = {"א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: 0.1mg/kg פלאש"], "ד": ["דופמין: 1-20mcg/kg/min"]}
    l = st.selectbox("בחר אות:", sorted(meds.keys()))
    d = st.selectbox("בחר תרופה:", meds[l])
    st.markdown(f"<div class='clinical-card'>{d}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה חיה</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד חיוור, אפרורי ואפטי.")
        st.markdown("""<div class='icu-monitor'><div class='mon-val hr'>HR: 196 | BP: 68/40 | SpO2: 89%</div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה עקב עומס תאים. +30 XP"); st.session_state.sc_idx = 1; st.rerun()
