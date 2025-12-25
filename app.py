import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ועיצוב RTL מושלם ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# הזרקת CSS לתיקון כל בעיות היישור והעיצוב
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    
    /* יישור כותרות לאמצע */
    h1, h2, h3, h4, h5 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: 700; margin-top: 10px; }
    
    /* יישור טקסט ופקדים לימין */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stDataFrame, .stTable, .stExpander { 
        direction: RTL !important; text-align: right !important; 
    }
    
    /* עיצוב כרטיסיות (Cards) */
    .med-card { 
        background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 20px; 
        border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
    }
    
    /* עיצוב כפתורים */
    .stButton>button { width: 100%; border-radius: 30px; background-color: #2e59a8; color: white; font-weight: bold; height: 3.5em; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #1e3d59; transform: scale(1.02); }
    
    /* תיקון סיידבר */
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; border-left: 1px solid #ddd; }
    
    /* תיקון טבלאות */
    div[data-testid="stTable"] { direction: RTL; }
    th { text-align: right !important; background-color: #f0f2f6 !important; }
    td { text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור למסד נתונים (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_points(points):
    df = get_db()
    email = st.session_state.user_email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.user_score = int(df.at[idx, 'score'])

# --- ניהול מצב משתמש (Session State) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_score' not in st.session_state: st.session_state.user_score = 0
if 'scen_step' not in st.session_state: st.session_state.scen_step = 0

# --- מסך כניסה (יציב ובטוח) ---
if not st.session_state.logged_in:
    st.markdown("<h1>🏥 PICU Master - למידה ותרגול</h1>", unsafe_allow_html=True)
    st.markdown("### ברוכים הבאים למערכת הלמידה המחלקתית.\nאנא הזדהו כדי לשמור על הניקוד בטבלת השיאים:")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        u_name = st.text_input("שם מלא:")
        u_email = st.text_input("אימייל (לסנכרון ניקוד):")
        if st.button("כניסה למערכת"):
            if u_name and u_email:
                st.session_state.logged_in = True
                st.session_state.user_name = u_name
                st.session_state.user_email = u_email
                db = get_db()
                if u_email in db['email'].values:
                    st.session_state.user_score = int(db[db['email'] == u_email]['score'].values[0])
                st.rerun()
            else:
                st.error("נא למלא את כל השדות")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- מאגר ידע מלא (מתוך ה-PDFים שלך) ---
clinical_knowledge = {
    "המטולוגיה ומוצרי דם": {
        "פאנציטופניה": "ירידה בטרומבוציטים, נויטרופילים והמוגלובין. דגשים: לוקמיה (אורגנומגלי, כאבי עצמות), אנמיה אפלסטית (השתלת מח עצם או דיכוי חיסוני).",
        "טסיות (PLT)": "מתן מתחת ל-10,000. **איסור מוחלט על IVAC!** הלחץ מפרק את הטסיות. מינון: 5mg/kg. חייב הקרנה.",
        "Cryoprecipitate": "מקורו בפלסמה. מכיל פיברינוגן (פקטור I), פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.",
        "FFP (פלסמה)": "מכיל את כל חלבוני הקרישה. סוג AB הוא התורם האוניברסלי לפלסמה (אין בו נוגדנים).",
        "SCID": "חוסר חיסוני משולב. דורש בידוד, מוצרי דם מוקרנים ושליליים ל-CMV. פרוגנוזה טובה אם הושתלו לפני גיל 3.5 חודשים."
    },
    "אלקטרוליטים (שיב''א)": {
        "אשלגן (Potassium)": "רמות: 3.5-5. **דגש קריטי:** חובה לתקן מגנזיום תחילה! אחרת תהיה היפוקלמיה עמידה. קצב IV מקסימלי: 0.5mEq/kg/h.",
        "אינסולין בהחייאה": "מינון פוש: 0.1 units/kg. מהילה: 50 יחידות ב-50 סליין (1 יחידה ל-מ''ל).",
        "סודיום ביקרבונט": "בופר לדם. מינון: 1mEq/kg. בילדים מתחת לגיל שנתיים - לדלל פי 2 עם מים להזרקה."
    },
    "שוק וספסיס": {
        "זיהוי ספסיס": "זיהום + SIRS (חום, טכיקרדיה, טכיפניאה). טיפול תוך שעה! בולוסים של 20ml/kg עד 60ml/kg.",
        "שוק קרדיוגני": "כשל לבבי. **סימני גודש:** כבד מוגדל (Liver drop), חרחורים בריאות. **אזהרה:** להימנע מבולוסים של נוזלים! התחלת אמינים.",
        "אנפילקסיס": "טיפול ראשון: אדרנלין IM בירך (0.01mg/kg). מקסימום 0.5mg למנה."
    },
    "נוירולוגיה ו-TBI": {
        "יעדים ב-TBI": "CPP (MAP-ICP) יעד: 40-60. GCS מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר.",
        "טיפול בבצקת": "ראש ב-30 מעלות, מנח ישר. סליין 3% (5cc/kg) או מניטול (דרך פילטר 1.2 מיקרון).",
        "Cushing Triad": "ברדיקרדיה, שינויי נשימה, יתר לחץ דם. סימן לעלייה קריטית ב-ICP."
    }
}

# --- ספריית תרופות ABC מלאה ---
drugs_abc = {
    "א": ["אדרנלין: 0.01mg/kg (החייאה) / 400mcg/kg (סטרידור)", "אטרופין: 0.02mg/kg (מינימום 0.1mg)", "אדנוזין: 0.1mg/kg פלאש מהיר", "אמיאודורון: 5mg/kg"],
    "ד": ["דופמין: 1-5mcg (כליות), 5-15mcg (לב), >15mcg (ואזופרסורי)", "דקסמתזון: 0.6mg/kg", "דובוטמין: 2-20mcg/kg/min", "דיאמוקס: 2.5-5mg/kg"],
    "מ": ["מילרינון: 0.25-0.75mcg/kg/min", "מידזולם: 0.1-0.2mg/kg (סדציה)", "מורפין: 0.1mg/kg (כאב)", "מניטול: להורדת ICP דרך פילטר"],
    "פ": ["פוסיד: 0.5-2mg/kg (משתן)", "פנטניל: 1-2mcg/kg (זהירות מ-Chest Rigidity)", "פרופופול: 2.5-3.5mg/kg", "פנוברביטל: 15-20mg/kg העמסה"]
}

# --- תפריט צדי ---
with st.sidebar:
    st.markdown(f"<h4>שלום, {st.session_state.user_name}</h4>", unsafe_allow_html=True)
    st.metric("XP - הניקוד שלך 🏆", st.session_state.user_score)
    if st.button("התנתק"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "ספריה קלינית (PDF)", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢", "מבחן מעורב", "חיפוש מהיר"])

# --- דף דאשבורד ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה מחלקתי</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🏆 מובילי המחלקה")
        try:
            df = get_db().sort_values(by="score", ascending=False).head(10)
            st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))
        except: st.info("טוען נתונים...")
    with col2:
        st.markdown('<div class="med-card"><h3>💊 תרופת היום</h3><b>Adenosine</b><br>לטיפול ב-SVT. חובה להזריק בפולש מהיר (Flash) הכי קרוב ללב. זמן מחצית חיים קצר מ-10 שניות!</div>', unsafe_allow_html=True)

# --- דף ספריה קלינית ---
elif page == "ספריה קלינית (PDF)":
    st.markdown("<h1>מרכז הידע - מבוסס UpToDate</h1>", unsafe_allow_html=True)
    cat = st.selectbox("בחר תחום:", list(clinical_knowledge.keys()))
    for sub, content in clinical_knowledge[cat].items():
        with st.expander(f"📌 {sub}"):
            st.write(content)

# --- דף ספריית תרופות ABC ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU</h1>", unsafe_allow_html=True)
    letter = st.select_slider("בחר אות:", options=sorted(drugs_abc.keys()))
    for drug in drugs_abc[letter]:
        st.markdown(f'<div class="med-card">{drug}</div>', unsafe_allow_html=True)

# --- דף תרחיש מתגלגל ---
elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה: מהמטולוגיה לקריסה</h1>", unsafe_allow_html=True)
    
    if st.session_state.scen_step == 0:
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        st.subheader("שלב 1: הקבלה")
        st.info("תינוק בן חודשיים התקבל עם AML. ספירת WBC של 810,000. הילד אפטי מאוד.")
        ans = st.radio("מה הסיכון המיידי של המטופל כרגע?", ["דימום מוחי", "Leukostasis (שבץ/כשל נשימתי)", "זיהום ויראלי"])
        if st.button("בצע פעולה"):
            if "Leukostasis" in ans:
                st.success("נכון מאוד! צמיגות הדם גבוהה עקב עומס תאים חריג."); st.session_state.scen_step = 1; st.rerun()
            else: st.error("טעות. ספירת לבנים כזו גורמת לחסימה מכנית של כלי דם.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.scen_step == 1:
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        st.subheader("שלב 2: התפתחות TLS")
        st.warning("התחלת הידרציה. המעבדה חוזרת: אשלגן 6.8, פוספט 9.2, חומצה אורית 15. אבחנה: Tumor Lysis Syndrome.")
        ans = st.radio("מהי תרופת הבחירה להורדת חומצה אורית במצב זה?", ["אלופורינול", "רזבוריקז"])
        if st.button("טפל"):
            if ans == "רזבוריקז":
                st.success("מדויק! רזבוריקז מפרקת חומצה אורית קיימת באופן אקטיבי."); st.session_state.scen_step = 2; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.scen_step == 2:
        st.markdown('<div class="med-card">', unsafe_allow_html=True)
        st.subheader("שלב 3: הקריסה")
        st.error("הילד מפתח חרחורים בריאות, כבד מוגדל ב-3 ס''מ (Liver drop), ומילוי קפילרי של 5 שניות.")
        ans = st.radio("מהי האבחנה הקלינית שלך ומה הפעולה?", ["שוק ספטי - מתן בולוס נוזלים", "שוק קרדיוגני - התחלת אמינים (אדרנלין/נוראדרנלין)"])
        if st.button("סיים תרחיש"):
            if "קרדיוגני" in ans:
                st.balloons(); st.success("מצוין! זיהית fluid overload בשוק קרדיוגני. הצלת את הילד!"); update_points(50); st.session_state.scen_step = 0
            else: st.error("טעות קריטית! מתן נוזלים בשוק קרדיוגני יחמיר את בצקת הריאות.")
        st.markdown('</div>', unsafe_allow_html=True)
