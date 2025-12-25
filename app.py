import streamlit as st
import pandas as pd
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# --- הזרקת CSS לעיצוב RTL וכותרות באמצע ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    h1, h2, h3 { text-align: center !important; direction: RTL !important; color: #1e3d59; margin-bottom: 20px; }
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric { direction: RTL !important; text-align: right !important; }
    .med-card { background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 20px; border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2e59a8; color: white; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- מאגר נתונים מורחב (מבוסס על כל ה-PDFים ששלחת) ---

if 'points' not in st.session_state: st.session_state.points = 0
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'requests' not in st.session_state: st.session_state.requests = []

# 1. תוכן לימודי לפי נושאים
topics_content = {
    "המטואונקולוגיה": """
    **פאנציטופניה:** ירידה בכל שורות הדם.
    **מוצרי דם:** 
    - טסיות (PLT): מינון 5mg/kg. אסור ב-IVAC (הלחץ הורס אותן). חובה הקרנה.
    - Cryoprecipitate: מכיל פיברינוגן, פקטור VIII, XIII, vWF. ניתן ב-IVAC עם פילטר.
    - FFP: מכיל גורמי קרישה. סוג AB הוא התורם האוניברסלי.
    **TLS:** היפרקלמיה, היפרפוספטמיה, היפוקלצמיה, היפראוריצמיה. טיפול: הידרציה ורזבוריקז.
    """,
    "שוק וספסיס": """
    **ספסיס:** טיפול תוך שעה! בולוסים של 20ml/kg (עד 60). אמינים בעדיפות: אדרנלין/נוראדרנלין.
    **שוק קרדיוגני:** נזהרים מנוזלים! סימנים: כבד מוגדל, חרחורים.
    **אנפילקסיס:** אדרנלין IM מיידי (0.01mg/kg).
    """,
    "TBI ו-ICP": """
    **יעדים:** CPP (MAP-ICP) בין 40-60. 
    **Cushing Triad:** ברדיקרדיה, ירידה בנשימה, יתר ל"ד (סימן להרניאציה).
    **טיפול:** ראש ב-30 מעלות, מנח נייטרלי, סליין היפרטוני 3% או מניטול (דרך פילטר).
    """,
    "אלקטרוליטים": """
    **אשלגן:** 3.5-5. תיקון IV: קצב מקסימלי 0.5mEq/kg/h. 
    **דגש קריטי:** חובה לתקן היפומגנזמיה לפני תיקון אשלגן, אחרת האשלגן לא יעלה.
    **אינסולין:** ב-DKA או היפרקלמיה. מינון פוש: 0.1 units/kg.
    """
}

# 2. מאגר שאלות לכל נושא
all_questions = [
    {"cat": "המטואונקולוגיה", "q": "מדוע אין לתת טרומבוציטים במכשיר IVAC?", "options": ["הפילטר נסתם", "הלחץ המכני הורס את התאים", "הקצב איטי מדי"], "a": "הלחץ המכני הורס את התאים"},
    {"cat": "המטואונקולוגיה", "q": "איזה סוג פלסמה (FFP) נחשב לתורם אוניברסלי?", "options": ["O", "AB", "A"], "a": "AB"},
    {"cat": "שוק וספסיס", "q": "מהו הטיפול הראשון והחשוב ביותר בשוק אנפילקטי?", "options": ["סטרואידים IV", "אפינפרין IM", "נוזלים מאסיביים"], "a": "אפינפרין IM"},
    {"cat": "שוק וספסיס", "q": "מהו סימן האזהרה המרכזי למתן נוזלים ביתר בשוק קרדיוגני?", "options": ["דופק מהיר", "כבד מוגדל (Liver drop)", "חום"], "a": "כבד מוגדל (Liver drop)"},
    {"cat": "TBI ו-ICP", "q": "מהו ה-GCS שמתחתיו נבצע אינטובציה לצורך הגנה על נתיב אוויר?", "options": ["10", "8", "12"], "a": "8"},
    {"cat": "אלקטרוליטים", "q": "מה יש לתקן לפני שמתקנים היפוקלמיה עמידה?", "options": ["נתרן", "מגנזיום", "קלציום"], "a": "מגנזיום"}
]

# 3. ספריית תרופות ABC (משולב עברית ואנגלית)
drugs_db = {
    "א": [
        {"name": "אדרנלין (Adrenaline)", "info": "החייאה: 0.01mg/kg. אינהלציה לסטרידור: 400mcg/kg (עד 5mg)."},
        {"name": "אדנוזין (Adenosine)", "info": "ל-SVT. מינון: 0.1mg/kg. הזרקה מהירה מאוד (Flash)."},
        {"name": "אטרופין (Atropine)", "info": "לברדיקרדיה. מינון: 0.02mg/kg (מינימום 0.1mg למנה)."}
    ],
    "ב": [
        {"name": "ביקרבונט (Bicarbonate)", "info": "בופר לדם. מינון: 1mEq/kg. לדלל פי 2 בילדים מתחת לגיל שנתיים."},
        {"name": "בוסנתן (Bosentan)", "info": "אנטגוניסט לאנדותלין לטיפול ב-PHTN."}
    ],
    "ד": [
        {"name": "דופמין (Dopamine)", "info": "מינון נמוך (1-5) לכליות, ביניים (5-15) אינוטרופי, גבוה (>15) ואזופרסורי."},
        {"name": "דקסמתזון (Dexa)", "info": "לסטרידור או מנינגיטיס. מינון: 0.6mg/kg."}
    ],
    "מ": [
        {"name": "מילרינון (Milrinone)", "info": "Inodilator. יעד: 0.25-0.75 mcg/kg/min. מוריד Afterload."},
        {"name": "מניטול (Mannitol)", "info": "להורדת ICP. מתן דרך פילטר 1.2 מיקרון."}
    ]
}

# --- תפריט צדי ---
with st.sidebar:
    st.title("🏥 PICU Train & Play")
    if not st.session_state.user_name:
        st.subheader("כניסת משתמש")
        name = st.text_input("שם מלא:")
        if st.button("התחבר"):
            if name: st.session_state.user_name = name; st.rerun()
    else:
        st.success(f"שלום, {st.session_state.user_name}")
        st.metric("הניקוד שלך (XP)", st.session_state.points)
    
    st.divider()
    menu = st.radio("ניווט:", ["דאשבורד", "מרכז למידה נושאי", "מבחן מעורב (Mixed)", "ספריית תרופות ABC", "בקשת תוכן", "ניהול Admin"])

# --- לוגיקת דפים ---

if menu == "דאשבורד":
    st.header("לוח בקרה לימודי")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""<div class="med-card"><h3>💊 תרופת היום: Adenosine</h3>
        <p><b>שימוש:</b> היפוך SVT.</p>
        <p><b>עובדה מעניינת:</b> זמן מחצית החיים שלה הוא פחות מ-10 שניות, לכן חייבים להזריק הכי קרוב לווריד מרכזי ובפולש מהיר.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.subheader("🔍 חיפוש מהיר")
        search = st.text_input("חפש תרופה או מושג:")
        if search:
            st.write(f"מחפש: {search}...")

elif menu == "מרכז למידה נושאי":
    st.header("ספריית ידע ומבחנים נושאיים")
    selected_topic = st.selectbox("בחר נושא ללמידה:", list(topics_content.keys()))
    
    col_text, col_quiz = st.columns([2, 1])
    with col_text:
        st.markdown(f"""<div class="med-card"><h3>{selected_topic}</h3>{topics_content[selected_topic]}</div>""", unsafe_allow_html=True)
    
    with col_quiz:
        st.subheader(f"מבחן: {selected_topic}")
        topic_qs = [q for q in all_questions if q["cat"] == selected_topic]
        if topic_qs:
            q = topic_qs[0] # לוקח את הראשונה לצורך הדגמה
            user_choice = st.radio(q["q"], q["options"], key="topic_q")
            if st.button("בדוק תשובה"):
                if user_choice == q["a"]:
                    st.success("נכון! +20 נקודות")
                    st.session_state.points += 20
                else: st.error(f"טעות. התשובה היא: {q['a']}")
        else: st.write("בקרוב יתווספו שאלות לנושא זה.")

elif menu == "מבחן מעורב (Mixed)":
    st.header("מבחן כללי מעורב")
    num_q = st.slider("בחר מספר שאלות למבחן:", 2, len(all_questions), 5)
    if st.button("צור מבחן אקראי"):
        st.session_state.mixed_qs = random.sample(all_questions, num_q)
        st.rerun()
    
    if 'mixed_qs' in st.session_state:
        for i, q in enumerate(st.session_state.mixed_qs):
            st.write(f"**שאלה {i+1}:** {q['q']}")
            st.radio("בחר תשובה:", q["options"], key=f"mixed_{i}")
        if st.button("הגש מבחן"):
            st.success("המבחן הוגש. בדוק את תשובותיך למעלה!")

elif menu == "ספריית תרופות ABC":
    st.header("🔤 ספריית תרופות PICU")
    letters = list(drugs_db.keys())
    selected_letter = st.select_slider("בחר אות:", options=letters)
    
    for drug in drugs_db[selected_letter]:
        st.markdown(f"""<div class="med-card"><b>{drug['name']}</b><br>{drug['info']}</div>""", unsafe_allow_html=True)

elif menu == "בקשת תוכן":
    st.header("📝 בקשת תוכן חדש")
    with st.form("request_form"):
        subject = st.text_input("נושא חסר (תרופה/מחלה):")
        details = st.text_area("פירוט:")
        if st.form_submit_button("שלח בקשה"):
            st.session_state.requests.append({"שם": st.session_state.user_name, "נושא": subject})
            st.success("הבקשה נרשמה במערכת!")

elif menu == "ניהול Admin":
    pwd = st.text_input("סיסמת מנהל:", type="password")
    if pwd == "PICU123":
        st.subheader("בקשות צוות לתוכן חדש")
        if st.session_state.requests:
            st.table(pd.DataFrame(st.session_state.requests))
        else: st.write("אין בקשות חדשות.")
