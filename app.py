import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- 1. הגדרות דף ו-RTL אבסולוטי ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# CSS: Manus Style + RTL Fix + ICU Monitor
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        font-family: 'Assistant', sans-serif; direction: RTL !important; text-align: right !important; 
    }
    
    /* כותרות Manus - ממורכזות */
    h1, h2, h3, h4 { text-align: center !important; color: #0f172a; font-weight: 800; margin-top: 20px; }
    
    /* עיצוב כרטיסיות מידע (Clean Manus Style) */
    .clinical-card {
        background: white; border-radius: 20px; padding: 40px; margin-bottom: 25px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border-right: 12px solid #2e59a8; 
        line-height: 2; font-size: 20px; color: #1e293b; 
    }

    /* מוניטור ICU שחור-ניאון */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 35px; border-radius: 20px; border: 5px solid #334155;
        direction: ltr; text-align: left; box-shadow: 0 10px 40px rgba(0,0,0,0.7); margin: 25px 0;
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
    .mon-val { font-size: 50px; font-weight: bold; }
    .c-hr { color: #f87171; } .c-bp { color: #fbbf24; } .c-spo2 { color: #22d3ee; }

    /* יישור טבלאות וגלגלות */
    div[data-baseweb='select'] > div { direction: RTL !important; text-align: right !important; }
    div[data-testid='stTable'] { direction: RTL !important; }
    th { text-align: right !important; background-color: #f1f5f9 !important; }
    
    /* עיצוב כפתור כניסה גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; border: 1px solid #ddd !important; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. חיבור ל-Database ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    email = st.user.email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = int(df.at[idx, 'score'])

# --- 3. מערכת כניסה מאובטחת ---
if not st.user.get("is_logged_in", False):
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("ברוכים הבאים למערכת הלמידה המחלקתית. לכניסה מאובטחת ושמירת ניקוד המיילים המאומתים שלכם:")
        try:
            st.login("google")
        except:
            st.error("תקלת אבטחה: פרטי Google Client ID לא מוגדרים ב-Secrets של האתר.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון התחלתי של המשתמש
if 'u_score' not in st.session_state:
    db = get_db()
    if st.user.email in db['email'].values:
        st.session_state.u_score = int(db.loc[db['email'] == st.user.email, 'score'].values[0])
    else:
        # רישום משתמש חדש
        new_row = pd.DataFrame([{"name": st.user.name, "email": st.user.email, "score": 0, "date": str(datetime.date.today())}])
        db = pd.concat([db, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=db)
        st.session_state.u_score = 0

# --- 4. תפריט ואתר ---
with st.sidebar:
    st.image(st.user.picture, width=70)
    st.markdown(f"### שלום, {st.user.name}")
    st.metric("XP - ניקוד למידה", f"{st.session_state.u_score} 🏆")
    if st.button("יציאה מהחשבון"): st.logout()
    st.divider()
    page = st.radio("תפריט למידה:", ["דאשבורד ושיאים", "פרוטוקולים מלאים (PDF)", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢"])

# --- 5. דף דאשבורד ---
if page == "דאשבורד ושיאים":
    st.markdown("<h1>לוח בקרה ודירוג מחלקתי</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class='clinical-card'><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש מהסיכום:</b> חולים הסובלים במקביל מהיפומגנזמיה והיפוקלמיה - <b>חובה לתקן מגנזיום תחילה!</b><br>
        ● <b>מידע IV:</b> 14.9% KCl IV = 2mEq/ml. קצב מקסימלי בילדים: 0.5mEq/kg/h (מקסימום 40mEq/h).</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top Leaders")
        df_list = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(df_list[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

# --- 6. מרכז ידע (Full OCR Content) ---
elif page == "פרוטוקולים מלאים (PDF)":
    st.markdown("<h1>ספריית הידע PICU - הכל מתוךUpToDate</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "🩺 שוק וספסיס", "🧠 נוירולוגיה", "💧 אלקטרוליטים"])
    
    with t1:
        st.markdown("""<div class='clinical-card'><h3>פאנציטופניה ומוצרי דם</h3>
        ● <b>פאנציטופניה:</b> ירידה ב-PLT, נויטרופילים ואנמיה. גורמים: לוקמיה, אנמיה אפלסטית.<br>
        ● <b>טסיות:</b> מתן < 10,000. <b>איסור מוחלט על IVAC:</b> הורס את הטסיות בדחיפה. מינון: 5mg/kg.<br>
        ● <b>FFP (פלזמה):</b> תורם אוניברסלי מסוג AB. אין צורך בהקרנה. <br>
        ● <b>Cryoprecipitate:</b> פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.</div>""", unsafe_allow_html=True)
    
    with t2:
        st.markdown("""<div class='clinical-card'><h3>ניהול וזיהוי שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! בולוסים של 20ml/kg עד 60ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש (כבד מוגדל, חרחורים). להימנע מנוזלים המעמיסים על הלב!<br>
        ● <b>שוק המורגי:</b> דירוג Class I-IV. Class IV = אובדן דם מעל 40%, ל"ד צלול.</div>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""<div class='clinical-card'><h3>TBI וניהול ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר.<br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד (סימן להרניאציה).</div>""", unsafe_allow_html=True)

# --- 7. ספריית תרופות (Dropdown Selection) ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU Master</h1>", unsafe_allow_html=True)
    meds_db = {
        "א": ["אדרנלין: 0.01mg/kg החייאה / 400mcg/kg (סטרידור)", "אדנוזין: SVT - 0.1mg/kg (פלאש)", "אטרופין: ברדיקרדיה 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: סטרידור 0.6mg/kg", "דובוטמין: 2-20mcg/kg/min"],
        "מ": ["מילרינון: 0.25-0.75mcg (Inodilator)", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg (כאב)"],
        "פ": ["פוסיד: משתן 0.5-2mg/kg", "פנטניל: שיכוך כאב 1-2mcg/kg", "פרופופול: הרדמה 2.5-3.5mg/kg"]
    }
    col_a, col_b = st.columns(2)
    with col_a: 
        letter = st.selectbox("בחר אות ראשונה:", sorted(meds_db.keys()))
    with col_b: 
        drug = st.selectbox(f"תחרות באות {letter}:", meds_db[letter])
    st.markdown(f"<div class='clinical-card'>{drug}</div>", unsafe_allow_html=True)

# --- 8. תרחיש מתגלגל (The Simulation) ---
elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה חיה</h1>", unsafe_allow_html=True)
    if 's_step' not in st.session_state: st.session_state.s_step = 0
    
    if st.session_state.s_step == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים הגיע עם AML, WBC 810,000. הילד **חיוור, אפרורי ואפטי**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-grid'>
            <div><span style='color:#94a3b8;font-size:14px;'>HEART RATE</span><br><span class='mon-val c-hr'>196</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>BP SYSTOLIC</span><br><span class='mon-val' style='color:#fbbf24'>68</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>SPO2</span><br><span class='mon-val c-spo2'>89%</span></div>
            <div><span style='color:#94a3b8;font-size:14px;'>TEMP</span><br><span class='mon-val' style='color:white'>38.4</span></div>
        </div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי?", ["דימום פנימי", "Leukostasis (חסימה מכנית)", "ספסיס ויראלי"], key="q1")
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון! +30 XP"); st.session_state.s_step = 1; st.rerun()

    elif st.session_state.s_step == 1:
        st.warning("**מצב:** תוך כדי החלטה על טיפול נוזלי, המטופל מפתח אריתמיה במוניטור. אשלגן 7.2. הילד עם **רעד בגפיים**.")
        st.markdown("""<div class='icu-monitor'><div class='mon-val c-hr'>! ARRYTHMIA DETECTED !</div><div class='mon-val'>HR: 215</div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה הפעולה הדחופה ביותר להגנה על הלב?", ["פוסיד", "קלציום גלוקונט IV", "אלופורינול פומי"], key="q2")
        if st.button("בצע טיפול"):
            if ans == "קלציום גלוקונט IV": st.success("נכון מאוד! קלציום מגן על ממברנת הלב מהיפרקלמיה."); st.session_state.s_step = 2; st.rerun()

    elif st.session_state.s_step == 2:
        st.error("**מצב:** הילד מתנשם בכבדות. בהאזנה: **חרחורים (Rales)**. כבד נמוש 4 ס''מ (Liver drop).")
        st.write("**שאלה קלינית:** מהי האבחנה כעת ומה הפעולה?")
        ans = st.radio("בחר החלטה:", ["שוק ספטי - מתן בולוס נוזלים", "שוק קרדיוגני - התחלת אמינים ועצירת נוזלים", "שוק היפוולמי - מתן דם"], key="q3")
        if st.button("סיום תרחיש"):
            if "קרדיוגני" in ans: st.balloons(); update_xp(50); st.success("מצוין! זיהית fluid overload בשוק קרדיוגני. הצלת את החולה!"); st.session_state.s_step = 0
