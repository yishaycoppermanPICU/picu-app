import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ועיצוב RTL מושלם ---
st.set_page_config(page_title="PICU Master - Learning Hub", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    
    /* יישור כותרות לאמצע */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: bold; margin-bottom: 25px; }
    
    /* יישור טקסט ופקדים לימין */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stDataFrame, .stTable, .stExpander { 
        direction: RTL !important; text-align: right !important; 
    }
    
    /* עיצוב כרטיסיות תוכן */
    .med-card { 
        background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 25px; 
        border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
    }
    
    /* כפתורים מעוצבים */
    .stButton>button { width: 100%; border-radius: 30px; background-color: #2e59a8; color: white; font-weight: bold; height: 3.5em; border: none; }
    .stButton>button:hover { background-color: #1e3d59; }
    
    /* תיקון סיידבר */
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; }
    
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

def update_db_score(points):
    df = get_db()
    email = st.user.email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
    else:
        new_row = pd.DataFrame([{"name": st.user.name, "email": email, "score": points, "date": str(datetime.date.today())}])
        df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Sheet1", data=df)
    st.session_state.user_score = int(df[df['email'] == email]['score'].values[0])

# --- ניהול כניסה (תיקון השגיאה) ---
if not st.user.is_logged_in:
    st.write("# 🏥 PICU Learning System")
    st.markdown("### ברוכים הבאים למערכת התרגול המחלקתית.\nאנא התחברו עם חשבון הגוגל שלכם כדי לשמור על הניקוד בטבלת השיאים:")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.login("google")
    st.stop()

# --- טעינת ניקוד ראשונית ---
if 'user_score' not in st.session_state:
    db = get_db()
    if st.user.email in db['email'].values:
        st.session_state.user_score = int(db[db['email'] == st.user.email]['score'].values[0])
    else:
        st.session_state.user_score = 0

# --- כל התוכן הקליני מה-PDFים שלך ---
clinical_data = {
    "המטולוגיה ומוצרי דם": {
        "פאנציטופניה": "ירידה בטרומבוציטים, נויטרופילים והמוגלובין. דגשים: לוקמיה (אורגנומגלי, כאבי עצמות), אנמיה אפלסטית (השתלת מח עצם או דיכוי חיסוני).",
        "טסיות (PLT)": "מתן מתחת ל-10,000. **איסור מוחלט על IVAC!** הלחץ מפרק את הטסיות. מינון: 5mg/kg. חייב הקרנה.",
        "Cryoprecipitate": "מקורו בפלסמה. מכיל פיברינוגן (פקטור I), פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר דם.",
        "FFP (פלסמה)": "מכיל את כל חלבוני הקרישה. **דגש סוג דם:** סוג AB הוא התורם האוניברסלי לפלסמה (אין בו נוגדנים).",
        "Granulocytes": "ניתן רק בהוראת המטואונקולוג. **בלי פילטר** (הם נתקעים בו)."
    },
    "שוק וספסיס": {
        "ספסיס ו-SIRS": "חום >38 או <36, טכיקרדיה, טכיפניאה, לויקוציטוזיס. טיפול תוך שעה!",
        "דירוג שוק המורגי": "Class I (<15%), Class II (15-30%), Class III (30-40%), Class IV (>40% - סכנת מוות מיידית).",
        "שוק קרדיוגני": "כשל לבבי. **סימני גודש:** כבד מוגדל (Liver drop), חרחורים בריאות. **אזהרה:** להימנע מבולוסים של נוזלים!",
        "אנפילקסיס": "אדרנלין IM בירך (0.01mg/kg). בולוס NS במינון 20ml/kg במידה ויש היפוטנסיביות."
    },
    "נוירולוגיה ו-TBI": {
        "יעדים ב-TBI": "CPP (MAP-ICP) יעד: 40-60. GCS מתחת ל-8 מחייב אינטובציה להגנה על נתיב אוויר.",
        "טריאדת קושינג": "ברדיקרדיה, שינויי נשימה, יתר לחץ דם. מסמל עלייה קריטית ב-ICP וחשש להרניאציה.",
        "טיפול בבצקת": "ראש ב-30 מעלות, מנח ישר. סליין 3% (5cc/kg) או מניטול (דרך פילטר 1.2 מיקרון)."
    }
}

# --- ספריית תרופות ABC (מה-PDF של שיב"א) ---
drugs_db = {
    "א": ["אדרנלין: 0.01mg/kg (החייאה) / 400mcg/kg (סטרידור)", "אטרופין: 0.02mg/kg (מינימום 0.1mg)", "אדנוזין: 0.1mg/kg פלאש מהיר", "אמיאודורון: 5mg/kg"],
    "ד": ["דופמין: 1-5mcg (כליות), 5-15mcg (לב), >15mcg (ואזופרסורי)", "דקסמתזון: 0.6mg/kg", "דובוטמין: 2-20mcg/kg/min"],
    "מ": ["מילרינון: 0.25-0.75mcg/kg/min", "מידזולם: 0.1-0.2mg/kg", "מורפין: 0.1mg/kg", "מניטול: להורדת ICP דרך פילטר"],
    "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: 1-2mcg/kg", "פרופופול: 2.5-3.5mg/kg", "פניטואין: 20mg/kg העמסה"]
}

# --- תפריט צדי ---
with st.sidebar:
    st.image(st.user.picture, width=80)
    st.write(f"שלום, **{st.user.name}**")
    st.metric("XP - הניקוד שלך", st.session_state.user_score)
    if st.button("התנתק"): st.logout()
    st.divider()
    page = st.radio("לאן הולכים?", ["דאשבורד", "ספריה קלינית (PDF)", "ספריית תרופות ABC", "תרחיש מתגלגל 🎢", "מבחן מעורב", "חיפוש מהיר", "בקשת תוכן"])

# --- דפים ---
if page == "דאשבורד":
    st.header("לוח בקרה מחלקתי")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🏆 טבלת שיאים (Live)")
        df = get_db().sort_values(by="score", ascending=False).head(10)
        st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))
    with col2:
        st.markdown('<div class="med-card"><h3>💊 תרופת היום</h3><b>Potassium (אשלגן)</b><br>זכור: בחולה עם היפומגנזמיה והיפוקלמיה - חובה לתקן מגנזיום קודם! אחרת האשלגן לא ייספג.</div>', unsafe_allow_html=True)

elif page == "ספריה קלינית (PDF)":
    st.header("ספריית הידע - סיכומי PICU")
    sel_cat = st.selectbox("בחר תחום למידה:", list(clinical_data.keys()))
    for sub, text in clinical_data[sel_cat].items():
        with st.expander(f"📌 {sub}"):
            st.write(text)

elif page == "ספריית תרופות ABC":
    st.header("🔤 תרופות לפי סדר הא'-ב'")
    letter = st.select_slider("בחר אות:", options=sorted(drugs_db.keys()))
    for drug in drugs_db[letter]:
        st.markdown(f'<div class="med-card">{drug}</div>', unsafe_allow_html=True)

elif page == "תרחיש מתגלגל 🎢":
    st.header("סימולציה: מהמטולוגיה לקריסה")
    if 'scen_idx' not in st.session_state: st.session_state.scen_idx = 0
    
    if st.session_state.scen_idx == 0:
        st.subheader("שלב 1: קבלת המטופל")
        st.info("תינוק בן חודשיים התקבל עם AML. WBC 810,000. הילד אפטי מאוד.")
        ans = st.radio("מה הסיכון המיידי של המטופל כרגע?", ["דימום מוחי", "Leukostasis (שבץ/כשל נשימתי)", "זיהום ויראלי"])
        if st.button("בצע פעולה"):
            if "Leukostasis" in ans: st.success("נכון מאוד! צמיגות הדם גבוהה עקב עומס תאים."); st.session_state.scen_idx = 1; st.rerun()
            else: st.error("טעות. ספירת לבנים כזו גורמת לחסימה מכנית של כלי דם.")

    elif st.session_state.scen_idx == 1:
        st.subheader("שלב 2: התפתחות TLS")
        st.warning("התחלת הידרציה. המעבדה: אשלגן 6.8, פוספט 9.2, חומצה אורית 15. הילד מאובחן עם Tumor Lysis Syndrome.")
        ans = st.radio("מהי תרופת הבחירה להורדת חומצה אורית במצב זה?", ["אלופורינול", "רזבוריקז"])
        if st.button("טפל"):
            if ans == "רזבוריקז": st.success("מדויק! רזבוריקז מפרקת חומצה אורית קיימת באופן אקטיבי."); st.session_state.scen_idx = 2; st.rerun()

    elif st.session_state.scen_idx == 2:
        st.subheader("שלב 3: הקריסה")
        st.error("הילד מפתח חרחורים בריאות, כבד מוגדל ב-3 ס''מ (Liver drop), ומילוי קפילרי של 5 שניות.")
        ans = st.radio("מהי האבחנה הקלינית שלך ומה הפעולה?", ["שוק ספטי - מתן בולוס נוזלים", "שוק קרדיוגני - התחלת אמינים (אדרנלין/נוראדרנלין)"])
        if st.button("סיים תרחיש"):
            if "קרדיוגני" in ans: 
                st.balloons(); st.success("מצוין! זיהית fluid overload בשוק קרדיוגני. הצלת את הילד!"); update_db_score(50); st.session_state.scen_idx = 0
            else: st.error("טעות קריטית! מתן נוזלים בשוק קרדיוגני יחמיר את בצקת הריאות.")

elif page == "חיפוש מהיר":
    st.header("🔍 מנוע חיפוש קליני")
    q = st.text_input("הקלד שם תרופה, מחלה או מדד:")
    if q:
        found = False
        for cat, content in clinical_data.items():
            for sub, text in content.items():
                if q.lower() in sub.lower() or q.lower() in text.lower():
                    st.markdown(f'<div class="med-card"><b>{sub}</b><br>{text}</div>', unsafe_allow_html=True)
                    found = True
        if not found: st.warning("לא נמצאו תוצאות. נסה מונח אחר.")

elif page == "בקשת תוכן":
    st.header("📝 בקשת תוכן חדש מהמנהל")
    with st.form("req"):
        subj = st.text_input("איזה נושא או תרופה חסרים לך?")
        if st.form_submit_button("שלח בקשה"):
            st.success("הבקשה נרשמה במערכת!")
