import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ועיצוב RTL ---
st.set_page_config(page_title="PICU Expert - Learning Hub", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: bold; }
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stDataFrame, .stTable { direction: RTL !important; text-align: right !important; }
    .med-card { background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 20px; border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2e59a8; color: white; font-weight: bold; height: 3em; }
    div[data-testid="stTable"] { direction: RTL; }
    th { text-align: right !important; background-color: #f0f2f6 !important; }
    td { text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור למסד נתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    return conn.read(worksheet="Sheet1", ttl=0)

def update_score(points):
    df = get_db()
    email = st.experimental_user.email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.score = int(df.at[idx, 'score'])

# --- ניהול כניסה ---
if not st.experimental_user.is_logged_in:
    st.write("# 🏥 מערכת הלמידה המרכזית - PICU")
    st.markdown("### התחברו עם גוגל כדי להתחיל בצבירת XP ולמידה")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: st.login("google")
    st.stop()

# --- הגדרת תוכן קליני (מתוך ה-PDFים שלך) ---
clinical_knowledge = {
    "המטולוגיה ומוצרי דם": {
        "פאנציטופניה": "ירידה בטרומבוציטים, נויטרופילים והמוגלובין. גורמים: לוקמיה (אורגנומגלי, כאבי עצמות), אנמיה אפלסטית.",
        "טסיות (PLT)": "התוויה < 10,000. **איסור IVAC!** הלחץ הורס את הטסיות. מינון: 5mg/kg.",
        "Cryoprecipitate": "מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.",
        "FFP (פלזמה)": "מכיל את כל חלבוני הקרישה. סוג AB הוא התורם האוניברסלי (אין בו נוגדנים).",
        "TLS (טומור ליזיס)": "מצב חירום. היפרקלמיה, היפרפוספטמיה, היפוקלצמיה, היפראוריצמיה. טיפול: הידרציה מאסיבית ורזבוריקז."
    },
    "שוק וספסיס": {
        "ספסיס": "זיהום + SIRS. טיפול תוך שעה! בולוסים של 20ml/kg עד 60ml/kg.",
        "דירוג שוק המורגי": "Class I (<15%), Class II (15-30%), Class III (30-40%), Class IV (>40%). ביטוי מאוחר: ירידת לחץ דם.",
        "שוק קרדיוגני": "כשל לבבי. סימנים: כבד מוגדל (Liver drop), חרחורים. **זהירות מנוזלים!** מתן אמינים (אדרנלין/נוראדרנלין).",
        "אנפילקסיס": "טיפול ראשון: אדרנלין IM בירך (0.01mg/kg). אין קונטראינדיקציה לאדרנלין באנפילקסיס."
    },
    "TBI ונוירולוגיה": {
        "יעדים קריטיים": "CPP = MAP - ICP. יעד בילדים: 40-60. GCS מתחת ל-8 מחייב אינטובציה.",
        "Cushing Triad": "ברדיקרדיה, ברדיפניאה, יתר לחץ דם. סימן להרניאציה מוחית.",
        "טיפול בבצקת": "הרמת ראש 30 מעלות, מנח ישר, סליין 3% (cc/kg 5) או מניטול (דרך פילטר)."
    }
}

# --- ספריית תרופות ABC (מתוך PDF התרופות) ---
drugs_abc = {
    "א": ["אדרנלין: 0.01mg/kg החייאה / 400mcg/kg אינהלציה", "אדנוזין: 0.1mg/kg פלאש מהיר ל-SVT", "אטרופין: 0.02mg/kg (מינימום 0.1mg)", "אמיאודורון: 5mg/kg לאריתמיות"],
    "ד": ["דופמין: 1-5mcg (כליות), 5-15mcg (אינוטרופי), >15mcg (ואזופרסורי)", "דקסמתזון: 0.6mg/kg לאקסטובציה/סטרידור", "דובוטמין: 2-20mcg/kg/min"],
    "מ": ["מילרינון: 0.25-0.75mcg/kg/min (Inodilator)", "מידזולם: 0.1-0.2mg/kg לסדציה", "מורפין: 0.1mg/kg לשיכוך כאב"],
    "פ": ["פוסיד: 0.5-2mg/kg משתן לולאה", "פנטניל: 1-2mcg/kg (זהירות מ-Chest Rigidity)", "פרופופול: 2.5-3.5mg/kg להשראת הרדמה"],
    "ק": ["קטמין: 1-2mg/kg. לא מדכא נשימה, לא מעלה ICP", "קלציום גלוקונט: 100mg/kg להגנה על הלב"]
}

# --- תפריט ראשי ---
with st.sidebar:
    st.image(st.experimental_user.picture, width=80)
    st.write(f"שלום, **{st.experimental_user.name}**")
    if 'score' not in st.session_state: st.session_state.score = 0
    st.metric("XP - ניקוד למידה", st.session_state.score)
    page = st.radio("ניווט באתר:", ["דאשבורד", "ספריה קלינית (PDF)", "ספריית תרופות ABC", "התרחיש המתגלגל 🎢", "מבחן מעורב"])

if page == "דאשבורד":
    st.header("לוח בקרה לימודי")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🏆 מובילי המחלקה")
        try:
            df = get_db().sort_values(by="score", ascending=False).head(10)
            st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))
        except: st.write("טוען נתונים...")
    with col2:
        st.markdown('<div class="med-card"><h3>💊 תרופת היום: Adenosine</h3>זמן מחצית חיים של פחות מ-10 שניות! חובה להזריק קרוב ככל הניתן ללב ולשטוף במהירות (Flush).</div>', unsafe_allow_html=True)

elif page == "ספריה קלינית (PDF)":
    st.header("מרכז הידע - מבוסס UpToDate")
    cat = st.selectbox("בחר תחום:", list(clinical_knowledge.keys()))
    for sub, content in clinical_knowledge[cat].items():
        with st.expander(f"📌 {sub}"):
            st.write(content)

elif page == "ספריית תרופות ABC":
    st.header("🔤 ספריית תרופות ABC")
    letter = st.select_slider("בחר אות:", options=sorted(drugs_abc.keys()))
    for drug in drugs_abc[letter]:
        st.markdown(f'<div class="med-card">{drug}</div>', unsafe_allow_html=True)

elif page == "התרחיש המתגלגל 🎢":
    st.header("סימולציה: מהמטולוגיה לקריסה")
    if 'scen_step' not in st.session_state: st.session_state.scen_step = 0
    
    if st.session_state.scen_step == 0:
        st.subheader("שלב 1: הקבלה")
        st.info("תינוק בן חודשיים עם AML, ספירת WBC של 810,000. הילד אפטי.")
        ans = st.radio("מה הסיכון המיידי?", ["דימום מוחי", "Leukostasis (שבץ/כשל נשימתי)", "היפוגליקמיה"])
        if st.button("בצע פעולה"):
            if "Leukostasis" in ans: 
                st.success("נכון! צמיגות הדם גבוהה מאוד."); st.session_state.scen_step = 1; st.rerun()
    
    elif st.session_state.scen_step == 1:
        st.subheader("שלב 2: התפתחות TLS")
        st.warning("התחלת הידרציה. מעבדה: אשלגן 6.9, פוספט 9.5, חומצה אורית 14.")
        ans = st.radio("מה תרופת הבחירה להורדת חומצה אורית כעת?", ["אלופורינול", "רזבוריקז"])
        if st.button("טפל"):
            if ans == "רזבוריקז": st.success("מצוין. רזבוריקז מפרקת חומצה אורית קיימת."); st.session_state.scen_step = 2; st.rerun()

    elif st.session_state.scen_step == 2:
        st.subheader("שלב 3: קריסה")
        st.error("הילד מפתח חרחורים בריאות, כבד מוגדל ב-3 ס''מ, מילוי קפילרי 5 שניות.")
        ans = st.radio("איזה שוק זה ומה הפעולה?", ["שוק ספטי - בולוס נוזלים", "שוק קרדיוגני - התחלת אמינים"])
        if st.button("סיים תרחיש"):
            if "קרדיוגני" in ans: 
                st.balloons(); st.success("הצלת את הילד! זיהית fluid overload בשוק קרדיוגני."); update_score(50); st.session_state.scen_step = 0
