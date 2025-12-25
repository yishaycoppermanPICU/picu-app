import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- 1. הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- 2. איתחול משתנים (מניעת קריסות AttributeError) ---
if 'u_xp' not in st.session_state: st.session_state.u_xp = 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0

# --- 3. עיצוב RTL ומרכוז (Manus Pro Style) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    /* יישור לימין אבסולוטי - תיקון לכל האתר */
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* מרכוז כותרות */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; margin-top: 0px; }
    
    /* ניקוי שטח לבן */
    .block-container { padding-top: 2rem !important; }

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
        box-shadow: 0 15px 40px rgba(0,0,0,0.5); margin: 20px 0;
    }
    .mon-val { font-size: 50px; font-weight: bold; }
    .hr { color: #f87171; } .bp { color: #fbbf24; } .spo2 { color: #22d3ee; }

    /* הגדרת גלגלות לימין */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }
    
    /* כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 55px; font-weight: bold; }
    
    /* תיקון טבלאות */
    div[data-testid='stTable'] { direction: RTL !important; }
    th { text-align: right !important; background-color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. לוגיקת נתונים ---
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
        st.session_state.u_xp = int(df.at[idx, 'score'])

# --- 5. כניסה מאובטחת - Google OAuth ---
if not st.user.get("is_logged_in", False):
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("ברוכים הבאים למערכת הלמידה המרכזית. לכניסה ושמירת התקדמות, נא להתחבר עם חשבון גוגל:")
        # ניסיון הרצה - אם יש שגיאה ב-auth, נציג הודעה מובנת
        try:
            st.login("google")
        except Exception:
            st.error("שגיאת אימות: וודא שפרטי Google Client ID ב-Secrets נכונים וביצעת Reboot לאפליקציה.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון ניקוד לאחר כניסה
if st.session_state.u_xp == 0:
    db = get_db()
    email = st.user.get("email")
    if email in db['email'].values:
        st.session_state.u_xp = int(db.loc[db['email'] == email, 'score'].values[0])

# --- 6. תפריט ואתר ---
with st.sidebar:
    st.image(st.user.get("picture", ""), width=70)
    st.markdown(f"### שלום, {st.user.get('name', 'משתמש')}")
    st.metric("XP ניקוד מצטבר", st.session_state.u_xp)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד ושיאים", "פרוטוקולים לקריאה", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה מהמערכת"): st.logout()

# --- 7. תוכן האתר (המסה הקלינית המלאה מה-PDF) ---

if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה ודירוג מחלקתי</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class='clinical-card'><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש מהסיכום:</b> חולים הסובלים במקביל מהיפומגנזמיה והיפוקלמיה, חובה לתקן מגנזיום תחילה למניעת היפוקלמיה עמידה.<br>
        ● <b>מידע שימושי:</b> 14.9% KCl IV = 2mEq/ml. קצב מקסימלי בילדים: 0.5 mEq/kg/h.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10 Leaders")
        try:
            df_list = get_db().sort_values(by="score", ascending=False).head(10)
            st.table(df_list[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))
        except: st.write("טוען נתונים...")

elif page == "פרוטוקולים לקריאה":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    
    with t1: 
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ירידה משמעותית בטרומבוציטופניה (PLT), נויטרופניה ואנמיה.<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור מוחלט על IVAC:</b> הלחץ מועך את הטסיות. מינון: 5mg/kg.<br>
        ● <b>FFP (פלזמה):</b> תורם אוניברסלי סוג AB. נשמר שנה במינוס 20 מעלות.<br>
        ● <b>Cryoprecipitate:</b> מקורו בפלסמה. מכיל פיברינוגן (פקטור I), פקטור VIII, XIII, vWF.</div>""", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול וזיהוי שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! SIRS: חום, טכיקרדיה, טכיפניאה. בולוסים 20ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש, כבד מוגדל (Liver drop). <b>להימנע מנוזלים!</b><br>
        ● <b>אנפילקסיס:</b> טיפול ראשון - אדרנלין IM בירך (0.01mg/kg). מקסימום 0.5mg.</div>""", unsafe_allow_html=True)
    with t3:
        st.markdown("""<div class='clinical-card'><h3>חבלות ראש (TBI) וניהול ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר. <br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד (סימן להרניאציה).<br>
        ● <b>טיפול בבצקת:</b> ראש 30 מעלות, מנח ישר, סליין 3% (5cc/kg) או מניטול.</div>""", unsafe_allow_html=True)
    with t4:
        st.markdown("""<div class='clinical-card'><h3>אלקטרוליטים ואינסולין (שיב"א)</h3>
        ● <b>KCl:</b> תיקון פומי עדיף. מתן IV רק במקרים קשים. קצב מקסימלי: 40mEq/h.<br>
        ● <b>אינסולין בהחייאה:</b> מינון פוש 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין.<br>
        ● <b>ביקרבונט:</b> בופר לדם. בילדים < שנתיים יש לדלל פי 2.</div>""", unsafe_allow_html=True)

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
    st.markdown("<h1>סימולציה: התדרדרות חיה</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-grid'>
            <div><span style='color:#94a3b8;font-size:14px;'>HEART RATE</span><br><span class='mon-val hr'>196</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>BP SYSTOLIC</span><br><span class='mon-val' style='color:#fbbf24'>68</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>SPO2</span><br><span class='mon-val spo2'>89%</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>TEMP</span><br><span class='mon-val' style='color:white'>38.4</span></div>
        </div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה מאוד. +30 XP"); update_xp(30); st.session_state.sc_idx = 1; st.rerun()
    # (המשך התרחישים יופיע כאן בלחיצה)
