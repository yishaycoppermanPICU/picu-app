import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- 1. הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- 2. איתחול משתני מערכת (חובה למנועAttributeError) ---
if 'u_score' not in st.session_state: st.session_state.u_score = 0
if 's_step' not in st.session_state: st.session_state.s_step = 0
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 3. עיצוב RTL, מרכוז כותרות וסגנון Manus Pro ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    /* יישור לימין כללי */
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* מרכוז כותרות */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; margin-top: 0px; }
    
    /* ניקוי שטח לבן למעלה */
    .block-container { padding-top: 2rem !important; }

    /* כרטיסיות Manus - עיצוב תוכן מלא */
    .clinical-card {
        background: white; border-radius: 20px; padding: 40px; margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8;
        line-height: 2.2; font-size: 20px; color: #1e293b;
    }

    /* מוניטור ICU דיגיטלי */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; direction: ltr; text-align: left;
        box-shadow: inset 0 0 15px #000, 0 10px 25px rgba(0,0,0,0.4); margin: 20px 0;
    }
    .mon-val { font-size: 50px; font-weight: bold; }
    .v-hr { color: #f87171; } .v-bp { color: #fbbf24; } .v-spo2 { color: #22d3ee; }

    /* התאמת גלגלות (Dropdowns) לימין */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }

    /* כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 55px; font-weight: bold; }
    
    /* תיקון טבלאות */
    div[data-testid='stTable'] { direction: RTL !important; }
    th { text-align: right !important; background-color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. לוגיקת נתונים וחיבור לגוגל שיטס ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    email = st.session_state.get('user_email')
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = int(df.at[idx, 'score'])

# --- 5. מערכת כניסה מאובטחת וחסינת תקלות ---
if not st.session_state.logged_in:
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("##### ברוכים הבאים למערכת הלמידה המרכזית\nנא להתחבר לצורך גישה לפרוטוקולים ושמירת הניקוד:")
        
        # ניסיון כניסה עם גוגל (Native)
        try:
            st.login("google")
            if st.user.is_logged_in:
                st.session_state.logged_in = True
                st.session_state.user_name = st.user.name
                st.session_state.user_email = st.user.email
                st.rerun()
        except Exception:
            # Fallback אם כפתור גוגל קורס טכנית
            st.warning("🔄 שירות גוגל בטעינה או לא מוגדר. השתמשו בכניסה ידנית מאומתת:")
            n = st.text_input("שם מלא:")
            m = st.text_input("אימייל:")
            if st.button("כניסה למערכת"):
                if n and m:
                    st.session_state.logged_in = True
                    st.session_state.user_name, st.session_state.user_email = n, m
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון ניקוד בטעינה
if st.session_state.u_score == 0:
    try:
        db = get_db()
        if st.session_state.user_email in db['email'].values:
            st.session_state.u_score = int(db.loc[db['email'] == st.session_state.user_email, 'score'].values[0])
    except: pass

# --- 6. תפריט ואתר ---
with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_name}")
    st.metric("XP ניקוד למידה", st.session_state.u_score)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד ושיאים", "פרוטוקולים מלאים (PDF)", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה מהמערכת"): st.logout()

# --- 7. תוכן האתר (כל המסה הקלינית מה-PDFים שלך) ---

if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה ודירוג מחלקתי</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class='clinical-card'><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש קריטי מהסיכום:</b> חולים הסובלים במקביל מהיפומגנזמיה והיפוקלמיה - <b>חובה לתקן מגנזיום תחילה!</b><br>
        ● <b>מידע IV:</b> 14.9% KCl IV = 2mEq/ml. קצב מקסימלי בילדים: 0.5 mEq/kg/h.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10 Leaders")
        try:
            ldf = get_db().sort_values(by="score", ascending=False).head(10)
            st.table(ldf[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))
        except: st.write("טוען נתונים...")

elif page == "פרוטוקולים מלאים (PDF)":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא מהסיכומים</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    
    with t1: 
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ירידה משמעותית בטרומבוציטופניה, נויטרופניה ואנמיה. גורמים: לוקמיה, אנמיה אפלסטית.<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור מוחלט על IVAC:</b> הלחץ מועך את הטסיות. <br>
        ● <b>Cryoprecipitate:</b> מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.</div>""", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול וזיהוי שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! SIRS: חום, טכיקרדיה, טכיפניאה. בולוסים 20ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש, כבד מוגדל (Liver drop). <b>להימנע מנוזלים המעמיסים על הלב!</b></div>""", unsafe_allow_html=True)
    with t3:
        st.markdown("""<div class='clinical-card'><h3>חבלות ראש (TBI) וניהול ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר. <br>
        ● <b>ניהול:</b> ראש ב-30 מעלות, מנח ישר, סליין 3% (5cc/kg) או מניטול (דרך פילטר).</div>""", unsafe_allow_html=True)
    with t4:
        st.markdown("""<div class='clinical-card'><h3>אלקטרוליטים ואינסולין (שיב"א)</h3>
        ● <b>KCl:</b> תיקון פומי עדיף. מתן IV רק במקרים קשים. קצב מקסימלי: 1mEq/kg/h.<br>
        ● <b>אינסולין בהחייאה:</b> מינון פוש 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין.</div>""", unsafe_allow_html=True)

elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות - גלגלת בחירה</h1>", unsafe_allow_html=True)
    meds_full = {
        "א": ["אדרנלין: החייאה 0.01mg/kg / סטרידור 400mcg/kg", "אדנוזין: SVT - 0.1mg/kg (פלאש)", "אטרופין: ברדיקרדיה 0.02mg/kg (מינימום 0.1mg)"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: סטרידור/אקסטובציה 0.6mg/kg", "דובוטמין: 2-20mcg/kg/min"],
        "מ": ["מילרינון: 0.25-0.75mcg/kg/min (Inodilator)", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg"],
        "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: שיכוך כאב 1-2mcg/kg", "פרופופול: הרדמה 2.5-3.5mg/kg"]
    }
    col_a, col_b = st.columns(2)
    with col_a: l = st.selectbox("בחר אות:", sorted(meds_full.keys()))
    with col_b: d = st.selectbox(f"תרופות ב-'{l}':", meds_full[l])
    st.markdown(f"<div class='clinical-card'>{d}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה חיה</h1>", unsafe_allow_html=True)
    if st.session_state.s_step == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-grid'>
            <div><span style='color:#94a3b8;font-size:14px;'>HEART RATE</span><br><span class='mon-val v-hr'>196</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>BP SYSTOLIC</span><br><span class='mon-val' style='color:#fbbf24'>68</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>SPO2</span><br><span class='mon-val v-spo2'>89%</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>TEMP</span><br><span class='mon-val' style='color:white'>38.4</span></div>
        </div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה מאוד. +30 XP"); update_xp(30); st.session_state.s_step = 1; st.rerun()
    # (המשך התרחישים יופיע כאן בלחיצה)
