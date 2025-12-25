import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
import datetime

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# --- הזרקת CSS לעיצוב RTL מושלם, כותרות באמצע וטבלאות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; font-weight: 700; }
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stDataFrame, .stTable { 
        direction: RTL !important; text-align: right !important; 
    }
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; border-left: 1px solid #ddd; }
    .med-card { 
        background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 20px; 
        border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
    }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2e59a8; color: white; font-weight: bold; height: 3em; border: none; }
    .stButton>button:hover { background-color: #1e3d59; color: #fff; }
    /* תיקון טבלאות */
    div[data-testid="stTable"] { direction: RTL; }
    th { text-align: right !important; background-color: #f0f2f6 !important; }
    td { text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור לגוגל שיטס ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    return conn.read(worksheet="Sheet1", ttl=0)

def update_user_score(name, email, points_to_add):
    df = get_db()
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points_to_add
    else:
        new_user = pd.DataFrame([{"name": name, "email": email, "score": points_to_add, "date": str(datetime.date.today())}])
        df = pd.concat([df, new_user], ignore_index=True)
    conn.update(worksheet="Sheet1", data=df)
    st.session_state.points = int(df[df['email'] == email]['score'].values[0]) if email in df['email'].values else points_to_add

# --- ניהול מצב משתמש ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'points' not in st.session_state: st.session_state.points = 0

# --- מסך כניסה ---
if not st.session_state.logged_in:
    st.title("🏥 PICU Learning System")
    st.write("ברוכים הבאים למערכת התרגול המחלקתית. נא להזדהות כדי לשמור על הניקוד.")
    with st.container():
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
                    # בדיקת ניקוד קיים
                    try:
                        df = get_db()
                        if u_email in df['email'].values:
                            st.session_state.points = int(df[df['email'] == u_email]['score'].values[0])
                    except: pass
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- מאגר נתונים קליני (מבוסס PDF) ---
knowledge_base = {
    "המטואונקולוגיה": """
    **מוצרי דם:** 
    - **טסיות (PLT):** מינון 5mg/kg. אסור ב-IVAC (הלחץ הורס אותן). חובה הקרנה.
    - **Cryoprecipitate:** פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר.
    - **FFP:** מנה 200 מ"ל. סוג AB הוא התורם האוניברסלי.
    **TLS:** היפרקלמיה, היפרפוספטמיה, היפוקלצמיה, היפראוריצמיה. טיפול: הידרציה מאסיבית ורזבוריקז.
    """,
    "שוק וספסיס": """
    **שוק ספטי:** טיפול תוך שעה. בולוסים 20ml/kg עד 60ml/kg. אדרנלין/נוראדרנלין עדיפים על דופמין.
    **שוק קרדיוגני:** זהירות מנוזלים! סימנים: כבד מוגדל (Liver drop), חרחורים.
    **אנפילקסיס:** אדרנלין IM 0.01mg/kg (מקסימום 0.5mg).
    """,
    "TBI ו-ICP": """
    **יעדים:** CPP (MAP-ICP) בין 40-60. GCS < 8 מחייב אינטובציה.
    **Cushing Triad:** ברדיקרדיה, ירידה בנשימה, יתר לחץ דם.
    **טיפול:** ראש ב-30 מעלות, מנח נייטרלי, סליין 3% או מניטול (דרך פילטר 1.2 מיקרון).
    """,
    "אלקטרוליטים": """
    **אשלגן:** 3.5-5. חובה לתקן מגנזיום לפני אשלגן (אחרת תהיה היפוקלמיה עמידה).
    **אינסולין:** ב-DKA או היפרקלמיה. מינון פוש: 0.1 units/kg.
    """
}

all_questions = [
    {"q": "מדוע אין לתת טרומבוציטים ב-IVAC?", "a": "הלחץ המכני הורס את התאים", "options": ["מהירות נמוכה", "הלחץ המכני הורס את התאים", "הפילטר נסתם"], "cat": "המטואונקולוגיה"},
    {"q": "מהו סימן האזהרה המבדיל שוק קרדיוגני מהיפוולמי?", "a": "כבד מוגדל וחרחורים", "options": ["דופק מהיר", "כבד מוגדל וחרחורים", "חום גבוה"], "cat": "שוק וספסיס"},
    {"q": "מה יש לתקן תחילה בחולה עם היפוקלמיה והיפומגנזמיה?", "a": "מגנזיום", "options": ["אשלגן", "מגנזיום", "נתרן"], "cat": "אלקטרוליטים"},
    {"q": "מהו יעד ה-CPP המומלץ בילדים עם TBI?", "a": "40-60", "options": ["20-30", "40-60", "70-90"], "cat": "TBI ו-ICP"}
]

drugs_abc = {
    "א": ["אדרנלין: 0.01mg/kg החייאה", "אדנוזין: 0.1mg/kg ל-SVT", "אטרופין: 0.02mg/kg (מינימום 0.1mg)"],
    "ד": ["דופמין: מינון 1-20mcg/kg/min", "דקסמתזון: 0.6mg/kg לסטרידור"],
    "מ": ["מילרינון: 0.25-0.75mcg/kg/min", "מניטול: להורדת ICP דרך פילטר"],
    "פ": ["פוסיד: 0.5-2mg/kg", "פנטניל: 1-2mcg/kg לתינוקות"]
}

# --- תפריט צדי ---
with st.sidebar:
    st.title("🏥 PICU Expert")
    st.write(f"שלום, **{st.session_state.user_name}**")
    st.metric("הניקוד שלך 🏆", f"{st.session_state.points} XP")
    if st.button("התנתק"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "חיפוש מהיר", "מרכז למידה", "מבחן אישי", "ספריית תרופות ABC", "בקשת תוכן"])

# --- דפים ---
if page == "דאשבורד":
    st.header("לוח בקרה לימודי")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🏆 טבלת שיאים מחלקתית")
        try:
            df = get_db().sort_values(by="score", ascending=False).head(10)
            st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "ניקוד"}))
        except: st.write("טעינת נתונים...")
    with col2:
        st.markdown('<div class="med-card"><h3>💊 תרופת היום</h3><b>Adenosine</b><br>לטיפול ב-SVT. הזרקת פלאש מהירה בווריד קרוב ללב. זמן מחצית חיים קצר מ-10 שניות!</div>', unsafe_allow_html=True)

elif page == "חיפוש מהיר":
    st.header("🔍 מנוע חיפוש קליני")
    q = st.text_input("חפש מחלה, תרופה או פרוטוקול:")
    if q:
        for cat, content in knowledge_base.items():
            if q.lower() in cat.lower() or q.lower() in content.lower():
                st.markdown(f'<div class="med-card"><b>{cat}</b><br>{content}</div>', unsafe_allow_html=True)

elif page == "מרכז למידה":
    st.header("ספריית ידע - UpToDate")
    sel_cat = st.selectbox("בחר נושא:", list(knowledge_base.keys()))
    st.markdown(f'<div class="med-card"><h3>{sel_cat}</h3>{knowledge_base[sel_cat]}</div>', unsafe_allow_html=True)
    if st.button(f"התחל מבחן על {sel_cat}"):
        st.info("עבור ללשונית 'מבחן אישי'")

elif page == "מבחן אישי":
    st.header("מבחן תרגול XP")
    mode = st.radio("סוג מבחן:", ["מעורב (כל הנושאים)", "נושאי"])
    if 'current_q' not in st.session_state:
        st.session_state.current_q = random.choice(all_questions)
    
    q = st.session_state.current_q
    st.subheader(q["q"])
    user_ans = st.radio("בחר תשובה:", q["options"], key="q_radio")
    
    if st.button("בדוק תשובה"):
        if user_ans == q["a"]:
            st.success("נכון מאוד! +20 נקודות")
            update_user_score(st.session_state.user_name, st.session_state.user_email, 20)
            st.session_state.current_q = random.choice(all_questions)
            st.button("לשאלה הבאה")
        else:
            st.error(f"טעות. התשובה הנכונה היא: {q['a']}")

elif page == "ספריית תרופות ABC":
    st.header("🔤 תרופות לפי סדר הא'-ב'")
    letter = st.select_slider("בחר אות:", options=sorted(drugs_abc.keys()))
    for d in drugs_abc[letter]:
        st.markdown(f'<div class="med-card">{d}</div>', unsafe_allow_html=True)

elif page == "בקשת תוכן":
    st.header("📝 בקשת תוכן חדש")
    with st.form("req"):
        subj = st.text_input("מה חסר לך באתר?")
        if st.form_submit_button("שלח למנהל"):
            st.success("הבקשה נרשמה!")
