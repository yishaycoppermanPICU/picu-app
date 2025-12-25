import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- CSS: Manus AI Evolution + RTL Fix ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; background-color: #f8fafc; }
    
    /* כותרות Manus-Style */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #0f172a; font-weight: 700; margin-top: 10px; }
    
    /* יישור רכיבי טופס לימין */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        direction: RTL !important; text-align: right !important; 
    }
    div[data-baseweb="select"] { direction: RTL !important; }

    /* כרטיסיות מידע מקצועיות */
    .clinical-card {
        background: white; border-radius: 16px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-right: 10px solid #2e59a8;
        line-height: 1.8; font-size: 18px; color: #1e293b;
    }
    
    /* מוניטור ICU ויזואלי */
    .monitor-box {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 25px; border-radius: 15px; border: 4px solid #334155;
        direction: ltr; text-align: left; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin: 20px 0;
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .mon-val { font-size: 42px; font-weight: bold; }
    .v-hr { color: #ff4b4b; } .v-bp { color: #facc15; } .v-spo2 { color: #22d3ee; }

    /* כפתור גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- לוגיקת חיבור נתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    email = st.session_state.get("user_email")
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.user_score = int(df.at[idx, 'score'])

# --- מערכת כניסה חכמה (Fallback Mechanism) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("לכניסה ושמירת התקדמות, אנא התחברו:")
        
        # ניסיון כניסה עם גוגל - אם נכשל, עובר לטופס
        try:
            st.login("google")
            if st.user.is_logged_in:
                st.session_state.logged_in = True
                st.session_state.user_name = st.user.name
                st.session_state.user_email = st.user.email
                st.rerun()
        except:
            st.warning("התחברות גוגל לא מוגדרת. השתמש בכניסה מהירה:")
            u_name = st.text_input("שם מלא:")
            u_email = st.text_input("אימייל:")
            if st.button("כניסה"):
                if u_name and u_email:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u_name
                    st.session_state.user_email = u_email
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון ניקוד
if 'user_score' not in st.session_state:
    db = get_db()
    st.session_state.user_score = int(db.loc[db['email'] == st.session_state.user_email, 'score'].values[0]) if st.session_state.user_email in db['email'].values else 0

# --- תפריט צד ---
with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_name}")
    st.metric("XP - ניקוד למידה", st.session_state.user_score)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "פרוטוקולים (PDF)", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢", "מבחן מעורב"])
    if st.button("התנתק"): st.session_state.logged_in = False; st.rerun()

# --- 1. דאשבורד ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה ושיאים</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class="clinical-card"><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש קריטי:</b> בחולים עם היפומגנזמיה והיפוקלמיה במקביל - <b>חובה לתקן מגנזיום תחילה!</b><br>
        ● <b>מידע שימושי:</b> 14.9% KCl IV = 2mEq/ml. קצב מקסימלי בילדים: 0.5mEq/kg/h.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10")
        df_sorted = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(df_sorted[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

# --- 2. פרוטוקולים (Full PDF Content) ---
elif page == "פרוטוקולים (PDF)":
    st.markdown("<h1>מרכז הידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "💧 אלקטרוליטים", "🧠 נוירולוגיה", "🩺 שוק וספסיס"])
    
    with t1:
        st.markdown("""<div class="clinical-card"><h3>פאנציטופניה ומוצרי דם</h3>
        ● <b>הגדרה:</b> ירידה בטרומבוציטופניה, נויטרופניה ואנמיה. <br>
        ● <b>טסיות (PLT):</b> התוויה < 10,000. <b>אסור לתת ב-IVAC!</b> (הלחץ הורס אותן). מינון: 5mg/kg.<br>
        ● <b>Cryoprecipitate:</b> מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.<br>
        ● <b>FFP:</b> מכיל את כל חלבוני הקרישה. סוג AB הוא התורם האוניברסלי.</div>""", unsafe_allow_html=True)
    
    with t2:
        st.markdown("""<div class="clinical-card"><h3>אלקטרוליטים ואינסולין</h3>
        ● <b>אשלגן:</b> תיקון פומי עדיף. IV רק במקרים קשים. קצב מקסימלי: 40mEq/h.<br>
        ● <b>אינסולין בהחייאה:</b> מינון פוש 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין.<br>
        ● <b>ביקרבונט:</b> בופר לדם. בילדים < שנתיים יש לדלל פי 2.</div>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""<div class="clinical-card"><h3>חבלות ראש ו-ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד (סימן להרניאציה).<br>
        ● <b>ניהול:</b> הרמת ראש 30 מעלות, מנח ישר, סליין 3% (5cc/kg) או מניטול.</div>""", unsafe_allow_html=True)

    with t4:
        st.markdown("""<div class="clinical-card"><h3>ניהול שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! בולוסים של 20ml/kg עד 60ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש (כבד מוגדל, חרחורים). <b>להימנע מנוזלים!</b></div>""", unsafe_allow_html=True)

# --- 3. ספריית תרופות ABC (גלגלת) ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות</h1>", unsafe_allow_html=True)
    meds_data = {
        "א": ["אדרנלין: החייאה 0.01mg/kg / סטרידור 400mcg/kg", "אדנוזין: 0.1mg/kg פלאש מהיר", "אטרופין: 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg", "דובוטמין: 2-20mcg/kg/min"],
        "מ": ["מילרינון: 0.25-0.75mcg/kg/min", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg"],
        "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: 1-2mcg/kg", "פרופופול: 2.5-3.5mg/kg"]
    }
    
    col_l, col_d = st.columns(2)
    with col_l:
        sel_letter = st.selectbox("בחר אות ראשונה:", sorted(meds_data.keys()))
    with col_d:
        sel_drug = st.selectbox(f"בחר תרופה באות {sel_letter}:", meds_data[sel_letter])
    
    st.markdown(f'<div class="clinical-card">{sel_drug}</div>', unsafe_allow_html=True)

# --- 4. תרחיש מתגלגל (Visual Experience) ---
elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: התדרדרות מהירה</h1>", unsafe_allow_html=True)
    if 'sc_idx' not in st.session_state: st.session_state.sc_idx = 0
    
    if st.session_state.sc_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור מאוד ואפטי**.")
        st.markdown("""<div class="monitor-box"><div class="mon-grid">
            <div><span style="color:#94a3b8; font-size:14px;">HR</span><br><span class="mon-val v-hr">194</span></div>
            <div><span style="color:#94a3b8; font-size:14px;">BP</span><br><span class="mon-val v-bp">68/40</span></div>
            <div><span style="color:#94a3b8; font-size:14px;">SpO2</span><br><span class="mon-val v-spo2">89%</span></div>
            <div><span style="color:#94a3b8; font-size:14px;">RR</span><br><span class="mon-val" style="color:white">62</span></div>
        </div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי?", ["דימום מוחי", "Leukostasis (חסימה מכנית)", "ספסיס"], key="q1")
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון! +20 XP"); st.session_state.sc_idx = 1; st.rerun()

    elif st.session_state.sc_idx == 1:
        st.warning("**מצב:** תוך כדי הידרציה, מופיעה אריתמיה. אשלגן 7.2. הילד עם **רעד בגפיים**.")
        st.markdown("""<div class="monitor-box"><div class="mon-val v-hr">! ARRYTHMIA !</div><div class="mon-val">HR: 215</div></div>""", unsafe_allow_html=True)
        ans = st.radio("טיפול דחוף להגנה על הלב?", ["פוסיד", "קלציום גלוקונט IV", "אלופורינול"], key="q2")
        if st.button("טפל"):
            if "קלציום" in ans: st.success("נכון מאוד!"); st.session_state.sc_idx = 2; st.rerun()

    elif st.session_state.sc_idx == 2:
        st.error("**מצב:** הילד מתנשם בכבדות. **חרחורים** בריאות, כבד מוגדל ב-4 ס''מ.")
        ans = st.radio("אבחנה ופעולה?", ["שוק ספטי - נוזלים", "שוק קרדיוגני - אמינים", "שוק היפוולמי - דם"], key="q3")
        if st.button("סיום תרחיש"):
            if "קרדיוגני" in ans: 
                st.balloons(); update_xp(50); st.success("מצוין! זיהית fluid overload בשוק קרדיוגני."); st.session_state.sc_idx = 0
