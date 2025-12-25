import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# --- הזרקת CSS ל-RTL, כותרות באמצע ויישור טבלאות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    
    /* יישור כותרות לאמצע */
    h1, h2, h3, h4 { text-align: center !important; direction: RTL !important; color: #1e3d59; }
    
    /* יישור טקסט וטבלאות לימין */
    .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stDataFrame, .stTable { 
        direction: RTL !important; text-align: right !important; 
    }
    
    /* כפיית יישור לימין על תאי טבלה */
    [data-testid="stTable"] td, [data-testid="stTable"] th { text-align: right !important; }
    
    .med-card { background-color: #ffffff; border-right: 8px solid #2e59a8; padding: 20px; border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2e59a8; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור לגוגל שיטס ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_user_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["name", "email", "score"])

def save_user(name, email, score):
    df = get_user_data()
    if email in df['email'].values:
        df.loc[df['email'] == email, 'score'] = score
    else:
        new_row = pd.DataFrame([{"name": name, "email": email, "score": score}])
        df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Sheet1", data=df)

# --- ניהול מצב (Session State) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_email' not in st.session_state: st.session_state.user_email = ""
if 'points' not in st.session_state: st.session_state.points = 0

# --- מסך כניסה (Mandatory Login) ---
if not st.session_state.logged_in:
    st.title("🏥 ברוכים הבאים למערכת הלמידה PICU")
    st.subheader("נא להתחבר כדי להתחיל בתרגול")
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            name = st.text_input("שם מלא:")
            email = st.text_input("כתובת אימייל:")
            if st.button("כניסה למערכת"):
                if name and email:
                    st.session_state.user_name = name
                    st.session_state.user_email = email
                    st.session_state.logged_in = True
                    # בדיקה אם המשתמש קיים בשיטס ומשוך את הניקוד שלו
                    df = get_user_data()
                    if email in df['email'].values:
                        st.session_state.points = int(df.loc[df['email'] == email, 'score'].values[0])
                    st.rerun()
                else:
                    st.error("יש למלא שם ואימייל")
    st.stop()

# --- תוכן האתר (אחרי התחברות) ---
with st.sidebar:
    st.write(f"שלום, **{st.session_state.user_name}**")
    st.metric("XP - ניקוד", st.session_state.points)
    if st.button("יציאה"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    page = st.radio("תפריט:", ["דאשבורד", "מרכז ידע", "מבחן אישי", "ספריית תרופות ABC", "בקשת תוכן", "ניהול"])

# --- דף דאשבורד וטבלת שיאים ---
if page == "דאשבורד":
    st.header("לוח בקרה לימודי")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""<div class="med-card"><h3>💊 תרופת היום: Potassium (אשלגן)</h3>
        <p><b>דגש קריטי:</b> בחולים עם היפומגנזמיה והיפוקלמיה במקביל - <b>חובה לתקן מגנזיום תחילה!</b> אחרת האשלגן לא ייספג בתאים.</p>
        <p><b>עובדה מעניינת:</b> אשלגן הוא הקטיון המרכזי בתוך התא, ושינויים קלים בו משפיעים מיידית על סף הגירוי של שריר הלב.</p></div>""", unsafe_allow_html=True)
    
    with col2:
        st.subheader("🏆 טבלת שיאים (Live)")
        leader_df = get_user_data().sort_values(by="score", ascending=False).head(5)
        # הסרת עמודת המייל מהתצוגה הציבורית והצגת השם והניקוד בלבד
        st.table(leader_df[["name", "score"]].rename(columns={"name": "שם", "score": "ניקוד"}))

# --- ספריית תרופות ABC (מבוסס על ה-PDF של שיב"א) ---
elif page == "ספריית תרופות ABC":
    st.header("🔤 ספריית תרופות PICU")
    drugs_data = {
        "א": [
            {"name": "אדרנלין (Adrenaline)", "info": "מינון החייאה: 0.01mg/kg. אינהלציה לסטרידור: 400mcg/kg (מקסימום 5mg)."},
            {"name": "אדנוזין (Adenosine)", "info": "ל-SVT. הזרקה מהירה (Flash) בווריד הכי קרוב ללב. מינון: 0.1mg/kg."},
            {"name": "אטרופין (Atropine)", "info": "לברדיקרדיה. מינון: 0.02mg/kg (מינימום 0.1mg למנה למניעת אפקט פרדוקסלי)."}
        ],
        "פ": [
            {"name": "פוסיד (Furosemide)", "info": "משתן לולאה. מינון: 0.5-2 mg/kg. בילדים מתחת לגיל שנתיים יש לדלל פי 2."},
            {"name": "פנטניל (Fentanyl)", "info": "אופיואיד קצר טווח. מינון לתינוקות: 1-2 mcg/kg. דגש: עלול לגרום ל-Chest Rigidity."}
        ],
        "מ": [
            {"name": "מניטול (Mannitol)", "info": "להורדת ICP. פועל תוך משיכת נוזלים לכלי הדם. חובה להשתמש בפילטר 1.2 מיקרון."},
            {"name": "מילרינון (Milrinone)", "info": "Inodilator. יעד מינון: 0.25-0.75 mcg/kg/min."}
        ]
    }
    
    letter = st.select_slider("בחר אות:", options=sorted(drugs_data.keys()))
    for d in drugs_data[letter]:
        st.markdown(f"""<div class="med-card"><b>{d['name']}</b><br>{d['info']}</div>""", unsafe_allow_html=True)

# (המשך הקוד עם מרכז ידע ומבחנים - ניתן להוסיף את כל השאלות מה-PDF כאן)
