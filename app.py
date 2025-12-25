import streamlit as st
import pandas as pd
from datetime import datetime

# --- הגדרת עמוד ועיצוב ---
st.set_page_config(page_title="אֲחָיוּת עם ישי קופרמן", layout="wide", initial_sidebar_state="expanded")

# עיצוב לימין-לשמאל (RTL) והתאמות ויזואליות - גרסה משופרת
st.markdown("""
<style>
    /* כיוון כללי של האפליקציה */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* יישור טקסטים בכותרות ופסקאות */
    h1, h2, h3, h4, h5, h6, p, div, span {
        text-align: right;
    }
    
    /* יישור תפריט הצד */
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    /* יישור שדות קלט (Input fields) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        direction: rtl;
        text-align: right;
    }
    
    /* יישור כפתורי רדיו וצ'קבוקסים */
    .stRadio, .stCheckbox {
        direction: rtl;
        text-align: right;
    }
    
    /* תיקון ספציפי למרקדאון */
    .stMarkdown {
        text-align: right !important;
    }
    
    /* צבע כותרת ראשית */
    h1 { color: #2E86C1; }
</style>
""", unsafe_allow_html=True)

# --- דאטה דמי (בהמשך נחליף את זה בקבצים אמיתיים) ---
if 'questions_db' not in st.session_state:
    st.session_state.questions_db = [
        {
            "id": 1,
            "topic": "הנשמה",
            "question": "מהי האינדיקציה המרכזית להנשמה בלחץ חיובי בילד עם אי ספיקה נשימתית?",
            "options": ["ירידה במצב ההכרה", "pH מתחת ל-7.25", "סטורציה מתחת ל-90% עם חמצן", "כל התשובות נכונות"],
            "correct": "כל התשובות נכונות",
            "explanation": "אי ספיקה נשימתית בילדים מוגדרת שילוב של קליניקה וערכי גזים. כל המצבים שתוארו מחייבים שקילת הנשמה."
        },
        {
            "id": 2,
            "topic": "תרופות",
            "question": "מה המינון המקובל לאדרנלין בהחייאה (IV/IO)?",
            "options": ["0.1 mg/kg", "0.01 mg/kg", "1 mg/kg", "0.5 mg/kg"],
            "correct": "0.01 mg/kg",
            "explanation": "המינון בהחייאת ילדים הוא 0.01 מ״ג לק״ג (שהם 0.1 מ״ל לק״ג בתמיסה של 1:10,000)."
        }
    ]

# --- ניהול משתמש (Session State) ---
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

# --- פונקציות עזר ---
def save_score(user, score, topic):
    if 'leaderboard' not in st.session_state:
        st.session_state.leaderboard = []
    
    st.session_state.leaderboard.append({
        "שם": user['name'],
        "מחלקה": user['department'],
        "בית חולים": user['hospital'],
        "נושא": topic,
        "ציון": score,
        "תאריך": datetime.now().strftime("%d/%m %H:%M")
    })

# --- תפריט צד (Sidebar) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/nurse-male--v1.png", width=80) 
    st.title("פרופיל משתמש")
    
    # בדיקה האם המשתמש כבר מחובר
    if not st.session_state.user_info:
        st.info("אנא הזן פרטים כדי להיכנס למערכת")
        
        # יצירת טופס (Form) - ככה הנתונים נשלחים רק בלחיצה על הכפתור
        with st.form("login_form"):
            name = st.text_input("שם מלא")
            email = st.text_input("אימייל")
            hospital = st.selectbox("בית חולים", ["שיבא - תל השומר", "שניידר", "איכילוב - דנה", "הדסה", "רמב\"ם", "סורוקה", "אחר"])
            department = st.text_input("מחלקה", value="טיפול נמרץ ילדים")
            
            # כפתור האישור בתוך הטופס
            submit_button = st.form_submit_button("אישור פרטים וכניסה")
        
        if submit_button:
            if name and email:
                st.session_state.user_info = {"name": name, "email": email, "hospital": hospital, "department": department}
                st.success(f"ברוך הבא, {name}!")
                st.rerun() # רענון כדי שהסטטוס יתעדכן מיד
            else:
                st.error("חובה למלא שם ואימייל")
    
    else:
        # אם המשתמש מחובר - הצג את הפרטים וכפתור יציאה
        user = st.session_state.user_info
        st.success(f"מחובר כ: {user['name']}")
        st.text(f"{user['hospital']}")
        
        if st.button("התנתק / החלף משתמש"):
            st.session_state.user_info = {}
            st.rerun()

    st.markdown("---")
    
    # תפריט ניווט
    menu = st.radio(
        "נווט באתר:",
        ["דף הבית", "חומר לימוד", "תרגול ומבחנים", "סימולציות (תרחישים)", "טבלת המובילים 🏆", "ניהול"]
    )

# --- לוגיקה ראשית ---

if menu == "דף הבית":
    st.title("אֲחָיוּת - עם ישי קופרמן")
    st.subheader("מערכת למידה מתקדמת לצוות טיפול נמרץ ילדים (PICU)")
    st.markdown("""
    ברוכים הבאים למערכת הלמידה. כאן תוכלו:
    * לקרוא פרוטוקולים ומאמרים מקצועיים.
    * לתרגל מבחנים לפי נושאים.
    * להתחרות עם מחלקות אחרות בארץ.
    * לבצע סימולציות קליניות של מקרי קיצון.
    """)
    
    if not st.session_state.user_info:
        st.warning("⬅️ נא להירשם בתפריט הצד כדי להתחיל")

elif menu == "חומר לימוד":
    st.header("📚 חומר לימוד")
    topic = st.selectbox("בחר נושא ללמידה:", ["הנשמה", "המודינמיקה", "פרמקולוגיה", "פרוצדורות"])
    st.info(f"מציג חומר לימוד בנושא: {topic}")
    st.markdown("### עקרונות בסיסיים")
    st.write("כאן יופיע התוכן המקצועי המפורט...")

elif menu == "תרגול ומבחנים":
    st.header("📝 תרגול ומבחנים")
    
    if not st.session_state.user_info:
        st.error("יש להזין פרטי משתמש וללחוץ על אישור בתפריט הצד כדי להתחיל מבחן.")
    else:
        # הגדרות מבחן
        col1, col2 = st.columns(2)
        with col1:
            quiz_topic = st.selectbox("בחר נושא למבחן:", ["מעורבל", "הנשמה", "תרופות"])
        with col2:
            num_questions = st.slider("מספר שאלות:", 1, 10, 5)
        
        if st.button("התחל מבחן"):
            st.session_state.current_quiz = st.session_state.questions_db
            st.session_state.quiz_started = True
            st.rerun()

        # הצגת המבחן
        if st.session_state.get('quiz_started'):
            st.markdown("---")
            score = 0
            for idx, q in enumerate(st.session_state.current_quiz):
                st.subheader(f"שאלה {idx+1}: {q['question']}")
                user_ans = st.radio(f"בחר תשובה לשאלה {idx+1}", q['options'], key=f"q_{idx}")
                
                if st.checkbox(f"הצג תשובה והסבר לשאלה {idx+1}", key=f"chk_{idx}"):
                    if user_ans == q['correct']:
                        st.success("✅ תשובה נכונה!")
                    else:
                        st.error(f"❌ טעות. התשובה הנכונה היא: {q['correct']}")
                    st.info(f"📖 **הסבר:** {q['explanation']}")
            
            if st.button("סיים מבחן ושמור ציון"):
                save_score(st.session_state.user_info, 100, quiz_topic)
                st.balloons()
                st.success("הציון נשמר בהצלחה! בדוק את טבלת המובילים.")

elif menu == "סימולציות (תרחישים)":
    st.header("🚑 סימולציה מתגלגלת")
    st.warning("מודול זה בפיתוח...")

elif menu == "טבלת המובילים 🏆":
    st.header("🏆 טבלת האלופים בטיפול נמרץ")
    
    if 'leaderboard' in st.session_state and st.session_state.leaderboard:
        df = pd.DataFrame(st.session_state.leaderboard)
        
        filter_mode = st.radio("הצג לפי:", ["אישי", "מחלקה/בית חולים"], horizontal=True)
        
        if filter_mode == "אישי":
            st.dataframe(df, use_container_width=True)
        else:
            grouped = df.groupby("בית חולים")["ציון"].mean().reset_index().sort_values("ציון", ascending=False)
            st.bar_chart(grouped, x="בית חולים", y="ציון")
    else:
        st.info("עדיין אין נתונים. היה הראשון להיבחן!")

elif menu == "ניהול":
    st.header("⚙️ ממשק ניהול")
    
    current_email = st.session_state.user_info.get('email', '')
    
    if current_email == 'yishaycopp@gmail.com':
        st.success("זוהה מנהל מערכת: ישי קופרמן")
        
        tab1, tab2 = st.tabs(["הוספת שאלות", "ניהול קבצים"])
        
        with tab1:
            st.subheader("הוספת שאלה חדשה למאגר")
            with st.form("add_question_form"):
                new_q_topic = st.text_input("נושא")
                new_q_text = st.text_area("תוכן השאלה")
                new_q_correct = st.text_input("התשובה הנכונה")
                new_q_distractor1 = st.text_input("מסיח 1")
                new_q_distractor2 = st.text_input("מסיח 2")
                new_q_distractor3 = st.text_input("מסיח 3")
                new_q_explanation = st.text_area("הסבר לתשובה")
                
                submitted_q = st.form_submit_button("שמור שאלה")
                if submitted_q:
                    st.success("השאלה נוספה למאגר (כרגע מקומית)")
                
        with tab2:
            st.file_uploader("העלה קבצי תוכן (PDF/Word)", accept_multiple_files=True)
            
    else:
        st.error("אין לך הרשאה לצפות בדף זה. גישה למנהלים בלבד.")
