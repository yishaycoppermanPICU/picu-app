import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥")

# --- בקרה 1: יישור לימין (RTL) והנדסת ממשק Manus ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; background-color: #f8fafc; }
    
    /* יישור כותרות לאמצע */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: 700; margin-top: 10px; }
    
    /* הנדסת כרטיסיות (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; border-bottom: 2px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: 600; font-size: 17px; }
    
    /* יישור טקסט רץ ורכיבי טפסים */
    .stMarkdown, .stText, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander { direction: RTL !important; text-align: right !important; }
    
    /* מוניטור ICU משופר */
    .monitor-panel {
        background-color: #000; color: #39ff14; font-family: 'Share Tech Mono', monospace;
        padding: 25px; border-radius: 15px; border: 4px solid #334155;
        direction: ltr; text-align: left; box-shadow: 0 10px 25px rgba(0,0,0,0.4); margin: 20px 0;
    }
    .mon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .mon-val { font-size: 36px; font-weight: bold; }
    .hr { color: #f87171; } .bp { color: #fbbf24; } .spo2 { color: #22d3ee; }
    
    /* כרטיסיות תוכן מלא */
    .content-box {
        background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-right: 8px solid #2e59a8;
        line-height: 1.8; font-size: 18px; color: #1e293b;
    }
    
    /* כפתור כניסה גוגל */
    .stLoginButton > button { width: 100% !important; border-radius: 50px !important; border: 1px solid #ddd !important; }
    </style>
    """, unsafe_allow_html=True)

# --- לוגיקת מסד נתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_user_xp(points):
    df = get_data()
    email = st.user.email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.current_xp = int(df.at[idx, 'score'])

# --- בקרה 2: Google Login (אוטומטי) ---
if not st.user.is_logged_in:
    st.markdown("<h1>🏥 PICU Master Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="content-box" style="text-align:center; border:none;">', unsafe_allow_html=True)
        st.write("לכניסה ושמירת התקדמות, נא להתחבר:")
        st.login("google")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# סנכרון ניקוד בטעינה
if 'current_xp' not in st.session_state:
    db = get_data()
    if st.user.email in db['email'].values:
        st.session_state.current_xp = int(db.loc[db['email'] == st.user.email, 'score'].values[0])
    else:
        st.session_state.current_xp = 0

# --- תפריט צד ---
with st.sidebar:
    st.image(st.user.picture, width=70)
    st.markdown(f"### שלום, {st.user.name}")
    st.metric("XP - ניקוד למידה", st.session_state.current_xp)
    if st.button("יציאה מהחשבון"): st.logout()
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "מרכז ידע מלא", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢", "מבחן מעורב", "ניהול"])

# --- בקרה 3: תוכן מלא מה-PDFים (הטמעה רחבה) ---
clinical_content = {
    "המטולוגיה ומוצרי דם": """
    <h3>פאנציטופניה (Pancytopenia)</h3>
    ירידה משמעותית בכל שורות הדם: טרומבוציטופניה, נויטרופניה ואנמיה.
    <br><b>לוקמיה:</b> סרטן הפוגע במח העצם. סימנים: אורגנומגליה, לימפאדנופתיה וכאבי עצמות.
    <br><b>אנמיה אפלסטית:</b> היפופלזיה של מח העצם. סיבות: אידיופטי, תרופות ציטוטוקסיות, זיהומים.
    <hr>
    <h3>מתן מוצרי דם - דגשים קריטיים</h3>
    ● <b>טסיות (PLT):</b> מתן מתחת ל-10,000. <b>אין לתת ב-IVAC!</b> הלחץ הורס את הטסיות. מינון: 5mg/kg. חייב הקרנה.
    <br>● <b>CRYO:</b> מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.
    <br>● <b>FFP (פלזמה):</b> מנה של 200 מ"ל. סוג AB הוא התורם האוניברסלי לפלזמה (אין בו נוגדנים).
    <br>● <b>Granulocytes:</b> מתן ללא פילטר (נתקעים בו).
    """,
    "שוק וספסיס": """
    <h3>זיהוי וניהול ספסיס</h3>
    <b>SIRS:</b> חום >38 או <36, טכיקרדיה, טכיפניאה, לויקוציטוזיס.
    <br><b>פרוטוקול זהב:</b> מתן אנטיביוטיקה תוך שעה! בולוסים של 20ml/kg עד 60ml/kg. 
    <br><b>אמינים:</b> תיעוד אדרנלין/נוראדרנלין כקו ראשון בילדים.
    <hr>
    <h3>שוק קרדיוגני</h3>
    ירידה בכיווץ הלב. <b>סימני גודש:</b> כבד מוגדל (Liver drop), חרחורים בריאות.
    <br><b>אזהרה:</b> להימנע מבולוסים של נוזלים המעמיסים על הלב!
    """,
    "נוירולוגיה ו-TBI": """
    <h3>ניהול לחץ תוך גולגולתי (ICP)</h3>
    ● <b>CPP:</b> MAP פחות ICP. יעד בילדים: 40-60.
    <br>● <b>GCS:</b> מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר.
    <br>● <b>טריאדת קושינג:</b> ברדיקרדיה, ברדיפניאה, יתר ל"ד סיסטולי.
    <br>● <b>טיפול בבצקת:</b> ראש 30 מעלות, מנח ישר, סליין 3% או מניטול (פילטר 1.2 מיקרון).
    """
}

# --- דף דאשבורד ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה מחלקתי</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<div class="content-box"><h3>💊 תרופת היום</h3><b>Propofol</b><br>משמשת להשראת הרדמה מהירה. <br><b>דגש PICU:</b> עלולה לגרום לירידה חדה בלחץ דם. במתן ממושך (מעל 48 שעות) חשש מ-PRIS (Propofol Infusion Syndrome).</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### 🏆 טבלת שיאים (Live)")
        df = get_data().sort_values(by="score", ascending=False).head(10)
        st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))

# --- דף מרכז ידע (Manus Style) ---
elif page == "מרכז ידע מלא":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    cat = st.selectbox("בחר תחום:", list(clinical_content.keys()))
    st.markdown(f'<div class="content-box">{clinical_content[cat]}</div>', unsafe_allow_html=True)

# --- דף תרופות ABC (בחירה דרך גלגלת) ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU</h1>", unsafe_allow_html=True)
    drugs_dict = {
        "א": ["אדרנלין: 0.01mg/kg (החייאה) / 400mcg/kg (סטרידור)", "אדנוזין: 0.1mg/kg פלאש מהיר", "אטרופין: 0.02mg/kg"],
        "ד": ["דופמין: 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg", "דובוטמין: 2-20mcg"],
        "מ": ["מילרינון: 0.25-0.75mcg/kg/min", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg"],
        "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: 1-2mcg/kg", "פרופופול: 2.5-3.5mg/kg"]
    }
    # בקרה: גלגלת לבחירת אות
    letter = st.selectbox("בחר אות ראשונה:", sorted(drugs_dict.keys()))
    # גלגלת לבחירת תרופה ספציפית מהאות
    drug_sel = st.selectbox(f"בחר תרופה באות {letter}:", drugs_dict[letter])
    st.markdown(f'<div class="content-box">{drug_sel}</div>', unsafe_allow_html=True)

# --- תרחיש מתגלגל (Visual & Interactive) ---
elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה</h1>", unsafe_allow_html=True)
    if 'scen_idx' not in st.session_state: st.session_state.scen_idx = 0
    
    if st.session_state.scen_idx == 0:
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML, WBC 810,000. הילד נראה **חיוור מאוד, אפרורי ואפטי**.")
        st.markdown("""<div class="monitor-panel"><div class="mon-grid">
            <div><span class="mon-label">HR</span><br><span class="mon-val hr">192</span></div>
            <div><span class="mon-label">BP</span><br><span class="mon-val bp">68/40</span></div>
            <div><span class="mon-label">SpO2</span><br><span class="mon-val spo2">89%</span></div>
            <div><span class="mon-label">TEMP</span><br><span class="mon-val">38.4</span></div>
        </div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי שלך?", ["דימום פנימי", "Leukostasis (חסימה מכנית)", "ספסיס ויראלי"])
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון! +20 XP"); st.session_state.scen_idx = 1; st.rerun()

    elif st.session_state.scen_idx == 1:
        st.warning("**מצב:** תוך כדי הידרציה, מופיעה אריתמיה. מעבדה: Potassium 7.2. הילד מפתח **רעד בגפיים**.")
        st.markdown("""<div class="monitor-panel"><div class="mon-val hr">! ARRYTHMIA !</div><div class="mon-val">HR: 212</div></div>""", unsafe_allow_html=True)
        ans = st.radio("טיפול דחוף להגנה על הלב?", ["פוסיד", "קלציום גלוקונט IV", "אלופורינול"])
        if st.button("טפל"):
            if "קלציום" in ans: st.success("נכון מאוד! +20 XP"); st.session_state.scen_idx = 2; st.rerun()

    elif st.session_state.scen_idx == 2:
        st.error("**מצב:** הילד מתנשם בכבדות. **חרחורים** בריאות, כבד מוגדל ב-4 ס''מ.")
        ans = st.radio("אבחנה ופעולה?", ["שוק ספטי - נוזלים", "שוק קרדיוגני - אמינים", "שוק היפוולמי - דם"])
        if st.button("סיום תרחיש"):
            if "קרדיוגני" in ans: st.balloons(); update_user_xp(50); st.session_state.scen_idx = 0
