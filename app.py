import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. הגדרות דף ויישור לימין (RTL) אגרסיבי ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# איתחול משתנים קריטי למניעתAttributeError
if 'u_score' not in st.session_state: st.session_state.u_score = 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    /* יישור לימין לכל שטח האתר */
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* מרכוז כותרות Manus */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #011f4b; font-weight: 800; margin-top: 0px; }
    
    /* מניעת רווחים לבנים למעלה */
    .block-container { padding-top: 1.5rem !important; }

    /* כרטיסיות מידע Manaus Style - תוכן מלא מהסיכומים */
    .clinical-card {
        background: white; border-radius: 16px; padding: 40px; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8;
        line-height: 2.2; font-size: 20px; color: #1e293b;
    }

    /* מוניטור ICU שחור-ניאון */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; direction: ltr; text-align: left;
        box-shadow: inset 0 0 15px #000, 0 10px 25px rgba(0,0,0,0.4); margin: 20px 0;
    }
    .mon-val { font-size: 50px; font-weight: bold; }
    .hr { color: #f87171; } .bp { color: #fbbf24; } .spo2 { color: #22d3ee; }

    /* גלגלות מיושרות לימין */
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }
    
    /* כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 55px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. לוגיקת נתונים (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    email = st.user.get("email")
    if email and email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = int(df.at[idx, 'score'])

# --- 3. כניסה מאובטחת (Google Auth בלבד -Verified) ---
# בדיקת כניסה יציבה למניעת AttributeError
user_authenticated = st.user.get("is_logged_in", False)

if not user_authenticated:
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("### ברוכים הבאים למערכת הלמידה המרכזית")
        st.write("נא להתחבר עם חשבון גוגל מאומת לצורך גישה לספריית הפרוטוקולים ושמירת הניקוד:")
        st.login("google")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון ניקוד מהגיליון לאחר כניסה
if st.session_state.u_score == 0:
    db = get_db()
    u_email = st.user.get("email")
    if u_email in db['email'].values:
        st.session_state.u_score = int(db.loc[db['email'] == u_email, 'score'].values[0])
    else:
        # רישום ראשוני בגיליון
        new_row = pd.DataFrame([{"name": st.user.get("name"), "email": u_email, "score": 0, "date": str(datetime.date.today())}])
        df_new = pd.concat([db, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=df_new)

# --- 4. תפריט ואתר ---
with st.sidebar:
    st.image(st.user.get("picture", ""), width=70)
    st.markdown(f"### שלום, {st.user.get('name')}")
    st.metric("XP ניקוד מצטבר", st.session_state.u_score)
    st.divider()
    page = st.radio("בחר אזור למידה:", ["דאשבורד ושיאים", "פרוטוקולים מלאים (PDF)", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה מהמערכת"): st.logout()

# --- 5. תוכן האתר (מילה במילה מהסיכומים שלך) ---

if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה ודירוג מחלקתי</h1>", unsafe_allow_html=True)
    ldb = get_db().sort_values(by="score", ascending=False).head(10)
    st.table(ldb[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "פרוטוקולים מלאים (PDF)":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    with t1: 
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ירידה משמעותית בטרומבוציטופניה, נויטרופניה ואנמיה (פאנציטופניה).<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור מוחלט על IVAC:</b> הלחץ מועך את הטסיות. מינון: 5mg/kg.<br>
        ● <b>FFP:</b> תורם אוניברסלי סוג AB. נשמר שנה במינוס 20 מעלות.</div>""", unsafe_allow_html=True)
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

elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות - גלגלת בחירה</h1>", unsafe_allow_html=True)
    meds_full = {
        "א": ["אדרנלין: החייאה 0.01mg/kg / סטרידור 400mcg/kg", "אדנוזין: SVT - 0.1mg/kg (פלאש)", "אטרופין: ברדיקרדיה 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg", "דובוטמין: 2-20mcg/kg/min"],
        "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: שיכוך כאב 1-2mcg/kg"]
    }
    col_a, col_b = st.columns(2)
    with col_a: l = st.selectbox("בחר אות:", sorted(meds_full.keys()))
    with col_b: d = st.selectbox(f"תרופות באות '{l}':", meds_full[l])
    st.markdown(f"<div class='clinical-card'>{d}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: התדרדרות חיה</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-val hr'>HR: 196 | BP: 68/40 | SpO2: 89%</div></div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה מאוד עקב עומס תאים. +30 XP"); update_db_score(30); st.session_state.sc_idx = 1; st.rerun()
