import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# --- עיצוב RTL, כותרות באמצע ומוניטור ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&family=Share+Tech+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    
    /* כותרות באמצע */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: 800; }
    
    /* עיצוב המוניטור בתרחישים */
    .monitor {
        background-color: #000;
        color: #39ff14;
        font-family: 'Share Tech Mono', monospace;
        padding: 20px;
        border: 4px solid #555;
        border-radius: 15px;
        direction: ltr;
        text-align: left;
        box-shadow: inset 0 0 20px #000;
        margin: 20px 0;
    }
    .mon-row { display: flex; justify-content: space-between; font-size: 28px; }
    .hr { color: #ff3e3e; } .bp { color: #ffff4d; } .spo2 { color: #4de6ff; } .rr { color: #ffffff; }

    .content-card { 
        background: white; border-right: 10px solid #2e59a8; padding: 30px; 
        border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        line-height: 1.8; font-size: 18px;
    }
    .stButton>button { width: 100%; border-radius: 30px; background: #2e59a8; color: white; font-weight: bold; height: 3.5em; }
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור לגוגל שיטס ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def add_xp(points):
    df = get_db()
    email = st.session_state.user_email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.user_score = int(df.at[idx, 'score'])

# --- מערכת כניסה ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1>🏥 PICU Master Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        name = st.text_input("שם מלא:")
        email = st.text_input("אימייל:")
        if st.button("כניסה למערכת"):
            if name and email:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.session_state.user_email = email
                db = get_db()
                st.session_state.user_score = int(db.loc[db['email'] == email, 'score'].values[0]) if email in db['email'].values else 0
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- תוכן קליני מלא מה-PDFים שלך ---
DATA = {
    "המטואונקולוגיה": {
        "פאנציטופניה": "פאנציטופניה מתייחסת למצב בו ישנה ירידה משמעותית בכל שורות הדם: טרומבוציטופניה, נויטרופניה ואנמיה.\nגורמים: לוקמיה (אורגנומגליה, לימפאדנופתיה, כאבי עצמות), אנמיה אפלסטית (היפופלזיה של מח העצם).",
        "מוצרי דם": "● **טסיות (PLT):** התוויה < 10,000. אין לתת ב-IVAC! הלחץ הורס את הטסיות. מינון: 5mg/kg. חייב הקרנה.\n● **CRYO:** מכיל פיברינוגן (פקטור I), פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.\n● **FFP:** מכיל את כל חלבוני הקרישה. סוג AB הוא התורם האוניברסלי.\n● **Granulocytes:** ללא פילטר דם.",
        "TLS - Tumor Lysis Syndrome": "מצב חירום הנגרם מפירוק מסה של תאים. \nמעבדה: היפרקלמיה, היפרפוספטמיה, היפוקלצמיה, היפראוריצמיה.\nטיפול: הידרציה מאסיבית ורזבוריקז (פעיל אקטיבית על חומצה אורית)."
    },
    "שוק וספסיס": {
        "ספסיס ו-SIRS": "SIRS מוגדר כדלקת סיסטמית: חום >38 או <36, טכיקרדיה, טכיפניאה. ספסיס = SIRS + זיהום.\nטיפול: תוך שעה! בולוסים 20ml/kg עד 60ml/kg. אמינים: תיעוד אדרנלין/נוראדרנלין על פני דופמין.",
        "שוק קרדיוגני": "ירידה בכושר כיווץ הלב. סימנים: כבד מוגדל (Liver drop), חרחורים בריאות. אזהרה: להימנע מנוזלים המעמיסים על הלב!",
        "אנפילקסיס": "טיפול ראשון: אדרנלין IM בירך (0.01mg/kg). מקסימום 0.5mg. חמצן 100% ובולוס NS."
    },
    "נוירולוגיה ו-TBI": {
        "ניהול ICP": "יעד CPP (MAP-ICP) בילדים: 40-60. GCS < 8 מחייב אינטובציה.\nטריאדת קושינג: ברדיקרדיה, ברדיפניאה, יתר ל''ד סיסטולי.\nטיפול: ראש ב-30 מעלות, מנח ישר, סליין 3% (5cc/kg) או מניטול (פילטר 1.2)."
    }
}

# --- תפריט צדי ---
with st.sidebar:
    st.markdown(f"<h4>שלום, {st.session_state.user_name}</h4>", unsafe_allow_html=True)
    st.metric("XP - ניקוד למידה", st.session_state.user_score)
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "מרכז ידע מלא", "תרחיש מתגלגל 🎢", "ספריית תרופות ABC", "חיפוש", "ניהול (Admin)"])
    if st.button("התנתק"): st.session_state.logged_in = False; st.rerun()

# --- דף דאשבורד ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה מחלקתי</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🏆 טבלת שיאים (Live)")
        df = get_db().sort_values(by="score", ascending=False).head(5)
        st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))
    with col2:
        st.markdown('<div class="content-card"><h3>💊 תרופת היום</h3><b>Adenosine</b><br>ל-SVT. הזרקת פלאש מהירה. זמן מחצית חיים קצר מ-10 שניות.</div>', unsafe_allow_html=True)

# --- דף מרכז ידע ---
elif page == "מרכז ידע מלא":
    st.markdown("<h1>ספריית ידע PICU - תוכן מלא</h1>", unsafe_allow_html=True)
    cat = st.selectbox("בחר נושא:", list(DATA.keys()))
    for sub, text in DATA[cat].items():
        st.markdown(f'<div class="content-card"><h3>{sub}</h3>{text}</div>', unsafe_allow_html=True)

# --- תרחיש מתגלגל 🎢 ---
elif page == "תרחיש מתגלגל 🎢":
    if 's_idx' not in st.session_state: st.session_state.s_idx = 0
    
    if st.session_state.s_idx == 0:
        st.markdown("### שלב 1: הקבלה")
        st.info("**סיפור מקרה:** תינוק בן חודשיים עם AML. WBC 810,000. הילד נראה **אפרורי, חיוור מאוד ואפטי**.")
        st.markdown("""<div class="monitor"><div class="mon-row hr">HR: 192</div><div class="mon-row bp">BP: 68/38</div><div class="mon-row spo2">SpO2: 89% (RA)</div></div>""", unsafe_allow_html=True)
        ans = st.radio("מה החשד המיידי שלך?", ["דימום", "Leukostasis", "ספסיס"])
        if st.button("בצע פעולה"):
            if ans == "Leukostasis": st.success("נכון!"); st.session_state.s_idx = 1; st.rerun()

    elif st.session_state.s_idx == 1:
        st.markdown("### שלב 2: התפתחות TLS")
        st.warning("**מצב:** הילד מקבל הידרציה. המעבדה: אשלגן 7.2. הילד מפתח **רעד בגפיים**.")
        st.markdown("""<div class="monitor"><div class="mon-row hr">HR: 210 (Arrythmia)</div><div class="mon-row spo2">SpO2: 92%</div></div>""", unsafe_allow_html=True)
        ans = st.radio("פעולה דחופה?", ["פוסיד", "קלציום גלוקונט IV", "אלופורינול"])
        if st.button("טפל"):
            if "קלציום" in ans: st.success("מצוין!"); st.session_state.s_idx = 2; st.rerun()

    elif st.session_state.s_idx == 2:
        st.markdown("### שלב 3: שוק קרדיוגני")
        st.error("**מצב:** הילד מתנשם, חרחורים בריאות, כבד נמוש 4 ס''מ.")
        ans = st.radio("אבחנה?", ["שוק ספטי", "שוק קרדיוגני", "שוק היפוולמי"])
        if st.button("סיים"):
            if "קרדיוגני" in ans: st.balloons(); add_xp(50); st.session_state.s_idx = 0

# --- ספריית תרופות ABC ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות</h1>", unsafe_allow_html=True)
    letter = st.select_slider("בחר אות:", options=["א", "ב", "ד", "מ", "פ", "ק"])
    meds = {"א": ["אדרנלין: 0.01mg/kg", "אדנוזין: 0.1mg/kg"], "ד": ["דופמין: 1-20mcg"], "מ": ["מילרינון: 0.25-0.75mcg"]}
    for m in meds.get(letter, []): st.markdown(f'<div class="content-card">{m}</div>', unsafe_allow_html=True)

# --- פאנל ניהול ---
elif page == "ניהול (Admin)":
    pwd = st.text_input("סיסמת מנהל:", type="password")
    if pwd == "PICU123":
        st.success("שלום מנהל!")
        df = get_db()
        st.subheader("ניהול משתמשים וניקוד")
        st.data_editor(df)
        if st.button("שמור שינויים לגיליון"):
            conn.update(worksheet="Sheet1", data=df)
            st.success("הנתונים נשמרו!")
