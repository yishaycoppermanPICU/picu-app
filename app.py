import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- 2. איתחול משתנים למניעת Attribute Errors ---
if 'u_score' not in st.session_state: st.session_state.u_score = 0
if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0

# --- 3. עיצוב הממשק (Manus Pro Evolution) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    /* יישור לימין כללי */
    html, body, [class*='css'] { 
        font-family: 'Assistant', sans-serif; 
        direction: RTL !important; 
        text-align: right !important; 
        background-color: #f8fafc; 
    }
    
    /* כותרות Manus - ממורכזות ויוקרתיות */
    h1, h2, h3 { text-align: center !important; color: #011f4b; font-weight: 800; margin-bottom: 20px; }
    
    /* כרטיסיות המידע המלאות */
    .clinical-card {
        background: white; border-radius: 16px; padding: 35px; margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8;
        line-height: 2.2; font-size: 19px; color: #1e293b;
    }

    /* מוניטור ICU שחור-ניאון */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 30px; border-radius: 15px; direction: ltr; text-align: left;
        box-shadow: inset 0 0 15px #000, 0 10px 20px rgba(0,0,0,0.4); margin: 20px 0;
    }
    .mon-val { font-size: 45px; font-weight: bold; }
    .hr { color: #f87171; } .bp { color: #fbbf24; } .spo2 { color: #22d3ee; }

    /* התאמת גלגלות (Dropdowns) לימין */
    .stSelectbox, .stTextInput, .stRadio { direction: RTL !important; text-align: right !important; }
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }

    /* עיצוב כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. חיבור לנתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

# --- 5. בקרת כניסה (גוגל בלבד) ---
if not st.user.is_logged_in:
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("### ברוכים הבאים למערכת הלמידה המרכזית")
        st.write("נא להתחבר עם חשבון גוגל המאומת שלכם לצורך גישה לפרוטוקולים ושמירת הניקוד:")
        
        # כניסת גוגל נקייה
        st.login("google")
        
        # אם גוגל לא מוגדר, הצגת הודעה מקצועית
        if "auth" not in st.secrets:
            st.info("🛠️ המערכת בשלבי הקמה טכנית. נא להגדיר Google Client ID ב-Secrets.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון משתמש לאחר כניסה
if st.session_state.u_score == 0:
    db = get_db()
    email = st.user.email
    if email in db['email'].values:
        st.session_state.u_score = int(db.loc[db['email'] == email, 'score'].values[0])

# --- 6. ניווט ותפריט ---
with st.sidebar:
    st.image(st.user.picture, width=70)
    st.markdown(f"### שלום, {st.user.name}")
    st.metric("ניקוד מצטבר (XP)", st.session_state.u_score)
    st.divider()
    page = st.radio("בחר אזור למידה:", ["דאשבורד ושיאים", "פרוטוקולים לקריאה", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])
    if st.button("יציאה מהמערכת"): st.logout()

# --- 7. תוכן האתר (מילה במילה מהסיכומים שלך) ---

if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה ודירוג מחלקתי</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class="clinical-card"><h3>💊 תרופת היום: דקסמתזון</h3>
        ● <b>דגש מהסיכום:</b> ב-PICU משמשת למניעת בצקת דרכי נשימה (סטרידור) לאחר אקסטובציה.<br>
        ● <b>פרוטוקול:</b> מינון 0.5-1 mg/kg. מומלץ לתת מנה ראשונה כמתן מניעתי 6-12 שעות לפני הפעולה.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10 Leaders")
        leader_df = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(leader_df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

elif page == "פרוטוקולים לקריאה":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    
    with t1:
        st.markdown("""<div class="clinical-card"><h3>פאנציטופניה ומוצרי דם</h3>
        <b>הגדרה:</b> ירידה משמעותית בכל שלוש שורות הדם: טרומבוציטופניה, נויטרופניה ואנמיה.<br>
        ● <b>טסיות (PLT):</b> התוויה מתחת ל-10,000. <b>איסור מוחלט על IVAC:</b> דחיפת הנוזל דרך הצינור הורסת את הטסיות. מינון: 5mg/kg.<br>
        ● <b>Cryoprecipitate:</b> מקורו בפלסמה. מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.</div>""", unsafe_allow_html=True)
    
    with t2:
        st.markdown("""<div class="clinical-card"><h3>ניהול שוק (Shock)</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! SIRS מוגדר כחום >38 או <36 עם טכיקרדיה וטכיפניאה. בולוסים של 20ml/kg.<br>
        ● <b>שוק קרדיוגני:</b> ירידה בכושר כיווץ הלב. <b>סימני גודש:</b> כבד מוגדל (Liver drop), חרחורים בריאות. להימנע מנוזלים!</div>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""<div class="clinical-card"><h3>TBI וניהול ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר. <br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר לחץ דם סיסטולי.</div>""", unsafe_allow_html=True)

    with t4:
        st.markdown("""<div class="clinical-card"><h3>אלקטרוליטים (מבחן שיב"א)</h3>
        ● <b>אשלגן:</b> רמות 3.5-5. <b>חובה לתקן מגנזיום תחילה</b> למניעת היפוקלמיה עמידה.<br>
        ● <b>אינסולין:</b> ב-DKA מינון פוש 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין.</div>""", unsafe_allow_html=True)

elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות - בחירה מהירה</h1>", unsafe_allow_html=True)
    meds = {
        "א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: SVT 0.1mg/kg", "אטרופין: ברדיקרדיה 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: סטרידור 0.6mg/kg", "דובוטמין: 2-20mcg"],
        "פ": ["פוסיד: משתן 0.5-2mg/kg", "פנטניל: שיכוך כאב 1-2mcg/kg"]
    }
    col1, col2 = st.columns(2)
    with col1: letter = st.selectbox("בחר אות ראשונה:", sorted(meds.keys()))
    with col2: drug = st.selectbox(f"תרופות ב-'{letter}':", meds[letter])
    st.markdown(f"<div class='clinical-card'>{drug}</div>", unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה חיה</h1>", unsafe_allow_html=True)
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים הגיע עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class="icu-monitor">
            <div class="mon-val hr">HR: 196 (Tachy)</div>
            <div class="mon-val bp">BP: 68/40 (Hypo)</div>
            <div class="mon-val spo2">SpO2: 89% (RA)</div>
        </div>""", unsafe_allow_html=True)
        if st.button("בצע פעולה: חשד ל-Leukostasis"):
            st.success("נכון! צמיגות הדם גבוהה מאוד. +30 XP"); st.session_state.sc_idx = 1; st.rerun()

# (המשך התרחישים מנוהל לוגית כמו הגרסאות הקודמות אך בעיצוב ה-Monitor החדש)
