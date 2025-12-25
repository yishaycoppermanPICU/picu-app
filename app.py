import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. הגדרות דף ועיצוב RTL מוחלט (Manus Pro UI) ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# הזרקת CSS לביצוע יישור לימין (RTL) אגרסיבי ומרכוז כותרות
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* מרכוז כותרות */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; margin-bottom: 25px; }
    
    /* כרטיסיות Manus */
    .clinical-card {
        background: white; border-radius: 20px; padding: 40px; margin-bottom: 25px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8; 
        line-height: 2; font-size: 20px; color: #1e293b; 
    }

    /* מוניטור ICU דיגיטלי */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace; 
        padding: 30px; border-radius: 15px; border: 5px solid #334155; 
        direction: ltr; text-align: left; box-shadow: 0 15px 45px rgba(0,0,0,0.6); margin: 20px 0; 
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .mon-val { font-size: 48px; font-weight: bold; }
    .v-hr { color: #f87171; } .v-bp { color: #fbbf24; } .v-spo2 { color: #22d3ee; }
    
    /* יישור גלגלות וטבלאות */
    div[data-baseweb='select'] > div { direction: RTL !important; text-align: right !important; }
    div[data-testid='stTable'] { direction: RTL !important; }
    th { text-align: right !important; background-color: #f1f5f9 !important; }
    
    /* כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. לוגיקה וחיבור לנתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

# --- 3. מערכת כניסה מאובטחת - Google Only ---
if not st.user.is_logged_in:
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("ברוכים הבאים למערכת הלמידה המרכזית. לכניסה מאובטחת ושמירת ניקוד, נא להתחבר עם חשבון גוגל:")
        st.login("google")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. אתחול נתוני משתמש ---
if 'u_score' not in st.session_state:
    db = get_db()
    st.session_state.u_score = int(db.loc[db['email'] == st.user.email, 'score'].values[0]) if st.user.email in db['email'].values else 0
if 's_idx' not in st.session_state: st.session_state.s_idx = 0

# --- 5. תפריט ואתר ---
with st.sidebar:
    st.image(st.user.picture, width=70)
    st.markdown(f"### שלום, {st.user.name}")
    st.metric("XP ניקוד מצטבר", st.session_state.u_score)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד ושיאים", "מרכז ידע מלא (PDF)", "תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("התנתק"): st.logout()

# --- 6. דפי התוכן (המסה הקלינית המלאה) ---
if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה מחלקתי</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class='clinical-card'><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש מהסיכום:</b> חובה לתקן מגנזיום תחילה למניעת היפוקלמיה עמידה.<br>
        ● <b>מידע IV:</b> 14.9% KCl = 2mEq/ml. קצב מקסימלי: 0.5 mEq/kg/h.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10 Leaders")
        df_list = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(df_list[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "מרכז ידע מלא (PDF)":
    st.markdown("<h1>ספריית ידע PICU - הכל מתוך UpToDate</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    
    with t1:
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ירידה משמעותית בכל שורות הדם: טרומבוציטופניה (PLT), נויטרופניה ואנמיה.<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור מוחלט על IVAC:</b> הלחץ הורס את הטסיות. מינון: 5mg/kg.<br>
        ● <b>FFP (פלזמה):</b> תורם אוניברסלי מסוג AB. אין צורך בהקרנה. <br>
        ● <b>Cryoprecipitate:</b> מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.</div>""", unsafe_allow_html=True)
    
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול וזיהוי שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! בולוסים של 20ml/kg עד 60ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש (כבד מוגדל, חרחורים). להימנע מנוזלים המעמיסים על הלב!<br>
        ● <b>שוק המורגי:</b> דירוג Class I-IV. Class IV = אובדן דם מעל 40%.</div>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""<div class='clinical-card'><h3>TBI וניהול ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר.<br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד (סימן להרניאציה).</div>""", unsafe_allow_html=True)

    with t4:
        st.markdown("""<div class='clinical-card'><h3>אלקטרוליטים ואינסולין</h3>
        ● <b>KCl:</b> תיקון פומי עדיף. מתן IV רק במקרים קשים. קצב מקסימלי: 40mEq/h.<br>
        ● <b>אינסולין בהחייאה:</b> מינון פוש 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין.</div>""", unsafe_allow_html=True)

elif page == "תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU Master</h1>", unsafe_allow_html=True)
    meds_db = {
        "א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: SVT - 0.1mg/kg (פלאש)", "אטרופין: ברדיקרדיה 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg", "דובוטמין: 2-20mcg"],
        "מ": ["מילרינון: 0.25-0.75mcg (Inodilator)", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg"],
        "פ": ["פוסיד: משתן 0.5-2mg/kg", "פנטניל: שיכוך כאב 1-2mcg/kg"]
    }
    col_a, col_b = st.columns(2)
    with col_a: letter = st.selectbox("בחר אות:", sorted(meds_db.keys()))
    with col_b: drug = st.selectbox(f"תרופות ב-{letter}:", meds_db[letter])
    st.markdown(f"<div class='clinical-card'>{drug}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: התדרדרות חיה</h1>", unsafe_allow_html=True)
    if st.session_state.s_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-grid'>
            <div><span style='color:#94a3b8;font-size:14px;'>HR</span><br><span class='mon-val v-hr'>196</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>BP</span><br><span class='mon-val' style='color:#fbbf24'>68/40</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>SpO2</span><br><span class='mon-val v-spo2'>89%</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>RR</span><br><span class='mon-val' style='color:white'>64</span></div>
        </div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה מאוד. +30 XP"); st.session_state.s_idx = 1; st.rerun()
