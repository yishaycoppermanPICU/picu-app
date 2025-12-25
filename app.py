import streamlit as st
import pandas as pd
from docx import Document
import io

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Learning System", layout="wide", page_icon="🏥")

# --- אתחול משתני מערכת (במציאות יחוברו ל-Google Sheets) ---
if 'points' not in st.session_state: st.session_state.points = 0
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'scenario_step' not in st.session_state: st.session_state.scenario_step = 0

# --- פונקציות עזר ---
def parse_docx(file):
    doc = Document(file)
    return [p.text for p in doc.paragraphs if len(p.text) > 5]

# --- תפריט צדי (Navigation) ---
with st.sidebar:
    st.title("🏥 PICU Train & Play")
    if not st.session_state.user_name:
        st.subheader("רישום משתמש")
        name = st.text_input("שם מלא:")
        email = st.text_input("אימייל:")
        if st.button("התחל ללמוד"):
            st.session_state.user_name = name
            st.rerun()
    else:
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.metric("הניקוד שלך 🏆", st.session_state.points)
        
    st.divider()
    page = st.radio("ניווט", ["דאשבורד", "מרכז ידע", "התרחיש המתגלגל", "מבחן מעורב", "ניהול מערכת (Admin)"])

# --- דף 1: דאשבורד ---
if page == "דאשבורד":
    st.header("לוח בקרה לימודי")
    col1, col2 = st.columns(2)
    with col1:
        st.info("💊 **תרופת היום: Propranolol**\n\nשימוש ב-PICU: המאנגיומות אינפנטיליות. מנגנון: נסיגת כלי דם.")
    with col2:
        st.success("🏆 **טבלת שיאים (Live)**\n1. אחות אחראית - 1200\n2. יוסי כהן - 950")

# --- דף 2: מרכז ידע (מבוסס PDF) ---
elif page == "מרכז ידע":
    st.header("ספריה קלינית (UpToDate)")
    tab1, tab2, tab3 = st.tabs(["המטואונקולוגיה", "שוק וספסיס", "טראומה ו-ICP"])
    
    with tab1:
        st.subheader("פאנציטופניה ומוצרי דם")
        st.write("**טסיות (PLT):** אין לתת ב-IVAC! הלחץ הורס אותן. מינון: 5mg/kg.")
        st.write("**CRYO:** מכיל פיברינוגן, פקטור 8, 13 ו-vWF. ניתן ב-IVAC עם פילטר.")
        
    with tab2:
        st.subheader("ניהול שוק בילדים")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Pediatric_Shock_Algorithm.png/600px-Pediatric_Shock_Algorithm.png", caption="אלגוריתם שוק")

# --- דף 3: התרחיש המתגלגל (האינטגרציה שביקשת) ---
elif page == "התרחיש המתגלגל":
    st.header("🎢 תרחיש מתגלגל: מהמטולוגיה לקריסה")
    
    if st.session_state.scenario_step == 0:
        st.subheader("שלב 1: הקבלה")
        st.write("תינוק בן חודשיים עם AML, לבנים 800,000. מהו הסיכון המיידי?")
        ans = st.radio("בחר:", ["דימום מוחי", "Leukostasis", "היפוגליקמיה"])
        if st.button("בצע"):
            if "Leukostasis" in ans:
                st.session_state.points += 20
                st.session_state.scenario_step = 1
                st.rerun()

    elif st.session_state.scenario_step == 1:
        st.warning("⚠️ התפתח TLS. אשלגן 6.8, חומצה אורית 14.")
        ans = st.selectbox("תרופת בחירה?", ["אלופורינול", "רזבוריקז"])
        if st.button("טפל"):
            st.session_state.scenario_step = 2
            st.rerun()

    elif st.session_state.scenario_step == 2:
        st.error("🆘 שוק קרדיוגני! כבד מוגדל, חרחורים בריאות.")
        ans = st.radio("פעולה:", ["בולוס נוזלים 20ml/kg", "התחלת אמינים (אדרנלין)"])
        if st.button("סיים תרחיש"):
            st.balloons()
            st.success("כל הכבוד! הצלת את המטופל.")
            st.session_state.scenario_step = 0

# --- דף 5: ניהול מערכת ---
elif page == "ניהול מערכת (Admin)":
    pwd = st.text_input("סיסמת מנהל:", type="password")
    if pwd == "PICU123":
        st.header("🛠 פאנל ניהול")
        uploaded_file = st.file_uploader("העלאת שאלות מוורד (.docx)", type="docx")
        if uploaded_file:
            data = parse_docx(uploaded_file)
            st.write(f"נטענו {len(data)} שורות מהקובץ.")
        
        st.subheader("רשימת תפוצה (Emails)")
        st.write("admin@hospital.org, nurse1@hospital.org")