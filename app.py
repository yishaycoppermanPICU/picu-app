import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- CSS: עיצוב "Manus AI" משופר ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; background-color: #f8fafc; }
    
    /* יישור כותרות */
    h1, h2, h3 { text-align: center !important; color: #0f172a; font-weight: 700; }
    
    /* כרטיסיות Manus-Style */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; font-size: 16px; color: #64748b; }
    .stTabs [aria-selected="true"] { color: #2e59a8 !important; border-bottom: 3px solid #2e59a8 !important; }

    /* מוניטור ICU */
    .icu-monitor {
        background-color: #000;
        color: #39ff14;
        font-family: 'Share Tech Mono', monospace;
        padding: 25px;
        border: 5px solid #334155;
        border-radius: 15px;
        direction: ltr;
        text-align: left;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        margin: 20px 0;
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .mon-label { font-size: 14px; color: #94a3b8; }
    .mon-val { font-size: 32px; font-weight: bold; }
    .val-red { color: #f87171; } .val-cyan { color: #22d3ee; } .val-yellow { color: #fbbf24; }

    /* כרטיסיות תוכן */
    .clinical-card {
        background: white; border-radius: 12px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-right: 6px solid #2e59a8;
        line-height: 1.8; font-size: 17px; color: #1e293b;
    }
    
    /* כפתורים */
    .stButton>button { 
        width: 100%; border-radius: 10px; background: #2e59a8; color: white; 
        font-weight: 600; height: 3.5em; border: none; transition: 0.2s;
    }
    .stButton>button:hover { background: #1e3d59; box-shadow: 0 4px 12px rgba(46, 89, 168, 0.3); }

    /* Sidebar Fix */
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; background-color: #f1f5f9; }
    </style>
    """, unsafe_allow_html=True)

# --- לוגיקת בסיס נתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_score(points):
    df = get_data()
    email = st.session_state.user_email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.user_score = int(df.at[idx, 'score'])

# --- מסך כניסה ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1>🏥 PICU Master Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="clinical-card" style="border:none; text-align:center;">', unsafe_allow_html=True)
        name = st.text_input("שם מלא:")
        email = st.text_input("אימייל:")
        if st.button("כניסה למערכת"):
            if name and email:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.session_state.user_email = email
                db = get_data()
                st.session_state.user_score = int(db.loc[db['email'] == email, 'score'].values[0]) if email in db['email'].values else 0
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- תפריט צד ---
with st.sidebar:
    st.markdown(f"### שלום, {st.session_state.user_name}")
    st.metric("XP ניקוד למידה", f"{st.session_state.user_score}")
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "פרוטוקולים קליניים", "ספריית תרופות", "תרחיש מתגלגל 🎢", "ניהול"])
    if st.button("יציאה"): st.session_state.logged_in = False; st.rerun()

# --- דף דאשבורד ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה לימודי</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown("""<div class="clinical-card"><h3>💊 תרופת היום: Adenosine</h3>
        לטיפול ב-SVT. <b>דגש קריטי:</b> זמן מחצית חיים פחות מ-10 שניות. חייבים להזריק הכי קרוב ללב (וריד מרכזי/ג'וגולר) בשטיפה מהירה (Flash).</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("### 🏆 טבלת שיאים")
        df = get_data().sort_values(by="score", ascending=False).head(5)
        st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

# --- דף פרוטוקולים (מבנה טאבים כמו במאנוס) ---
elif page == "פרוטוקולים קליניים":
    st.markdown("<h1>מרכז הידע PICU</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🩸 המטולוגיה", "💧 אלקטרוליטים", "🧠 נוירולוגיה (TBI)"])
    
    with t1:
        st.markdown("""<div class="clinical-card">
        <h3>מוצרי דם ו-TLS</h3>
        <b>טסיות (PLT):</b> התוויה מתחת ל-10,000. אסור לתת ב-IVAC (הלחץ הורס אותן). מינון: 5mg/kg.<br><br>
        <b>FFP:</b> תורם אוניברסלי - סוג AB (אין בו נוגדנים).<br><br>
        <b>Tumor Lysis Syndrome:</b> היפרקלמיה, היפרפוספטמיה, היפוקלצמיה, היפראוריצמיה.
        </div>""", unsafe_allow_html=True)
        
    with t2:
        st.markdown("""<div class="clinical-card">
        <h3>תיקון אלקטרוליטים (שיב"א)</h3>
        <b>אשלגן:</b> רמות 3.5-5. חובה לתקן מגנזיום תחילה למניעת היפוקלמיה עמידה.<br><br>
        <b>סודיום ביקרבונט:</b> בילדים מתחת לגיל שנתיים - לדלל פי 2 עם מים להזרקה.
        </div>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""<div class="clinical-card">
        <h3>ניהול ICP וחבלות ראש</h3>
        <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60.<br><br>
        <b>טריאדת קושינג:</b> ברדיקרדיה, שינויי נשימה, יתר ל"ד. סימן להרניאציה.<br><br>
        <b>טיפול:</b> ראש ב-30 מעלות, מנח נייטרלי, סליין 3% (5cc/kg).
        </div>""", unsafe_allow_html=True)

# --- תרחיש מתגלגל 🎢 ---
elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה קלינית חיה</h1>", unsafe_allow_html=True)
    if 'step' not in st.session_state: st.session_state.step = 0
    
    if st.session_state.step == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, לבנים 810,000. הילד אפרורי ואפטי.")
        st.markdown("""<div class="icu-monitor">
            <div class="mon-grid">
                <div><span class="mon-label">HR</span><br><span class="mon-val val-red">194</span></div>
                <div><span class="mon-label">BP</span><br><span class="mon-val val-yellow">70/42</span></div>
                <div><span class="mon-label">SpO2</span><br><span class="mon-val val-cyan">88%</span></div>
                <div><span class="mon-label">RR</span><br><span class="mon-val">62</span></div>
            </div>
        </div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי שלך?", ["דימום מוחי", "Leukostasis", "ספסיס"])
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון!"); st.session_state.step = 1; st.rerun()
            
    elif st.session_state.step == 1:
        st.warning("**מצב:** הילד מקבל הידרציה. מעבדה: Potassium 7.2. הילד מפתח אריתמיה במוניטור.")
        st.markdown("""<div class="icu-monitor"><div class="mon-val val-red">! ARRYTHMIA DETECTED !</div><div class="mon-val">HR: 215</div></div>""", unsafe_allow_html=True)
        ans = st.radio("טיפול דחוף להגנה על הלב?", ["פוסיד", "קלציום גלוקונט IV", "אלופורינול"])
        if st.button("טפל"):
            if "קלציום" in ans: st.success("מצוין!"); st.session_state.step = 2; st.rerun()

    elif st.session_state.step == 2:
        st.error("**מצב:** הילד מתנשם בכבדות, חרחורים בריאות, כבד נמוש 4 ס''מ.")
        ans = st.radio("אבחנה?", ["שוק ספטי", "שוק קרדיוגני", "שוק היפוולמי"])
        if st.button("סיום תרחיש"):
            if "קרדיוגני" in ans: st.balloons(); update_score(50); st.session_state.step = 0

# --- ספריית תרופות ABC ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות</h1>", unsafe_allow_html=True)
    letter = st.select_slider("בחר אות:", options=["א", "ב", "ד", "מ", "פ", "ק"])
    meds = {"א": ["אדרנלין: 0.01mg/kg", "אדנוזין: 0.1mg/kg", "אטרופין: 0.02mg/kg"], "ד": ["דופמין: 1-20mcg", "דקסמתזון: 0.6mg/kg"]}
    for m in meds.get(letter, []): st.markdown(f'<div class="clinical-card">{m}</div>', unsafe_allow_html=True)

# --- פאנל ניהול ---
elif page == "ניהול":
    pwd = st.text_input("סיסמת מנהל:", type="password")
    if pwd == "PICU123":
        st.success("גישת מנהל מאושרת")
        st.dataframe(get_data())
