import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- CSS: RTL, Manus Style ועיצוב כותרות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; background-color: #f8fafc; }
    
    /* יישור כותרות לאמצע */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: 700; margin-bottom: 20px; }
    
    /* Manus Style Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; justify-content: center; border-bottom: 2px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: 600; font-size: 18px; }
    
    /* RTL Fix for all elements */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, label { 
        direction: RTL !important; text-align: right !important; justify-content: flex-end !important;
    }
    div[data-baseweb="select"] > div { direction: RTL !important; text-align: right !important; }

    /* המוניטור ICU */
    .icu-monitor {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 25px; border-radius: 15px; border: 4px solid #334155;
        direction: ltr; text-align: left; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin: 20px 0;
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .mon-val { font-size: 38px; font-weight: bold; }
    .v-hr { color: #ff4b4b; } .v-bp { color: #facc15; } .v-spo2 { color: #22d3ee; }

    /* כרטיסיות מידע */
    .content-card {
        background: white; border-radius: 16px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-right: 10px solid #2e59a8;
        font-size: 18px; line-height: 1.8; color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור למסד נתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    df = get_db()
    user_email = st.user.get("email")
    if user_email and user_email in df['email'].values:
        idx = df[df['email'] == user_email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.current_score = int(df.at[idx, 'score'])

# --- מערכת כניסה (Fix for AttributeError) ---
# נשתמש ב-st.user.get() כדי למנוע קריסה
is_logged_in = st.user.get("is_logged_in", False)

if not is_logged_in:
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="content-card" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("ברוכים הבאים למערכת הלמידה המחלקתית.\nאנא התחברו עם חשבון הגוגל שלכם:")
        st.login("google")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- טעינת נתוני משתמש ---
if 'current_score' not in st.session_state:
    db = get_db()
    email = st.user.get("email")
    if email in db['email'].values:
        st.session_state.current_score = int(db.loc[db['email'] == email, 'score'].values[0])
    else:
        # רישום משתמש חדש
        new_user = pd.DataFrame([{"name": st.user.get("name"), "email": email, "score": 0, "date": str(datetime.date.today())}])
        db = pd.concat([db, new_user], ignore_index=True)
        conn.update(worksheet="Sheet1", data=db)
        st.session_state.current_score = 0

# --- תפריט צד ---
with st.sidebar:
    st.image(st.user.get("picture"), width=80)
    st.markdown(f"### שלום, {st.user.get('name')}")
    st.metric("XP ניקוד מצטבר", f"{st.session_state.current_score}")
    if st.button("התנתק"): st.logout()
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "פרוטוקולים (PDF)", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢", "מבחן מעורב"])

# --- 1. דאשבורד ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה ושיאים</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("""<div class="content-card"><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        ● <b>דגש קריטי:</b> בחולים עם היפומגנזמיה והיפוקלמיה - חובה לתקן מגנזיום תחילה!<br>
        ● <b>מידע שימושי:</b> 14.9% KCl IV = 2mEq/ml. קצב מקסימלי בילדים: 0.5mEq/kg/h.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 Top 10")
        df_sorted = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(df_sorted[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

# --- 2. פרוטוקולים (Manus Tabs Style) ---
elif page == "פרוטוקולים (PDF)":
    st.markdown("<h1>ספריית ידע PICU מלאה</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🩸 המטולוגיה", "💧 אלקטרוליטים", "🧠 נוירולוגיה", "🩺 שוק וספסיס"])
    
    with t1:
        st.markdown("""<div class="content-card"><h3>פאנציטופניה ומוצרי דם</h3>
        ● <b>הגדרה:</b> ירידה בטרומבוציטופניה, נויטרופניה ואנמיה. <br>
        ● <b>טסיות (PLT):</b> התוויה < 10,000. <b>אסור לתת ב-IVAC!</b> (דחיפת הנוזל הורסת אותן). מינון: 5mg/kg.<br>
        ● <b>FFP:</b> מכיל את כל חלבוני הקרישה. סוג AB הוא התורם האוניברסלי.</div>""", unsafe_allow_html=True)
    
    with t2:
        st.markdown("""<div class="content-card"><h3>אלקטרוליטים (מבחן שיב"א)</h3>
        ● <b>אשלגן:</b> תיקון פומי עדיף. IV רק במקרים קשים. קצב מקסימלי: 40mEq/h.<br>
        ● <b>ביקרבונט:</b> בופר לדם. בילדים < שנתיים יש לדלל פי 2 עם מים להזרקה.</div>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""<div class="content-card"><h3>חבלות ראש ו-ICP</h3>
        ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60. <br>
        ● <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד (סימן להרניאציה).</div>""", unsafe_allow_html=True)

    with t4:
        st.markdown("""<div class="content-card"><h3>ניהול שוק</h3>
        ● <b>ספסיס:</b> טיפול תוך שעה! בולוסים של 20ml/kg עד 60ml/kg. <br>
        ● <b>שוק קרדיוגני:</b> סימני גודש (כבד מוגדל, חרחורים). להימנע מנוזלים!</div>""", unsafe_allow_html=True)

# --- 3. ספריית תרופות (גלגלת לבחירה) ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU</h1>", unsafe_allow_html=True)
    meds_data = {
        "א": ["אדרנלין: החייאה 0.01mg/kg / סטרידור 400mcg/kg", "אדנוזין: 0.1mg/kg פלאש מהיר", "אטרופין: 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg", "דובוטמין: 2-20mcg/kg/min"],
        "מ": ["מילרינון: 0.25-0.75mcg/kg/min", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg"],
        "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: 1-2mcg/kg", "פרופופול: 2.5-3.5mg/kg"]
    }
    
    # גלגלת לבחירת אות
    sel_letter = st.selectbox("בחר אות ראשונה:", sorted(meds_data.keys()))
    # גלגלת לבחירת תרופה
    sel_drug = st.selectbox(f"בחר תרופה באות {sel_letter}:", meds_data[sel_letter])
    st.markdown(f'<div class="content-card">{sel_drug}</div>', unsafe_allow_html=True)

# --- 4. תרחיש מתגלגל (Visual Experience) ---
elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה</h1>", unsafe_allow_html=True)
    if 'sc_step' not in st.session_state: st.session_state.sc_step = 0
    
    if st.session_state.sc_step == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד **חיוור מאוד ואפטי**.")
        st.markdown("""<div class="icu-monitor"><div class="mon-grid">
            <div><span class="mon-label">HR</span><br><span class="mon-val v-hr">194</span></div>
            <div><span class="mon-label">BP</span><br><span class="mon-val v-bp">68/40</span></div>
            <div><span class="mon-label">SpO2</span><br><span class="mon-val v-spo2">89%</span></div>
            <div><span class="mon-label">RR</span><br><span class="mon-val">62</span></div>
        </div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי?", ["דימום מוחי", "Leukostasis (חסימה מכנית)", "ספסיס"], key="sc_q1")
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון! +20 XP"); st.session_state.sc_step = 1; st.rerun()

    elif st.session_state.sc_step == 1:
        st.warning("**מצב:** תוך כדי הידרציה, מופיעה אריתמיה. אשלגן 7.2. הילד עם **רעד בגפיים**.")
        st.markdown("""<div class="icu-monitor"><div class="mon-val v-hr">! ARRYTHMIA !</div><div class="mon-val">HR: 215</div></div>""", unsafe_allow_html=True)
        ans = st.radio("טיפול דחוף להגנה על הלב?", ["פוסיד", "קלציום גלוקונט IV", "אלופורינול"], key="sc_q2")
        if st.button("טפל"):
            if "קלציום" in ans: st.success("נכון מאוד!"); st.session_state.sc_step = 2; st.rerun()

    elif st.session_state.sc_step == 2:
        st.error("**מצב:** הילד מתנשם בכבדות. **חרחורים** בריאות, כבד מוגדל ב-4 ס''מ.")
