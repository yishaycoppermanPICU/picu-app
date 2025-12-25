import streamlit as st
import pandas as pd
import random
from datetime import datetime
import time
import json
import os

# --- הגדרת קובץ הנתונים (ה"דאטה-בייס" שלך) ---
DB_FILE = "content_db.json"

# --- תוכן התחלתי (ברירת מחדל אם הקובץ לא קיים) ---
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
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Capillary_refill.gif/220px-Capillary_refill.gif",
            "video": ""
        },
        "שוק ספטי": {
            "text": "### שוק ספטי\nזיהום + SIRS. דורש אנטיביוטיקה מהירה ונוזלים.",
            "image": "",
            "video": "https://www.youtube.com/watch?v=5j0zDoY8fBc"
        }
    },
    "תרופות והחייאה": {
        "אדרנלין": {
            "text": "**מינון החייאה:** 0.01 מ\"ג/ק\"ג (1:10,000).",
            "image": "",
            "video": ""
        }
    }
}

# --- פונקציות לניהול הדאטה ---
def load_data():
    """טוען את התוכן מהקובץ. אם לא קיים, יוצר חדש."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONTENT, f, ensure_ascii=False, indent=4)
        return DEFAULT_CONTENT
    else:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_data(data):
    """שומר את התוכן לקובץ."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- הגדרת עמוד ועיצוב ---
st.set_page_config(
    page_title="אֲחָיוּת - טיפול נמרץ ילדים",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS לעיצוב RTL, כרטיסיות ותמונות ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Rubik', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #0056b3; font-weight: 700; }
    
    /* כרטיסיות */
    .content-card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-right: 5px solid #0056b3;
    }
    
    /* התאמות לנגן וידאו ותמונות */
    .stVideo, .stImage {
        border-radius: 10px;
        overflow: hidden;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* כפתורים וטפסים לימין */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div { direction: rtl; text-align: right; }
    .stSidebar { direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- טעינת נתונים לזיכרון ---
if 'content_db' not in st.session_state:
    st.session_state.content_db = load_data()
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- סרגל צד (התחברות ותפריט) ---
with st.sidebar:
    st.title("🏥 אֲחָיוּת")
    
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
        st.success(f"מחובר: {st.session_state.user_info['name']}")
        if st.button("יציאה"):
            st.session_state.user_info = {}
            st.rerun()
            
    st.markdown("---")
    menu = st.radio("תפריט:", ["🏠 דף הבית", "📚 חומר לימוד", "⚙️ ניהול תוכן (CMS)"])

# --- לוגיקה ראשית ---

# 1. דף הבית
if menu == "🏠 דף הבית":
    st.title("מרכז ידע - טיפול נמרץ ילדים")
    st.markdown("""
    <div class="content-card">
    ברוכים הבאים. המערכת מאפשרת למידה דינמית ועדכון נהלים בזמן אמת.
    </div>
    """, unsafe_allow_html=True)

# 2. חומר לימוד (תצוגה)
elif menu == "📚 חומר לימוד":
    st.title("📚 הספרייה המקצועית")
    
    # שליפת המידע מה-DB
    db = st.session_state.content_db
    
    # בחירת נושא ראשי
    main_topics = list(db.keys())
    if not main_topics:
        st.warning("עדיין אין תוכן במערכת. לך ל'ניהול תוכן' כדי להוסיף.")
    else:
        selected_main = st.selectbox("בחר נושא ראשי:", main_topics)
        
        # בחירת תת-נושא
        sub_topics = list(db[selected_main].keys())
        selected_sub = st.radio("בחר נושא:", sub_topics, horizontal=True)
        
        st.markdown("---")
        
        # הצגת התוכן
        content_data = db[selected_main][selected_sub]
        
        # 1. כרטיס טקסט
        st.markdown(f'<div class="content-card">{content_data["text"]}</div>', unsafe_allow_html=True) # שימוש במרקדאון רגיל בתוך HTML לא תמיד עובד טוב, עדיף st.markdown נקי:
        
        # הצגה נקייה של הטקסט (תומך בכותרות, בולטים וכו')
        # st.markdown(content_data["text"]) 
        
        col_media1, col_media2 = st.columns(2)
        
        # 2. תמונה (אם יש)
        with col_media1:
            if content_data.get("image"):
                st.image(content_data["image"], caption="תמונה להמחשה", use_container_width=True)
                
        # 3. וידאו (אם יש)
        with col_media2:
            if content_data.get("video"):
                st.video(content_data["video"])

# 3. ממשק ניהול (CMS)
elif menu == "⚙️ ניהול תוכן (CMS)":
    st.title("⚙️ עריכת תכנים")
    
    # בדיקת הרשאות (רק ישי)
    user_email = st.session_state.user_info.get('email', '')
    if user_email != 'yishaycopp@gmail.com':
        st.error("⛔ אין לך הרשאת עריכה. (רק למנהל המערכת)")
    else:
        st.info("כאן אתה יכול לערוך את כל התוכן באתר, להוסיף תמונות וסרטונים.")
        
        db = st.session_state.content_db
        
        # לשוניות: עריכה קיימת / הוספה חדשה
        tab1, tab2, tab3 = st.tabs(["✏️ עריכת קיים", "➕ הוספת נושא חדש", "🗑️ מחיקה"])
        
        # --- עריכת קיים ---
        with tab1:
            if db:
                edit_main = st.selectbox("בחר נושא לעריכה:", list(db.keys()), key='edit_main')
                edit_sub = st.selectbox("בחר תת-נושא:", list(db[edit_main].keys()), key='edit_sub')
                
                # טעינת הנתונים הקיימים לתוך הטופס
                current_data = db[edit_main][edit_sub]
                
                with st.form("edit_form"):
                    new_text = st.text_area("תוכן הטקסט (ניתן להשתמש ב-Markdown)", value=current_data['text'], height=300)
                    new_img = st.text_input("קישור לתמונה (URL)", value=current_data.get('image', ''))
                    new_vid = st.text_input("קישור לוידאו (YouTube/MP4)", value=current_data.get('video', ''))
                    
                    if st.form_submit_button("שמור שינויים 💾"):
                        # עדכון הזיכרון
                        st.session_state.content_db[edit_main][edit_sub] = {
                            "text": new_text,
                            "image": new_img,
                            "video": new_vid
                        }
                        # שמירה לקובץ
                        save_data(st.session_state.content_db)
                        st.success("התוכן עודכן בהצלחה!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("אין תוכן לעריכה.")

        # --- הוספת חדש ---
        with tab2:
            add_type = st.radio("מה להוסיף?", ["נושא ראשי חדש", "תת-נושא לנושא קיים"])
            
            if add_type == "נושא ראשי חדש":
                with st.form("new_main_topic"):
                    new_main_name = st.text_input("שם הנושא הראשי (למשל: נפרולוגיה)")
                    if st.form_submit_button("צור נושא"):
                        if new_main_name and new_main_name not in db:
                            st.session_state.content_db[new_main_name] = {}
                            save_data(st.session_state.content_db)
                            st.success(f"נושא {new_main_name} נוצר!")
                            st.rerun()
                        else:
                            st.error("שם לא תקין או כבר קיים")
                            
            else: # הוספת תת נושא
                if db:
                    target_main = st.selectbox("לאיזה נושא ראשי להוסיף?", list(db.keys()))
                    with st.form("new_sub_topic"):
                        new_sub_name = st.text_input("שם תת-הנושא (למשל: אי ספיקת כליות)")
                        # תוכן התחלתי
                        st.markdown("**תוכן ראשוני:**")
                        init_text = st.text_area("טקסט")
                        init_img = st.text_input("לינק לתמונה")
                        init_vid = st.text_input("לינק לוידאו")
                        
                        if st.form_submit_button("צור תת-נושא"):
                            if new_sub_name:
                                st.session_state.content_db[target_main][new_sub_name] = {
                                    "text": init_text,
                                    "image": init_img,
                                    "video": init_vid
                                }
                                save_data(st.session_state.content_db)
                                st.success("נוסף בהצלחה!")
                                st.rerun()
                else:
                    st.warning("צור קודם נושא ראשי.")

        # --- מחיקה ---
        with tab3:
            st.warning("זהירות: מחיקה היא סופית!")
            del_main = st.selectbox("נושא למחיקה:", list(db.keys()), key='del_main')
            if st.button("מחק את כל הנושא הראשי הזה"):
                del st.session_state.content_db[del_main]
                save_data(st.session_state.content_db)
                st.rerun()
