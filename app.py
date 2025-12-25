import streamlit as st
import pandas as pd
import random
from datetime import datetime
import time
import json
import os

# --- הגדרת קובץ הנתונים ---
DB_FILE = "content_db.json"

# --- תוכן התחלתי ---
DEFAULT_CONTENT = {
    "מצבי שוק (Shock)": {
        "שוק היפוולמי": {
            "text": """### שוק היפוולמי / המורגי
הסיבה הנפוצה ביותר לשוק בילדים. נגרם מאובדן נפח דם או נוזלים.

**סימנים קליניים:**
* טכיקרדיה
* מילוי קפילרי איטי (>2 שניות)
* גפיים קרות

**טיפול:** בולוס נוזלים 20 מ"ל/ק"ג.""",
            "image": "",
            "video": ""
        }
    }
}

# --- פונקציות לניהול הדאטה ---
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONTENT, f, ensure_ascii=False, indent=4)
        return DEFAULT_CONTENT
    else:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- הגדרת עמוד ---
st.set_page_config(
    page_title="אֲחָיוּת - עם ישי קופרמן",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS מתוקן ליישור לימין ועיצוב ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;700&display=swap');
    
    /* הגדרות גלובליות לכל האלמנטים */
    html, body, .stApp {
        font-family: 'Rubik', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* יישור כותרות */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Rubik', sans-serif;
        text-align: right !important;
        direction: rtl !important;
        color: #0056b3;
    }

    /* יישור טקסט רגיל ורשימות - התיקון הקריטי */
    .stMarkdown, p, div, span {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* תיקון ספציפי לרשימות (בולטים) שבורחים לשמאל */
    ul {
        direction: rtl !important;
        text-align: right !important;
        padding-right: 20px !important; /* הזחה מימין */
        margin-left: auto !important;
        margin-right: 0 !important;
    }
    li {
        direction: rtl !important;
        text-align: right !important;
        list-style-position: inside; /* מכניס את הנקודה לתוך השורה */
    }

    /* כרטיסיות */
    .content-card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-right: 5px solid #0056b3;
        text-align: right;
    }
    
    /* תיקון עמודות */
    div[data-testid="column"] {
        text-align: right !important;
        direction: rtl !important;
    }

    /* כפתורים וטפסים */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div { direction: rtl; text-align: right; }
    
    /* הסתרת כפתורי ניהול של סטרימליט למראה נקי */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- טעינת נתונים ---
if 'content_db' not in st.session_state:
    st.session_state.content_db = load_data()
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- סרגל צד ---
with st.sidebar:
    st.title("🏥 פרופיל")
    
    if not st.session_state.user_info:
        with st.form("login"):
            st.write("כניסה למערכת")
            name = st.text_input("שם")
            email = st.text_input("מייל")
            if st.form_submit_button("כניסה"):
                if name and email:
                    st.session_state.user_info = {"name": name, "email": email}
                    st.rerun()
    else:
        st.success(f"שלום, {st.session_state.user_info['name']}")
        if st.button("יציאה"):
            st.session_state.user_info = {}
            st.rerun()
            
    st.markdown("---")
    menu = st.radio("תפריט:", ["🏠 דף הבית", "📚 חומר לימוד", "⚙️ ניהול תוכן"])

# --- לוגיקה ראשית ---

# 1. דף הבית
if menu == "🏠 דף הבית":
    # הכותרת הראשית כפי שביקשת
    st.title("אֲחָיוּת - עם ישי קופרמן")
    
    # כותרת המשנה
    st.header("טיפול נמרץ ילדים - PICU")
    
    st.markdown("---")
    
    st.markdown("""
    <div class="content-card">
    <strong>ברוכים הבאים למערכת הלמידה.</strong><br>
    מערכת זו מבוססת על הפרוטוקולים העדכניים של המחלקה.<br><br>
    <strong>מה במערכת?</strong>
    <ul>
        <li>📚 <strong>חומר עיוני:</strong> סיכומים על תרופות, החייאה, ספסיס וטראומה.</li>
        <li>📝 <strong>מבחנים:</strong> שאלות אמריקאיות לתרגול ידע עם הסברים מפורטים.</li>
        <li>🏆 <strong>תחרות:</strong> צבירת נקודות והשוואה בין מחלקות.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # עמודות לטיפים - ב-RTL עמודה 1 היא הימנית
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("💡 **טיפ יומי:** בהחייאה, אם יש היפרקלמיה, תן קלציום גלוקונט להגנה על הלב לפני מתן אינסולין.")
    
    with col2:
        st.warning("⚠️ **שים לב:** המינון לאדרנלין בהחייאה הוא 0.01 מ\"ג לק\"ג (ולא 0.1!).")

# 2. חומר לימוד
elif menu == "📚 חומר לימוד":
    st.title("אֲחָיוּת - עם ישי קופרמן")
    st.subheader("טיפול נמרץ ילדים - PICU")
    st.markdown("---")
    
    db = st.session_state.content_db
    main_topics = list(db.keys())
    
    if not main_topics:
        st.warning("אין תוכן. יש להוסיף בניהול.")
    else:
        col_nav, col_content = st.columns([1, 3])
        
        with col_nav:
            selected_main = st.selectbox("נושא ראשי:", main_topics)
            sub_topics = list(db[selected_main].keys())
            selected_sub = st.radio("בחר פרק:", sub_topics)
        
        with col_content:
            content_data = db[selected_main][selected_sub]
            
            # הצגת הטקסט בתוך כרטיסייה
            st.markdown(f"""
            <div class="content-card">
            {content_data["text"]}
            </div>
            """, unsafe_allow_html=True)
            
            # מדיה
            if content_data.get("image"):
                st.image(content_data["image"], use_container_width=True)
            if content_data.get("video"):
                st.video(content_data["video"])

# 3. ניהול תוכן
elif menu == "⚙️ ניהול תוכן":
    st.title("ממשק ניהול")
    
    user_email = st.session_state.user_info.get('email', '')
    if user_email != 'yishaycopp@gmail.com':
        st.error("⛔ אין הרשאה.")
    else:
        db = st.session_state.content_db
        tab1, tab2 = st.tabs(["✏️ עריכה", "➕ הוספה"])
        
        with tab1:
            if db:
                edit_main = st.selectbox("נושא ראשי:", list(db.keys()))
                edit_sub = st.selectbox("תת-נושא:", list(db[edit_main].keys()))
                current = db[edit_main][edit_sub]
                
                with st.form("edit"):
                    new_text = st.text_area("תוכן (Markdown)", value=current['text'], height=300)
                    new_img = st.text_input("תמונה (URL)", value=current.get('image', ''))
                    new_vid = st.text_input("וידאו (URL)", value=current.get('video', ''))
                    
                    if st.form_submit_button("שמור"):
                        st.session_state.content_db[edit_main][edit_sub] = {"text": new_text, "image": new_img, "video": new_vid}
                        save_data(st.session_state.content_db)
                        st.success("נשמר!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("אין תוכן.")

        with tab2:
            new_main = st.text_input("שם נושא ראשי חדש (או השאר ריק להוספה לקיים)")
            target_main = st.selectbox("או בחר נושא קיים:", list(db.keys()) if db else [])
            
            with st.form("add"):
                new_sub = st.text_input("שם תת-נושא חדש")
                init_text = st.text_area("תוכן")
                
                if st.form_submit_button("הוסף"):
                    final_main = new_main if new_main else target_main
                    if final_main and new_sub:
                        if final_main not in st.session_state.content_db:
                            st.session_state.content_db[final_main] = {}
                        
                        st.session_state.content_db[final_main][new_sub] = {"text": init_text, "image": "", "video": ""}
                        save_data(st.session_state.content_db)
                        st.success("נוסף!")
                        st.rerun()
