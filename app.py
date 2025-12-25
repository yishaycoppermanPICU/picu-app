import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import time

# --- 1. הגדרות דף ועיצוב אולטימטיבי (Manus Style & RTL) ---
st.set_page_config(page_title="PICU Master Pro", layout="wide", page_icon="🏥", initial_sidebar_state="expanded")

# CSS מתקדם: פונטים, כרטיסיות, מוניטור, ויישור לימין
st.markdown("""
    <style>
    /* ייבוא פונטים: Assistant לטקסט רגיל, Share Tech Mono למוניטור */
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&family=Share+Tech+Mono&display=swap');

    /* הגדרות גלובליות ו-RTL */
    html, body, [class*='css'], .stMarkdown, .stText, .stButton, .stRadio, .stSelectbox, .stTextInput, .stMetric, .stExpander, div[data-testid="stSidebar"] { 
        font-family: 'Assistant', sans-serif; 
        direction: RTL !important; 
        text-align: right !important; 
    }

    /* כותרות מרכזיות בסגנון Manus */
    h1, h2, h3 { 
        text-align: center !important; 
        font-family: 'Assistant', sans-serif;
        color: #0f172a; 
        font-weight: 800; 
        letter-spacing: -0.5px;
    }
    
    h1 { margin-bottom: 30px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }

    /* כרטיסיות מידע (Cards) */
    .clinical-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-right: 6px solid #3b82f6; /* פס כחול מימין */
        transition: transform 0.2s;
    }
    .clinical-card:hover { transform: translateY(-3px); }
    .card-title { font-weight: 800; font-size: 1.2rem; color: #1e40af; margin-bottom: 10px; }
    .card-content { font-size: 1.05rem; line-height: 1.6; color: #334155; }
    .card-warning { color: #b91c1c; font-weight: bold; background: #fef2f2; padding: 5px; border-radius: 4px; }

    /* עיצוב מוניטור ICU ריאליסטי */
    .icu-monitor-frame {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 20px;
        box-shadow: inset 0 0 20px #000, 0 10px 20px rgba(0,0,0,0.3);
        margin: 20px auto;
        border: 4px solid #333;
        max-width: 800px;
    }
    .icu-screen {
        font-family: 'Share Tech Mono', monospace;
        display: flex;
        justify-content: space-around;
        align-items: center;
        direction: ltr !important; /* מספרים משמאל לימין */
    }
    .vital-box { text-align: center; }
    .vital-label { font-size: 14px; color: #888; letter-spacing: 1px; }
    .vital-value { font-size: 56px; font-weight: bold; text-shadow: 0 0 10px currentColor; }
    .hr-color { color: #ef4444; } /* אדום */
    .bp-color { color: #f59e0b; } /* כתום */
    .spo2-color { color: #06b6d4; } /* תכלת */
    
    /* התאמות לרכיבי Streamlit */
    .stTabs [data-baseweb="tab-list"] { justify-content: flex-end; }
    .stTabs [data-baseweb="tab"] { font-family: 'Assistant'; font-weight: 600; }
    div[data-testid="stMetricValue"] { direction: ltr; } /* מספרים במדדים */
    
    /* כפתור גוגל */
    iframe[title="Sign in with Google"] { margin: 0 auto; display: block; }
    </style>
""", unsafe_allow_html=True)

# --- 2. אתחול Session State ---
if 'u_score' not in st.session_state: st.session_state.u_score = 0
if 'scenario_stage' not in st.session_state: st.session_state.scenario_stage = 0
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False

# --- 3. ניהול דאטה (Google Sheets) ---
# הערה: וודא שקובץ secrets.toml מכיל את המפתח [connections.gsheets]
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("שגיאה בחיבור ל-Google Sheets. בדוק את קובץ ה-secrets.")
    conn = None

def get_db():
    if conn is None: return pd.DataFrame(columns=["name", "email", "score", "date"])
    try:
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["name", "email", "score", "date"])

def update_xp(points):
    if conn is None: 
        st.session_state.u_score += points
        return

    df = get_db()
    email = st.user.get("email")
    if email and email in df['email'].values:
        idx = df[df['email'] == email].index[0]
        current_score = int(df.at[idx, 'score'])
        new_score = current_score + points
        df.at[idx, 'score'] = new_score
        conn.update(worksheet="Sheet1", data=df)
        st.session_state.u_score = new_score
        st.toast(f"🎉 כל הכבוד! נוספו {points} XP", icon="⭐")
    else:
        st.session_state.u_score += points

# --- 4. מסך כניסה (Login) ---
user_info = st.user
if not user_info.get("is_logged_in", False):
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style='text-align: center; background: white; padding: 50px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);'>
            <h1 style='border:none; margin-bottom:10px;'>🏥 PICU Master Pro</h1>
            <p style='font-size: 1.2rem; color: #64748b;'>מערכת אימון וסימולציה לצוות טיפול נמרץ ילדים</p>
            <hr style='margin: 30px 0;'>
            <p style='margin-bottom: 20px;'>אנא התחבר באמצעות חשבון Google הארגוני:</p>
        </div>
        """, unsafe_allow_html=True)
        # כפתור ההתחברות המובנה החדש של Streamlit
        st.login(provider="google") 
    st.stop()

# סנכרון משתמש לאחר כניסה
if st.session_state.u_score == 0 and conn is not None:
    db = get_db()
    u_email = st.user.get("email")
    if u_email in db['email'].values:
        st.session_state.u_score = int(db.loc[db['email'] == u_email, 'score'].values[0])
    else:
        # יצירת משתמש חדש
        new_row = pd.DataFrame([{"name": st.user.get("name"), "email": u_email, "score": 0, "date": str(datetime.date.today())}])
        df_new = pd.concat([db, new_row], ignore_index=True)
        conn.update(worksheet="Sheet1", data=df_new)

# --- 5. ממשק צד (Sidebar) ---
with st.sidebar:
    st.image(st.user.get("picture") if st.user.get("picture") else "https://via.placeholder.com/150", width=80)
    st.markdown(f"### שלום, {st.user.get('name', 'רופא/ה')}")
    st.markdown("---")
    
    # הצגת XP בצורה ויזואלית
    col_xp1, col_xp2 = st.columns([1, 2])
    with col_xp1: st.markdown("### ⭐")
    with col_xp2: st.metric("XP צבור", st.session_state.u_score)
    
    st.markdown("---")
    page = st.radio(
        "נווט במערכת:",
        ["📊 דאשבורד ושיאים", "📚 פרוטוקולים (UpToDate)", "💊 ספריית תרופות", "🎢 סימולציה: תרחיש חי", "⚙️ ניהול (Admin)"]
    )
    
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 יציאה מהמערכת", use_container_width=True):
        st.logout()

# --- 6. תוכן העמודים ---

# --- עמוד דאשבורד ---
if page == "📊 דאשבורד ושיאים":
    st.title("לוח בקרה מחלקתי")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏆 מובילי המחלקה")
        db = get_db()
        if not db.empty:
            leaderboard = db.sort_values(by="score", ascending=False).head(5)
            # עיצוב טבלה נקי
            st.dataframe(
                leaderboard[["name", "score"]].rename(columns={"name": "שם הצוות", "score": "ניקוד (XP)"}),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("אין עדיין נתונים להצגה.")

    with c2:
        st.markdown("### 📈 ההתקדמות שלך")
        st.progress(min(st.session_state.u_score % 1000 / 1000, 1.0), text=f"רמה נוכחית: {int(st.session_state.u_score/1000) + 1}")
        st.markdown("""
        <div class='clinical-card'>
            <div class='card-title'>הטיפ היומי</div>
            <div class='card-content'>
            זכור: בילדים, טכיקרדיה היא לרוב מנגנון הפיצוי הראשון לירידה בתפוקת הלב (CO). 
            לחץ דם יורד רק בשלבים מאוחרים (Decompensated Shock).
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- עמוד פרוטוקולים ---
elif page == "📚 פרוטוקולים (UpToDate)":
    st.title("ספריית ידע קליני PICU")
    st.markdown("מבוסס על UpToDate 2024 | יש לקרוא בקפידה")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🩸 המטולוגיה", "⚡ שוק וספסיס", "🧠 נוירולוגיה (TBI)", "🧪 אלקטרוליטים"])
    
    with tab1:
        st.markdown("""
        <div class='clinical-card'>
            <div class='card-title'>פאנציטופניה ומוצרי דם</div>
            <div class='card-content'>
            ירידה ב-3 שורות: טסיות, נויטרופילים, המוגלובין.<br><br>
            <b>1. טרומבוציטופניה (טסיות):</b><br>
            • סף למתן: מתחת ל-10,000 (או 50,000 לפני פרוצדורה/דימום פעיל).<br>
            • <span class='card-warning'>איסור מוחלט על שימוש ב-IVAC (Pump)!</span> המשאבה הורסת את הטסיות. גרביטציה בלבד.<br>
            • מינון: 5-10 מ"ל/ק"ג (או יחידה אחת לכל 10 ק"ג).<br><br>
            <b>2. FFP (פלזמה):</b><br>
            • מכיל פקטורי קרישה. תורם אוניברסלי: סוג AB.<br>
            • אחסון: שנה במינוס 20 מעלות. הפשרה לוקחת זמן!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with tab2:
        st.markdown("""
        <div class='clinical-card'>
            <div class='card-title'>זיהוי וטיפול בשוק</div>
            <div class='card-content'>
            <b>ספסיס (Sepsis):</b> זמן הוא קריטי ("Golden Hour").<br>
            • הגדרה (SIRS): חום/היפותרמיה + טכיקרדיה/ברדיקרדיה + טכיפניאה + לויקוציטוזיס/פניה.<br>
            • טיפול: בולוסים קריסטלואידים 20 מ"ל/ק"ג (עד 60 מ"ל/ק"ג תוך שעה) + אנטיביוטיקה.<br><br>
            <b>שוק קרדיוגני:</b><br>
            • סימנים: גודש ורידי צוואר, כבד מוגדל (Liver edge יורד), קרפטציות.<br>
            • <span class='card-warning'>זהירות בנוזלים!</span> מתן נוזלים יחמיר את הבצקת הריאתית. דגש על יונוטרופים (Milrinone/Adrenaline).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class='clinical-card'>
            <div class='card-title'>חבלות ראש (TBI) וניהול ICP</div>
            <div class='card-content'>
            <b>נוסחת CPP (Cerebral Perfusion Pressure):</b><br>
            $$ CPP = MAP - ICP $$<br>
            • יעדים בילדים: CPP > 40-50 mmHg (תלוי גיל).<br><br>
            <b>הגנה על נתיב אוויר:</b><br>
            • GCS מתחת ל-8 = אינטובציה מיידית (Protect the airway).<br>
            • יש להימנע מהיפר-ונטילציה אגרסיבית (מכווץ כלי דם במוח ומוריד פרפוזיה), אלא אם יש סימני הרניאציה אקוטית.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.markdown("""
        <div class='clinical-card'>
            <div class='card-title'>הפרעות אלקטרוליטריות ושיב"א</div>
            <div class='card-content'>
            <b>היפוקלמיה (אשלגן נמוך):</b><br>
            • העדפה לתיקון פומי (Per os) אם אפשרי.<br>
            • תיקון IV: קצב מקסימלי 0.5-1 mEq/kg/hr. חובה מוניטור לבבי!<br><br>
            <b>היפרקלמיה - טיפול חירום:</b><br>
            • קלציום גלוקונט (הגנה על הלב).<br>
            • אינסולין + גלוקוז: מינון אינסולין 0.1 יח'/ק"ג. מהילה לתינוקות: 50 יחידות ב-50 מ"ל סליין (1:1).
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- עמוד ספריית תרופות ---
elif page == "💊 ספריית תרופות":
    st.title("🔤 אינדקס תרופות PICU")
    
    # מאגר תרופות לדוגמה (ניתן להרחיב)
    meds_db = {
        "א": {
            "אדרנלין (Adrenaline)": {"dose": "החייאה: 0.01 mg/kg (1:10,000) | אינהלציה לסטרידור: 0.5ml/kg (Max 5ml)", "fact": "במינונים נמוכים עובד בעיקר על רצפטורי בטא (קצב), במינונים גבוהים על אלפא (כיווץ כלי דם)."},
            "אדנוזין (Adenosine)": {"dose": "SVT: מנה ראשונה 0.1 mg/kg. חובה שטיפה מהירה (Flush).", "fact": "זמן מחצית חיים של פחות מ-10 שניות. גורם לתחושת 'נפילה' לא נעימה."},
            "אטרופין (Atropine)": {"dose": "ברדיקרדיה/הרעלה: 0.02 mg/kg. מינון מינימום 0.1 מ''ג.", "fact": "משמש לייבוש הפרשות לפני אינטובציה (נדיר היום)."}
        },
        "ד": {
            "דופמין (Dopamine)": {"dose": "2-20 mcg/kg/min", "fact": "השימוש בו בילדים פוחת לטובת אדרנלין/נוראדרנלין עקב השפעה על הכליות."},
            "דקסמתזון (Dexamethasone)": {"dose": "אסטמה/סטרידור: 0.6 mg/kg (Max 16mg)", "fact": "זמן השפעה ארוך מאוד, ניתן לרוב במנה חד פעמית במיון."}
        },
        "פ": {
            "פוסיד (Furosemide)": {"dose": "בצקת/אי ספיקת לב: 0.5-2 mg/kg", "fact": "מתן מהיר מדי בווריד עלול לגרום לפגיעה בשמיעה (Ototoxicity)."},
            "פנטניל (Fentanyl)": {"dose": "שיכוך כאב/סדציה: 1-2 mcg/kg", "fact": "לא משחרר היסטמין כמו מורפיום, ולכן עדיף באסטמתיים או המודינמית לא יציבים."}
        }
    }
    
    c1, c2 = st.columns([1, 3])
    with c1:
        selected_letter = st.selectbox("בחר אות:", sorted(meds_db.keys()))
    
    with c2:
        selected_med = st.selectbox("בחר תרופה:", sorted(meds_db[selected_letter].keys()))
    
    med_info = meds_db[selected_letter][selected_med]
    
    st.markdown(f"""
    <div class='clinical-card' style='border-right-color: #10b981;'>
        <div class='card-title' style='color: #059669;'>{selected_med}</div>
        <div class='card-content'>
            <b>💉 מינונים:</b><br>{med_info['dose']}<br><br>
            <b>💡 האם ידעת?</b><br>{med_info['fact']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- עמוד סימולציה (היהלום שבכתר) ---
elif page == "🎢 סימולציה: תרחיש חי":
    st.title("חדר הלם 1: סימולציה אינטראקטיבית")
    
    # פונקציית עזר להצגת המוניטור
    def render_monitor(hr, bp, spo2):
        st.markdown(f"""
        <div class="icu-monitor-frame">
            <div class="icu-screen">
                <div class="vital-box">
                    <div class="vital-label">HR (bpm)</div>
                    <div class="vital-value hr-color">{hr}</div>
                </div>
                <div class="vital-box">
                    <div class="vital-label">NIBP (mmHg)</div>
                    <div class="vital-value bp-color">{bp}</div>
                </div>
                <div class="vital-box">
                    <div class="vital-label">SpO2 (%)</div>
                    <div class="vital-value spo2-color">{spo2}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # State Machine לתרחיש
    stage = st.session_state.scenario_stage
    
    # שלב 0: הצגת המקרה
    if stage == 0:
        st.markdown("""
        <div class='clinical-card' style='border-right-color: #6366f1;'>
            <div class='card-title'>📜 סיפור מקרה: קבלה דחופה</div>
            <div class='card-content'>
            תינוק בן חודשיים, אבחנה חדשה של <b>AML (לוקמיה)</b>.<br>
            בספירת דם: <b>WBC = 810,000</b> (היפר-לויקוציטוזיס קיצוני).<br>
            בקבלתו: התינוק נראה <b>חיוור, אפרורי, ואפטי</b>. נשימות שטחיות.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        render_monitor("196", "68/40", "89")
        
        st.warning("⚠️ התרעה קלינית: שינוי במצב ההכרה וצבע העור!")
        
        st.markdown("### מה הפעולה המיידית הנדרשת?")
        c1, c2, c3 = st.columns(3)
        if c1.button("מתן בולוס נוזלים 20cc/kg", use_container_width=True):
            st.error("טעות! בעומס תאי כזה, נוזלים עלולים להחמיר בצקת מוחית ולרסק את ההמוגלובין.")
        
        if c2.button("אינטובציה מיידית (RSI)", use_container_width=True):
            st.info("נתיב אוויר חשוב, אבל יש בעיה פיזיולוגית דחופה יותר לפתרון לפני כן.")

        if c3.button("חשד ל-Leukostasis וטיפול ב-Exchange", use_container_width=True):
            st.session_state.scenario_stage = 1
            update_xp(50)
            st.rerun()

    # שלב 1: הצלחה ראשונית והתדרדרות נוספת
    elif stage == 1:
        st.success("✅ החלטה מצוינת! צמיגות הדם (Hyperviscosity) גורמת לתסחיפים ולחוסר חמצון.")
        st.markdown("""
        <div class='clinical-card'>
            <div class='card-content'>
            התחלתם הערכות ל-Exchange Transfusion.<br>
            לפתע, הילד מפתח נשימות אגונליות והדופק יורד במהירות.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        render_monitor("55", "40/20", "70") # ברדיקרדיה קשה
        
        st.error("🚨 CODE BLUE: הילד נכנס לדום לב.")
        
        act = st.radio("מה המינון הנכון לאדרנלין (IV)?", ["0.1 mg/kg", "0.01 mg/kg (1:10,000)", "1 mg קבוע"], horizontal=True)
        
        if st.button("בצע החייאה"):
            if act == "0.01 mg/kg (1:10,000)":
                st.session_state.scenario_stage = 2
                update_xp(100)
                st.balloons()
                st.rerun()
            else:
                st.error("מינון שגוי! מינון החייאה בילדים הוא 0.01 מ''ג לק''ג.")

    # שלב 2: סיום
    elif stage == 2:
        render_monitor("130", "85/50", "94")
        st.markdown("""
        <div class='clinical-card' style='border-right-color: #10b981;'>
            <div class='card-title'>🎉 כל הכבוד! ROSC הושג.</div>
            <div class='card-content'>
            הדופק חזר. הילד מיוצב ומועבר להמשך טיפול.<br>
            סיימת את התרחיש בהצלחה וצברת נקודות XP.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("התחל סימולציה מחדש"):
            st.session_state.scenario_stage = 0
            st.rerun()

# --- עמוד ניהול (Admin) ---
elif page == "⚙️ ניהול (Admin)":
    st.title("פאנל ניהול מערכת")
    
    pwd = st.text_input("הכנס סיסמת מנהל:", type="password")
    if pwd == "picu1234":  # סיסמה זמנית
        st.session_state.admin_mode = True
    
    if st.session_state.admin_mode:
        st.success("מחובר כמנהל")
        st.markdown("### 👥 משתמשים רשומים")
        df = get_db()
        st.data_editor(df, use_container_width=True)
        
        st.markdown("### 📤 העלאת תוכן חדש")
        uploaded_file = st.file_uploader("העלה קובץ Word עם שאלות חדשות", type=['docx'])
        if uploaded_file:
            st.info("הפיצ'ר בפיתוח - הקובץ נקלט במערכת.")
