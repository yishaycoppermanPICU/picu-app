import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- בקרת איכות 1: יישור RTL ועיצוב Manus Pro ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; background-color: #f8fafc; }
    
    /* כותרות Manus - ממורכזות וכהות */
    h1, h2, h3 { text-align: center !important; direction: RTL !important; color: #0f172a; font-weight: 700; margin-top: 10px; }
    
    /* יישור רכיבים לימין */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        direction: RTL !important; text-align: right !important; 
    }
    
    /* תיקון ספציפי לגלגלות (Selectbox) */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }

    /* כרטיסיות מידע קליני */
    .clinical-box {
        background: white; border-radius: 16px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-right: 10px solid #2e59a8;
        line-height: 1.8; font-size: 18px; color: #1e293b;
    }
    
    /* מוניטור ICU דיגיטלי */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 25px; border-radius: 15px; border: 4px solid #334155;
        direction: ltr; text-align: left; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin: 20px 0;
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .mon-val { font-size: 42px; font-weight: bold; }
    .v-hr { color: #ff4b4b; } .v-bp { color: #facc15; } .v-spo2 { color: #22d3ee; }

    /* Sidebar RTL */
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- בקרת איכות 2: ניהול נתונים (GSheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    email = st.session_state.get("u_email")
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = int(df.at[idx, 'score'])

# --- בקרת איכות 3: כניסה אוטומטית (Google Auth) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-box" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("לכניסה ושמירת התקדמות, נא להתחבר:")
        
        # כפתור גוגל רשמי (Streamlit Native)
        try:
            st.login("google")
            if st.user.is_logged_in:
                st.session_state.logged_in = True
                st.session_state.u_name = st.user.name
                st.session_state.u_email = st.user.email
                # טעינת ניקוד
                db = get_db()
                st.session_state.u_score = int(db.loc[db['email'] == st.user.email, 'score'].values[0]) if st.user.email in db['email'].values else 0
                st.rerun()
        except:
            # Fallback אם גוגל לא מוגדר
            st.info("מצב כניסה מהירה:")
            n = st.text_input("שם:")
            m = st.text_input("מייל:")
            if st.button("כניסה"):
                st.session_state.logged_in = True
                st.session_state.u_name, st.session_state.u_email = n, m
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- תפריט צדי ---
with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.u_name}")
    st.metric("XP - ניקוד מצטבר", st.session_state.u_score)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "פרוטוקולים מלאים", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢", "ניהול"])
    if st.button("יציאה"): st.logout()

# --- תוכן האתר ---

if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה ושיאים</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class="clinical-box"><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש קריטי מהסיכום:</b> בחולים עם היפומגנזמיה והיפוקלמיה במקביל - <b>חובה לתקן מגנזיום תחילה!</b><br>
        ● <b>חישוב מהיר:</b> 14.9% KCl IV = 2mEq/ml. קצב מקסימלי בילדים: 0.5mEq/kg/h.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10")
        df_sorted = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(df_sorted[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "פרוטוקולים מלאים":
    st.markdown("<h1>מרכז הידע - UpToDate Based</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🩸 המטולוגיה", "💧 אלקטרוליטים", "🧠 נוירולוגיה (TBI)"])
    with t1:
        st.markdown('<div class="clinical-box"><h3>פאנציטופניה ומוצרי דם</h3>● <b>טסיות (PLT):</b> התוויה < 10,000. <b>אסור ב-IVAC!</b> (הלחץ הורס אותן). מינון: 5mg/kg.<br>● <b>FFP:</b> תורם אוניברסלי - סוג AB (אין בו נוגדנים).</div>', unsafe_allow_html=True)
    with t2:
        st.markdown('<div class="clinical-box"><h3>אלקטרוליטים ואינסולין</h3>● <b>אשלגן:</b> תיקון פומי עדיף. IV רק במקרים קשים.<br>● <b>אינסולין בהחייאה:</b> מינון פוש 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין.</div>', unsafe_allow_html=True)
    with t3:
        st.markdown('<div class="clinical-box"><h3>חבלות ראש ו-ICP</h3>● <b>CPP:</b> MAP פחות ICP. יעד: 40-60.<br>● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד (סימן להרניאציה).</div>', unsafe_allow_html=True)

elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU</h1>", unsafe_allow_html=True)
    meds = {
        "א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: 0.1mg/kg פלאש מהיר", "אטרופין: 0.02mg/kg (מינימום 0.1mg)"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg"],
        "מ": ["מילרינון: 0.25-0.75mcg/kg/min", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg"],
        "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: 1-2mcg/kg", "פרופופול: 2.5-3.5mg/kg"]
    }
    col_a, col_b = st.columns(2)
    with col_a: letter = st.selectbox("בחר אות:", sorted(meds.keys()))
    with col_b: drug = st.selectbox(f"תרופות ב-'{letter}':", meds[letter])
    st.markdown(f'<div class="clinical-box">{drug}</div>', unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור מאוד ואפטי**.")
        st.markdown("""<div class="icu-monitor"><div class="mon-grid">
            <div><span style="color:#94a3b8; font-size:14px;">HR</span><br><span class="mon-val v-hr">194</span></div>
            <div><span style="color:#94a3b8; font-size:14px;">BP</span><br><span class="mon-val v-bp">68/40</span></div>
            <div><span style="color:#94a3b8; font-size:14px;">SpO2</span><br><span class="mon-val v-spo2">89%</span></div>
            <div><span style="color:#94a3b8; font-size:14px;">RR</span><br><span class="mon-val" style="color:white">62</span></div>
        </div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי?", ["דימום", "Leukostasis (חסימה מכנית)", "ספסיס"], key="q1")
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון! +20 XP"); st.session_state.sc_idx = 1; st.rerun()
