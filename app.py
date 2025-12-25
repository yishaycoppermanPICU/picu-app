import streamlit as st
import pandas as pd
from docx import Document
import io

# --- הגדרות דף ועיצוב RTL ---
st.set_page_config(page_title="PICU Learning Hub", layout="wide", page_icon="🏥")

# הזרקת CSS לתיקון יישור לימין (RTL) ועיצוב רפואי
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Assistant', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric {
        direction: RTL !important;
        text-align: right !important;
    }
    /* תיקון לסיידבר */
    [data-testid="stSidebar"] {
        direction: RTL !important;
        text-align: right !important;
    }
    /* עיצוב כרטיסיות תרופה */
    .med-card {
        background-color: #f0f2f6;
        border-right: 5px solid #ff4b4b;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול מצב (Session State) ---
if 'points' not in st.session_state: st.session_state.points = 0
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'scenario_step' not in st.session_state: st.session_state.scenario_step = 0

# --- פונקציות ניהול ---
def parse_docx_questions(file):
    doc = Document(file)
    # לוגיקה לחילוץ שאלות (פשוטה לצורך הדגמה)
    return [p.text for p in doc.paragraphs if len(p.text) > 10]

# --- תפריט צדי ---
with st.sidebar:
    st.title("🏥 PICU Train & Play")
    st.write("מערכת תרגול לצוות טיפול נמרץ ילדים")
    
    if not st.session_state.user_name:
        st.subheader("כניסת משתמש")
        name = st.text_input("שם מלא:")
        email = st.text_input("אימייל (לרשימת תפוצה):")
        if st.button("התחל ללמוד"):
            if name and email:
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("נא להזין שם ואימייל")
    else:
        st.success(f"שלום, **{st.session_state.user_name}**")
        st.metric("הניקוד המצטבר שלך", f"{st.session_state.points} XP")
    
    st.divider()
    page = st.radio("ניווט באתר:", 
                    ["דאשבורד", "מרכז ידע", "התרחיש המתגלגל", "מבחן מעורב", "מאגר תרופות", "ניהול (Admin)"])

# --- דף 1: דאשבורד (Dashboard) ---
if page == "דאשבורד":
    st.header("לוח בקרה לימודי")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="med-card">
            <h3>💊 תרופת היום: Propranolol (דרלין)</h3>
            <p><b>עובדה מעניינת:</b> ב-PICU אנחנו משתמשים בה לא רק ללחץ דם, אלא כטיפול קו ראשון ב<b>המאנגיומות</b> (Hemangiomas) אינפנטיליות. היא גורמת לנסיגה של כלי הדם ע"י כיווץ כלי דם ועיכוב גורמי צמיחה.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("🏆 טבלת שיאים מחלקתית")
        leaderboard = pd.DataFrame({
            "שם": ["אחות אחראית", "דנה כהן", "ערן לוי"],
            "ניקוד": [1250, 890, 750]
        })
        st.table(leaderboard)

# --- דף 2: מרכז ידע (Knowledge Hub) ---
elif page == "מרכז ידע":
    st.header("ספריה קלינית - מבוסס UpToDate")
    
    topic = st.selectbox("בחר נושא ללמידה:", ["המטואונקולוגיה", "שוק וספסיס", "TBI ו-ICP", "DKA בילדים"])
    
    if topic == "המטואונקולוגיה":
        st.subheader("פאנציטופניה ומוצרי דם")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**טסיות (PLT):**")
            st.write("- התוויה: מתחת ל-10,000 או במצבי HIT/TTP.")
            st.write("- **דגש טכני:** אין לתת ב-IVAC! הלחץ הורס את הטסיות. יש להשתמש במזרק פאמפ.")
        with col2:
            st.info("**Cryoprecipitate (קריו):**")
            st.write("- מכיל: פיברינוגן, פקטור VIII, פקטור XIII, vWF.")
            st.write("- התוויה: מחסור בפיברינוגן או דמם חריף.")
            
        if st.button("בחן אותי על המטולוגיה (+20 נק')"):
            q = st.radio("ילד עם סוג דם O זקוק לפלסמה (FFP). אין סוג O במלאי. מה ניתן לתת?", 
                         ["סוג A", "סוג B", "סוג AB"])
            if st.button("בדוק תשובה"):
                if q == "סוג AB":
                    st.success("נכון מאוד! בפלסמה AB אין נוגדנים ולכן היא בטוחה לכולם.")
                    st.session_state.points += 20
                else:
                    st.error("טעות. פלסמה AB היא ה-Universal Donor.")

# --- דף 3: התרחיש המתגלגל (The Rolling Scenario) ---
elif page == "תרחיש מתגלגל":
    st.header("🎢 סימולציה: מהמטולוגיה לקריסה")
    
    if st.session_state.scenario_step == 0:
        st.subheader("שלב 1: קבלת המטופל")
        st.write("תינוק בן חודשיים התקבל עם AML. בבדיקות דם: WBC 810,000. הילד נראה אפטי.")
        ans = st.radio("מהי הפעולה הדחופה ביותר למניעת Leukostasis?", ["מתן בולוס נוזלים", "התחלת הידרציה מאסיבית ורזבוריקז", "מתן דם דחוף"])
        if st.button("בצע פעולה"):
            st.session_state.scenario_step = 1
            st.rerun()

    elif st.session_state.scenario_step == 1:
        st.warning("⚠️ המעבדה חוזרת: אשלגן 6.8, פוספט 9.0, חומצה אורית 15. אבחנה: TLS.")
        ans = st.radio("הילד מפתח הפרעת קצב במוניטור. מה הטיפול המיידי?", ["קלציום גלוקונט", "אינסולין וסוכר", "פוסיד"])
        if st.button("טפל"):
            st.session_state.scenario_step = 2
            st.rerun()

    elif st.session_state.scenario_step == 2:
        st.error("🆘 הילד בקריסה! מילוי קפילרי 5 שניות, כבד מוגדל ב-4 ס''מ מהקשת, חרחורים בריאות.")
        ans = st.radio("איזה שוק זה?", ["שוק היפוולמי", "שוק קרדיוגני", "שוק ספטי"])
        if st.button("סיים תרחיש"):
            st.balloons()
            st.success("עבודה מעולה! זיהית את המעבר לשוק קרדיוגני (עומס נוזלים וכשל לבבי).")
            st.session_state.scenario_step = 0

# --- דף 6: ניהול (Admin) ---
elif page == "ניהול (Admin)":
    st.header("🛠 פאנל ניהול (מוגן סיסמה)")
    pwd = st.text_input("הזן סיסמת מנהל:", type="password")
    if pwd == "PICU123":
        st.subheader("העלאת תוכן חדש")
        file = st.file_uploader("העלה שאלות מקובץ Word", type="docx")
        if file:
            questions = parse_docx_questions(file)
            st.write(f"זוהו {len(questions)} שאלות חדשות.")
        
        st.subheader("רשימת תפוצה (מיילים)")
        st.write("admin@hospital.org, nurse1@hospital.org, doctor2@hospital.org")
