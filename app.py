import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# --- הגדרות דף ---
st.set_page_config(page_title="PICU Master Hub", layout="wide", page_icon="🏥")

# --- CSS מתקדם: עיצוב רפואי, מוניטור ויישור RTL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&family=Share+Tech+Mono&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; background-color: #f4f7f9; }
    
    /* יישור כותרות לאמצע */
    h1, h2, h3 { text-align: center !important; color: #1e3d59; font-weight: 800; margin-bottom: 20px; }
    
    /* עיצוב מוניטור ICU */
    .monitor-box {
        background-color: #000;
        color: #39ff14;
        font-family: 'Share Tech Mono', monospace;
        padding: 20px;
        border: 4px solid #444;
        border-radius: 10px;
        text-align: left;
        direction: ltr;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px #000, 0 5px 15px rgba(0,0,0,0.5);
    }
    .monitor-val { font-size: 24px; margin-bottom: 5px; }
    .hr { color: #ff0000; } .bp { color: #ffff00; } .spo2 { color: #00ffff; }

    /* כרטיסיות תוכן מלא */
    .content-card {
        background-color: white;
        border-right: 10px solid #2e59a8;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        line-height: 1.8;
    }
    
    /* כפתורים */
    .stButton>button { width: 100%; border-radius: 50px; background: linear-gradient(135deg, #2e59a8 0%, #1e3d59 100%); color: white; font-weight: bold; height: 3.5em; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.2); transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.3); }

    /* RTL לסיידבר */
    [data-testid="stSidebar"] { direction: RTL !important; text-align: right !important; background-color: #ffffff; border-left: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- חיבור למסד נתונים ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Sheet1", ttl=0)
    except: return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_points(points):
    df = get_db()
    email = st.session_state.user_email
    if email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        df.at[idx, 'score'] = int(df.at[idx, 'score']) + points
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.user_score = int(df.at[idx, 'score'])

# --- ניהול כניסה ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1>🏥 PICU Master Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        u_name = st.text_input("שם מלא:")
        u_email = st.text_input("אימייל:")
        if st.button("כניסה למערכת"):
            if u_name and u_email:
                st.session_state.logged_in = True
                st.session_state.user_name = u_name
                st.session_state.user_email = u_email
                db = get_db()
                st.session_state.user_score = int(db.loc[db['email'] == u_email, 'score'].values[0]) if u_email in db['email'].values else 0
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- תוכן מלא מהסיכומים (PDF) ---
content_full = {
    "המטולוגיה: פאנציטופניה ומוצרי דם": """
    ### פאנציטופניה (Pancytopenia)
    מצב המוגדר כירידה משמעותית בכל שלוש שורות הדם: טרומבוציטופניה, נויטרופניה ואנמיה.
    
    **גורמים שכיחים ב-PICU:**
    * **לוקמיה:** פגיעה במח העצם. סימנים נלווים: אורגנומגליה (הגדלת איברים), לימפאדנופתיה וכאבי עצמות.
    * **אנמיה אפלסטית:** היפופלזיה של מח העצם. סיבות: אידיופטי, תרופות ציטוטוקסיות, קרינה או זיהומים ויראליים.
    
    ### דגשים למתן מוצרי דם:
    1. **טסיות (PLT):** התוויה מתחת ל-10,000. **אסור לתת ב-IVAC** (הלחץ הורס את הטסיות). יש להשתמש במזרק פאמפ ופילטר. מינון: 5mg/kg. חייב הקרנה.
    2. **Cryoprecipitate (קריו):** מקורו בפלסמה. מכיל פיברינוגן (פקטור I), פקטור VIII, XIII, ו-vWF. משמש למחסור בפיברינוגן או דמם חריף.
    3. **FFP (פלזמה):** נפח מנה 200 מ"ל. סוג AB הוא התורם האוניברסלי לפלסמה כי אין בו נוגדנים.
    4. **Granulocytes:** התוויה של המטואונקולוג. מתן ב-IVAC **ללא פילטר** (התאים נתקעים בפילטר).
    """,
    "שוק וספסיס: פרוטוקול טיפולי": """
    ### זיהוי ספסיס (Sepsis)
    הגדרה: חשד לזיהום יחד עם תגובה דלקתית סיסטמית (SIRS).
    **קריטריונים ל-SIRS:** חום >38 או <36 מעלות, טכיקרדיה, טכיפניאה או לויקוציטוזיס.
    
    ### ניהול הטיפול (The Golden Hour):
    1. **נוזלים:** התחלת החזר נוזלים של 10-20ml/kg תוך 5-10 דקות. ניתן להגיע עד 60ml/kg.
    2. **אמינים:** אם השוק עמיד לנוזלים, תיעדוף אדרנלין או נוראדרנלין על פני דופמין.
    3. **אנטיביוטיקה:** מתן תוך שעה מרגע החשד (למשל מרופנם 20mg/kg).
    
    ### שוק קרדיוגני (Cardiogenic Shock):
    **סימני גודש:** כבד מוגדל (Liver drop), חרחורים בריאות (קרפיטציות).
    **אזהרה:** בשוק קרדיוגני בולוס נוזלים עלול להחמיר בצקת ריאות וכשל לבבי.
    """,
    "נוירולוגיה: TBI ו-ICP": """
    ### יעדים בטיפול בחבלת ראש (TBI)
    * **CPP (Cerebral Perfusion Pressure):** מחושב כ-MAP מינוס ICP. יעד בילדים: 40-60.
    * **אינטובציה:** חובה בכל מצב של GCS < 8 לצורך הגנה על נתיב אוויר.
    
    ### טריאדת קושינג (Cushing Triad):
    סימן לעלייה קריטית ב-ICP וסכנת הרניאציה:
    1. ברדיקרדיה.
    2. ירידה בקצב הנשימה (ברדיפניאה).
    3. יתר לחץ דם סיסטולי.
    
    ### ניהול יומיומי:
    * הרמת מראש המיטה ל-30 מעלות.
    * מנח ראש ישר (Neutral) לשיפור ניקוז ורידי.
    * טיפול בבצקת: סליין היפרטוני 3% או מניטול (מתן דרך פילטר 1.2 מיקרון).
    """
}

# --- תפריט צדי ---
with st.sidebar:
    st.markdown(f"<h4>שלום, {st.session_state.user_name}</h4>", unsafe_allow_html=True)
    st.metric("XP - ניקוד למידה", st.session_state.user_score)
    st.divider()
    page = st.radio("תפריט:", ["דאשבורד", "מרכז למידה מלא", "תרחיש מתגלגל 🎢", "ספריית תרופות ABC", "חיפוש מהיר"])
    if st.button("התנתק"): st.session_state.logged_in = False; st.rerun()

# --- דף דאשבורד ---
if page == "דאשבורד":
    st.markdown("<h1>לוח בקרה מחלקתי</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🏆 טבלת שיאים")
        df = get_db().sort_values(by="score", ascending=False).head(5)
        st.table(df[["name", "score"]].rename(columns={"name": "שם", "score": "XP"}))
    with col2:
        st.markdown('<div class="content-card"><h3>💊 תרופת היום</h3><b>Adenosine</b><br>לטיפול ב-SVT. חובה להזריק ב-Flash מהיר הכי קרוב ללב. זמן מחצית חיים קצר מ-10 שניות!</div>', unsafe_allow_html=True)

# --- דף מרכז למידה ---
elif page == "מרכז למידה מלא":
    st.markdown("<h1>ספריית ידע PICU</h1>", unsafe_allow_html=True)
    sel = st.selectbox("בחר נושא לקריאה:", list(content_full.keys()))
    st.markdown(f'<div class="content-card">{content_full[sel]}</div>', unsafe_allow_html=True)

# --- תרחיש מתגלגל משופר ---
elif page == "תרחיש מתגלגל 🎢":
    st.markdown("<h1>סימולציה קלינית אינטראקטיבית</h1>", unsafe_allow_html=True)
    if 's_step' not in st.session_state: st.session_state.s_step = 0

    # שלב 1: קבלה
    if st.session_state.s_step == 0:
        st.markdown("### שלב 1: הודעה מהמיון")
        st.image("https://img.freepik.com/free-photo/sick-child-hospital-bed_23-2149122395.jpg", caption="תינוק אפטי במיטה", width=500)
        st.info("תינוק בן חודשיים עם AML, ספירת לבנים (WBC) של 810,000. הילד נראה חיוור מאוד ואפרורי.")
        
        # מוניטור
        st.markdown("""<div class="monitor-box">
            <div class="monitor-val hr">HR: 185 (Tachycardia)</div>
            <div class="monitor-val bp">BP: 72/40 (Hypotension)</div>
            <div class="monitor-val spo2">SpO2: 91% (RA)</div>
        </div>""", unsafe_allow_html=True)
        
        ans = st.radio("מה החשד המיידי שלך לאור ספירת הלבנים ומראה הילד?", ["דימום מוחי", "Leukostasis (שבץ/כשל נשימתי)", "זיהום ויראלי"])
        if st.button("בצע פעולה"):
            if "Leukostasis" in ans: st.success("נכון! צמיגות הדם גבוהה מאוד."); st.session_state.s_step = 1; st.rerun()

    # שלב 2: התדרדרות ל-TLS
    elif st.session_state.s_step == 1:
        st.markdown("### שלב 2: תוצאות מעבדה")
        st.warning("התחלת הידרציה מאסיבית. המעבדה חוזרת: Potassium 7.1, Uric Acid 16. הילד מפתח אריתמיה במוניטור.")
        
        # מוניטור משתנה
        st.markdown("""<div class="monitor-box" style="color: red;">
            <div class="monitor-val">ECG: PEAKED T-WAVES / PVCs</div>
            <div class="monitor-val hr">HR: 198</div>
        </div>""", unsafe_allow_html=True)
        
        ans = st.radio("מהי הפעולה הדחופה ביותר להגנה על שריר הלב?", ["מתן פוסיד", "קלציום גלוקונט IV", "אלופורינול"])
        if st.button("טפל"):
            if "קלציום" in ans: st.success("מצוין! קלציום מגן על ממברנת הלב מהיפרקלמיה."); st.session_state.s_step = 2; st.rerun()

    # שלב 3: שוק קרדיוגני
    elif st.session_state.s_step == 2:
        st.markdown("### שלב 3: קריסה המודינמית")
        st.error("הילד מתנשם בכבדות. בהאזנה: חרחורים דו-צדדיים. הכבד נמוש 4 ס''מ מתחת לקשת הצלעות.")
        st.image("https://media.istockphoto.com/id/1154562473/vector/medical-monitor-displaying-vital-signs.jpg?s=612x612&w=0&k=20&c=6_n-uT0v0k5N7_F1bS1k3yW0hY8v1N_f_H8b8z7kG3E=", caption="מוניטור מראה ירידה בתפקוד", width=400)
        
        ans = st.radio("מהי האבחנה הקלינית המדויקת ביותר כעת?", ["שוק ספטי (Sepsis)", "שוק קרדיוגני (Cardiogenic Shock)", "שוק היפוולמי"])
        if st.button("סיים תרחיש"):
            if "קרדיוגני" in ans:
                st.balloons(); st.success("עבודה מדהימה! זיהית את המעבר לשוק קרדיוגני. הצלת את הילד!"); update_points(50); st.session_state.s_step = 0
            else: st.error("טעות קריטית. הסימנים (כבד וחרחורים) מעידים על עומס יתר של נוזלים וכשל לבבי.")

# --- ספריית תרופות ABC ---
elif page == "ספריית תרופות ABC":
    st.markdown("<h1>🔤 ספריית תרופות PICU</h1>", unsafe_allow_html=True)
    abc = {"א": ["אדרנלין: החייאה 0.01mg/kg. אינהלציה 400mcg/kg.", "אדנוזין: 0.1mg/kg ל-SVT.", "אטרופין: 0.02mg/kg (מינימום 0.1mg)."],
           "ד": ["דופמין: 1-20mcg/kg/min.", "דקסמתזון: 0.6mg/kg."],
           "מ": ["מילרינון: 0.25-0.75mcg/kg/min (Inodilator).", "מניטול: להורדת ICP דרך פילטר 1.2."],
           "פ": ["פוסיד: 0.5-2mg/kg.", "פנטניל: 1-2mcg/kg (זהירות מ-Chest Rigidity)."]}
    letter = st.select_slider("בחר אות:", options=sorted(abc.keys()))
    for d in abc[letter]:
        st.markdown(f'<div class="content-card">{d}</div>', unsafe_allow_html=True)

# --- חיפוש מהיר ---
elif page == "חיפוש מהיר":
    st.markdown("<h1>🔍 חיפוש מהיר במאגר</h1>", unsafe_allow_html=True)
    q = st.text_input("הקלד מונח לחיפוש (למשל: אשלגן, שוק, ICP):")
    if q:
        for title, text in content_full.items():
            if q.lower() in title.lower() or q.lower() in text.lower():
                st.markdown(f'<div class="content-card"><b>{title}</b><br>{text}</div>', unsafe_allow_html=True)
