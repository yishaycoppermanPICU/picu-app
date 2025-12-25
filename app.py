import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- 1. הגדרות דף ועיצוב RTL הרמטי ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# הזרקת CSS לתיקון יישור לימין, מרכוז כותרות ועיצוב מוניטור
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    /* יישור לימין לכל האתר */
    html, body, [class*="css"], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; 
        direction: RTL !important; 
        text-align: right !important; 
    }
    
    /* מרכוז כותרות */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: 800; }
    
    /* עיצוב המוניטור (ICU Style) */
    .monitor-panel {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; border: 4px solid #334155;
        direction: ltr; text-align: left; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin: 20px 0;
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .mon-val { font-size: 45px; font-weight: bold; }
    .val-hr { color: #f87171; } .val-bp { color: #fbbf24; } .val-spo2 { color: #22d3ee; }

    /* כרטיסיות מידע בסגנון Manus Pro */
    .clinical-card {
        background: white; border-radius: 16px; padding: 30px; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8;
        line-height: 1.8; font-size: 19px; color: #1e293b;
    }

    /* התאמת גלגלות (Dropdowns) */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }
    
    /* הסרת אינדקס מטבלאות */
    div[data-testid="stTable"] { direction: RTL !important; }
    th { text-align: right !important; background-color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. חיבור נתונים (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def add_points(points):
    df = fetch_db()
    email = st.user.email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = int(df.at[idx, 'score'])

# --- 3. כניסה אוטומטית (Google OAuth בלבד) ---
if not st.user.get("is_logged_in"):
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("לכניסה ושמירת התקדמות, נא להתחבר עם חשבון גוגל המאומת שלכם:")
        st.login("google")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון ניקוד בטעינת האתר
if 'u_score' not in st.session_state or st.session_state.u_score == 0:
    db = fetch_db()
    if st.user.email in db['email'].values:
        st.session_state.u_score = int(db.loc[db['email'] == st.user.email, 'score'].values[0])
    else:
        # רישום משתמש חדש בגיליון
        new_row = pd.DataFrame([{"name": st.user.name, "email": st.user.email, "score": 0, "date": str(datetime.date.today())}])
        db = pd.concat([db, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=db)
        st.session_state.u_score = 0

# --- 4. תפריט ואתר ---
with st.sidebar:
    st.image(st.user.get("picture"), width=80)
    st.markdown(f"### שלום, {st.user.name}")
    st.metric("צבירת XP", f"{st.session_state.u_score}")
    if st.button("התנתק"): st.logout()
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "פרוטוקולים לקריאה", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])

# --- 5. דפי האתר ---

if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה ושיאים מחלקתיים</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class='clinical-card'><h3>💊 תרופת היום: דקסמתזון</h3>
        ● <b>דגש PICU:</b> משמשת רבות למניעת סטרידור לאחר אקסטובציה (Post-extubation stridor).<br>
        ● <b>עובדה מעניינת:</b> נותנים מנה ראשונה 6-12 שעות לפני האקסטובציה המתוכננת.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 טבלת המובילים")
        leader_df = fetch_db().sort_values(by="score", ascending=False).head(10)
        st.table(leader_df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "פרוטוקולים לקריאה":
    st.markdown("<h1>ספריית ידע PICU מלאה</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה (TBI)"])
    
    with t1:
        st.markdown("""<div class='clinical-card'><h3>המטולוגיה ומוצרי דם</h3>
        <b>פאנציטופניה:</b> ירידה בטרומבוציטים, נויטרופילים ואנמיה.<br>
        ● <b>טסיות (PLT):</b> התוויה מתחת ל-10,000. <b>אין לתת ב-IVAC!</b> (הלחץ הורס טסיות).<br>
        ● <b>Cryoprecipitate:</b> מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.</div>""", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול שוק</h3>
        ● <b>ספסיס:</b> תוך שעה - בולוסים של 20ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש (כבד מוגדל, חרחורים). להימנע מנוזלים המעמיסים על הלב!</div>""", unsafe_allow_html=True)
    with t3:
        st.markdown("""<div class='clinical-card'><h3>חבלות ראש ו-ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר לחץ דם. סימן להרניאציה.<br>
        ● <b>ניהול:</b> ראש ב-30 מעלות, מנח ישר, סליין 3% (5cc/kg).</div>""", unsafe_allow_html=True)

elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU</h1>", unsafe_allow_html=True)
    meds_db = {
        "א": ["אדרנלין: החייאה 0.01mg/kg", "אדנוזין: SVT 0.1mg/kg", "אטרופין: ברדיקרדיה 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg"],
        "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: לתינוקות 1-2mcg/kg"]
    }
    col_a, col_b = st.columns(2)
    with col_a: 
        letter = st.selectbox("בחר אות ראשונה:", sorted(meds_db.keys()))
    with col_b: 
        drug = st.selectbox(f"תחרות באות {letter}:", meds_db[letter])
    st.markdown(f"<div class='clinical-card'>{drug}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה</h1>", unsafe_allow_html=True)
    if 's_step' not in st.session_state: st.session_state.s_step = 0
    
    if st.session_state.s_step == 0:
        st.info("**מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור מאוד ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-grid'>
            <div><span style='color:#94a3b8;font-size:14px;'>HEART RATE</span><br><span class='mon-val val-hr'>196</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>BP SYSTOLIC</span><br><span class='mon-val val-bp'>68</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>SPO2</span><br><span class='mon-val val-spo2'>89%</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>TEMP</span><br><span class='mon-val' style='color:white'>38.4</span></div>
        </div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי?", ["דימום", "Leukostasis (חסימה)", "ספסיס"], key="q1")
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון! +30 XP"); st.session_state.s_step = 1; st.rerun()

    elif st.session_state.s_step == 1:
        st.warning("**מצב:** הילד פיתח אריתמיה. מעבדה: Potassium 7.2. הילד עם **רעד בגפיים**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-val val-red'>! ARRYTHMIA !</div><div class='mon-val'>HR: 215</div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה הפעולה הדחופה להגנה על הלב?", ["פוסיד", "קלציום גלוקונט IV", "אלופורינול"], key="q2")
        if st.button("טפל"):
            if "קלציום" in ans: st.success("נכון!"); st.session_state.s_step = 2; st.rerun()

    elif st.session_state.s_step == 2:
        st.error("**מצב:** הילד מתנשם בכבד. בהאזנה: **חרחורים**. כבד נמוש 4 ס''מ (Liver drop).")
        ans = st.radio("אבחנה?", ["שוק ספטי", "שוק קרדיוגני", "שוק היפוולמי"], key="q3")
        if st.button("סיים תרחיש"):
            if "קרדיוגני" in ans: st.balloons(); add_points(50); st.success("הצלת את החולה!"); st.session_state.s_step = 0
