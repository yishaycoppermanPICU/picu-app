import streamlit as st
import pandas as pd
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# --- הזרקת CSS לעיצוב RTL, כותרות באמצע וחיפוש ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    
    h1, h2, h3 { text-align: center !important; direction: RTL !important; color: #1e3d59; }
    
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric { 
        direction: RTL !important; text-align: right !important; 
    }
    
    .med-card { 
        background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 20px; 
        border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
    }
    
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2e59a8; color: white; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- בסיס נתונים (מבוסס על ה-PDF של מבחן התרופות) ---
if 'points' not in st.session_state: st.session_state.points = 0
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'requests' not in st.session_state: st.session_state.requests = []

# מאגר מידע מאוחד לחיפוש
knowledge_base = {
    "אשלגן (Potassium)": "רמות תקינות: 3.5-5. מינון IV: 0.5-1 mEq/kg. קצב מקסימלי: 0.5 mEq/kg/h. דגש: יש לתקן מגנזיום תחילה למניעת היפוקלמיה עמידה. אסור לתת במתן מהיר (Bolus).",
    "אדרנלין (Adrenaline)": "החייאה: 0.01mg/kg (1:10,000). מקסימום 1mg. ניתן כל 2 דקות ב-PALS. אינהלציה לסטרידור: 400mcg/kg (עד 5mg).",
    "אטרופין (Atropine)": "לברדיקרדיה או ייבוש הפרשות באינטובציה (עם קטמין). מינון: 0.02mg/kg. מינימום למנה: 0.1mg למניעת תגובה פרדוקסלית.",
    "אדנוזין (Adenosine)": "ל-SVT. מינון ראשון: 0.1mg/kg (עד 6mg). מינון שני: 0.2mg/kg (עד 12mg). דגש: הזרקה מהירה (Flash) בווריד הכי קרוב ללב.",
    "קלציום גלוקונט 10%": "להיפוקלצמיה או הגנה על הלב בהיפרקלמיה. מינון: 100mg/kg. זהירות מקריסטליזציה.",
    "לידוקאין 1%": "להפרעות קצב VT/VF עמידות לשוק. מינון העמסה: 1mg/kg. ניתן לתת בטובוס במינון כפול.",
    "פוסיד (Furosemide)": "משתן לולאה. מינון: 0.5-1 mg/kg. דגש: עלול לגרום להיפוקלמיה והיפונתרמיה.",
    "דיאמוקס (Diamox)": "להורדת ICP או בססת מטבולית. מינון: 2.5mg/kg מניעתי.",
    "מניטול (Mannitol)": "משתן אוסמוטי להורדת ICP. פועל תוך משיכת נוזלים לכלי הדם. דגש: מתן דרך פילטר 1.2 מיקרון.",
    "דופמין (Dopamine)": "מינון נמוך (1-5): כליות. ביניים (5-15): אינוטרופי. גבוה (>15): ואזופרסורי (אלפא).",
    "מילרינון (Milrinone)": "Inodilator. משפר כיווץ ומרחיב כלי דם ריאתיים וסיסטמיים. יעד מינון: 0.25-0.75 mcg/kg/min.",
    "טסיות (PLT)": "מינון 5ml/kg. אסור ב-IVAC (הלחץ מפרק את הטסיות).",
    "FFP (פלסמה)": "מכיל גורמי קריאה. סוג AB הוא התורם האוניברסלי."
}

# --- תפריט צדי ---
with st.sidebar:
    st.title("🏥 PICU Learning Hub")
    if not st.session_state.user_name:
        name = st.text_input("שם מלא:")
        if st.button("התחבר"):
            st.session_state.user_name = name
            st.rerun()
    else:
        st.success(f"שלום, **{st.session_state.user_name}**")
        st.metric("XP (ניקוד)", st.session_state.points)
    
    st.divider()
    page = st.radio("ניווט:", ["דאשבורד", "חיפוש מהיר", "מרכז למידה", "בנק תרופות", "התרחיש המתגלגל", "בקשת תוכן", "ניהול (Admin)"])

# --- דאשבורד ---
if page == "דאשבורד":
    st.header("ברוכים הבאים ל-LMS של היחידה")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""<div class="med-card"><h3>💊 תרופת היום: Insulin (אינסולין)</h3>
        <p><b>שימוש ב-PICU:</b> לא רק לסוכרת! משמש לטיפול דחוף ב<b>היפרקלמיה</b> (מעביר אשלגן לתוך התא בשילוב גלוקוז).</p>
        <p><b>עובדה מעניינת:</b> ב-DKA, האינסולין עוצר את יצירת גופי הקטון הרבה לפני שהוא מאזן את הסוכר.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.subheader("🏆 מובילי למידה")
        st.write("1. אחות אחראית - 2400 XP")
        st.write("2. דנה כהן - 1850 XP")

# --- מנוע חיפוש ---
elif page == "חיפוש מהיר":
    st.header("🔍 חיפוש נושאים ותרופות")
    search_query = st.text_input("הקלד שם תרופה או מחלה (למשל: אשלגן, שוק, ICP):")
    if search_query:
        results = {k: v for k, v in knowledge_base.items() if search_query in k or search_query in v}
        if results:
            for title, content in results.items():
                st.markdown(f"""<div class="med-card"><b>{title}</b><br>{content}</div>""", unsafe_allow_html=True)
        else:
            st.warning("לא נמצאו תוצאות. נסה מונח אחר או שלח בקשה להוספה.")

# --- בנק תרופות (מבוסס PDF) ---
elif page == "בנק תרופות":
    st.header("בנק תרופות PICU - פרוטוקול שיב''א")
    search_med = st.text_input("חפש תרופה בבנק:")
    for med, info in knowledge_base.items():
        if search_med.lower() in med.lower():
            with st.expander(f"💊 {med}"):
                st.write(info)

# --- בקשת תוכן ---
elif page == "בקשת תוכן":
    st.header("📝 בקשת תוכן חדש")
    st.write("חסרה תרופה? רוצה ללמוד על מחלה שלא מופיעה באתר? כתוב לנו!")
    with st.form("request_form"):
        req_type = st.selectbox("סוג הבקשה:", ["תרופה", "מחלה", "פרוטוקול טכני", "אחר"])
        req_subject = st.text_input("שם הנושא:")
        req_details = st.text_area("פרטים נוספים:")
        if st.form_submit_button("שלח בקשה"):
            st.session_state.requests.append({"user": st.session_state.user_name, "type": req_type, "subject": req_subject})
            st.success("הבקשה נשלחה למנהל האתר ותיבחן בקרוב!")

# --- ניהול (Admin) ---
elif page == "ניהול (Admin)":
    pwd = st.text_input("סיסמת מנהל:", type="password")
    if pwd == "PICU123":
        st.header("🛠 פאנל ניהול")
        st.subheader("בקשות משתמשים לתוכן חדש")
        if st.session_state.requests:
            st.table(pd.DataFrame(st.session_state.requests))
        else:
            st.write("אין בקשות חדשות.")
