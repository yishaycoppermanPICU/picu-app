import streamlit as st
import random
import time
import html
from datetime import datetime
from streamlit.components.v1 import html as st_html
import json
import io
import csv

# Local modules
from signup_store import init_db, add_user, list_users

# ==================================================================================================
# חלק 1: הגדרות מערכת ועיצוב (System & CSS)
# ==================================================================================================

st.set_page_config(
    page_title="PICU Pro Master - מערכת למידה וסימולציה",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
try:
    with open('assets/custom.css', 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    # If CSS not found, ignore
    pass

# Initialize DB
init_db()

# --- מנוע רינדור HTML חכם (מונע שבירת שורות) ---
def render_clean_html(text, sanitize=False):
    if not text: return ""
    if sanitize:
        text = html.escape(text)
    html_text = text.replace("\n", "<br>")
    lines = html_text.split("<br>")
    formatted = []
    in_list = False
    
    for line in lines:
        cl = line.strip()
        if not cl: continue
        
        # כותרות
        if cl.startswith("###"):
            if in_list: formatted.append("</ul>"); in_list = False
            cl = f"<h3 style='color:#01579b; border-bottom:2px solid #b3e5fc; margin-top:20px; font-weight:700;'>{cl.replace('###','')}</h3>"
        elif cl.startswith("##"):
            if in_list: formatted.append("</ul>"); in_list = False
            cl = f"<div style='background:linear-gradient(90deg, #e3f2fd 0%, #fff 100%); padding:12px; border-right:5px solid #1565c0; border-radius:6px; margin-top:30px;'><h2 style='color:#0d47a1; margin:0; font-size:1.5rem; font-weight:800;'>{cl.replace('##','')}</h2></div>"
        
        # טקסט מודגש (כותרות פנימיות)
        elif "**" in cl and cl.startswith("**") and (":" in cl or len(cl.split("**")[1]) < 20):
            parts = cl.split("**")
            if len(parts) >= 3:
                cl = f"<div style='margin:10px 0; background:#fafafa; padding:8px; border-radius:4px; border-right:3px solid #ef5350;'><span style='color:#c62828; font-weight:800; display:block;'>📌 {parts[1]}</span><span style='color:#37474f;'>{''.join(parts[2:])}</span></div>"
        
        # רשימות
        elif cl.startswith("* ") or cl.startswith("- "):
            if not in_list: formatted.append("<ul style='margin-right:20px; list-style-type:disc;'>"); in_list = True
            content = cl[2:]
            if "**" in content: 
                parts = content.split("**")
                new_c = ""
                for i, p in enumerate(parts):
                    if i%2==1: new_c += f"<span style='font-weight:700; background-color:#fff9c4; padding:0 4px; border-radius:3px;'>{p}</span>"
                    else: new_c += p
                content = new_c
            formatted.append(f"<li style='margin-bottom:8px; color:#263238;'>{content}</li>")
            continue
        else:
            # normal paragraph
            cl = f"<p style='color:#37474f; line-height:1.45; margin:6px 0;'>{cl}</p>"
        
        formatted.append(cl)
    if in_list: formatted.append("</ul>")
    return '\n'.join(formatted)

# ==================================================================================================
# חלק 2: פונקציות למבחנים ושאלות
# ==================================================================================================

QUESTIONS_PATH = 'data/questions.json'

def load_questions(path=QUESTIONS_PATH):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except Exception:
        return []

questions = load_questions()

def generate_quiz(n=10, difficulty=None):
    qs = questions.copy()
    if difficulty:
        qs = [q for q in qs if q.get('difficulty') == difficulty]
    if not qs:
        return []
    return random.sample(qs, k=min(n, len(qs)))

# ==================================================================================================
# חלק 3: Sidebar - הרשמה משתמשים / כניסה ו-admin
# ==================================================================================================

st.sidebar.title("משתמש")
if 'email' not in st.session_state:
    st.session_state['email'] = ''

with st.sidebar.form(key='signup_form'):
    st.subheader('הרשמה מהירה')
    name = st.text_input('שם מלא')
    email = st.text_input('אימייל', value=st.session_state.get('email',''))
    remember = st.checkbox('זכור אותי במחשב זה', value=bool(st.session_state.get('email','')))
    submitted = st.form_submit_button('הרשם')
    if submitted:
        if not email:
            st.sidebar.error('אנא הזן כתובת אימייל.')
        else:
            ok = add_user(name, email)
            if ok:
                st.sidebar.success('נרשמת בהצלחה ✅')
                if remember:
                    st.session_state['email'] = email
            else:
                st.sidebar.error('כנראה שהאימייל כבר קיים או שגיאה')

st.sidebar.markdown('---')
if st.sidebar.checkbox('הצג כלי ניהול (Admin)', value=False):
    st.sidebar.header('ניהול משתמשים')
    users = list_users()
    st.sidebar.write(f"סך הכול משתמשים: {len(users)}")
    if st.sidebar.button('הורד CSV של משתמשים'):
        # build CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id','name','email','created_at'])
        for u in users:
            writer.writerow(u)
        st.download_button('הורד CSV', data=output.getvalue(), file_name='users.csv', mime='text/csv')

# ==================================================================================================
# חלק 4: תוכן ראשי - כותרת, תיאור, ושילוב כרטיסים
# ==================================================================================================

st.title('PICU Pro Master')
st.markdown(render_clean_html('''
## ברוכים הבאים למערכת הלמידה והסימולציה
מטרת המערכת היא לספק מבחנים קליניים, חומר לימודי ושיעורי מעבדה לקבוצת ה-PICU.
**המערכת שופצה:** איסוף משתמשים, שיפור עיצוב ותשתית לשאלות.
'''), unsafe_allow_html=True)

# Two column layout
col1, col2 = st.columns([2,1])

with col1:
    st.markdown("""
    <div class='card'>
        <h2>תכנים מומלצים</h2>
        <p>העלה טקסט לימודי, הוסף שאלות, והרץ מבחנים לפי נושאים.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='card'>
        <h3>מבחן מהיר</h3>
    </div>
    """, unsafe_allow_html=True)

    q_count = st.slider('כמות שאלות במבחן', 1, 20, 10)
    difficulty = st.selectbox('רמת קושי (אופציונלי)', options=['','easy','medium','hard'])
    if st.button('צור מבחן אקראי'):
        quiz = generate_quiz(n=q_count, difficulty=difficulty if difficulty else None)
        if not quiz:
            st.warning('אין מספיק שאלות במאגר. אנא הוסף שאלות בקובץ data/questions.json')
        else:
            score = 0
            for i, q in enumerate(quiz, start=1):
                st.markdown(f"**שאלה {i}:** {q.get('stem')}\n")
                if q.get('type') == 'mcq':
                    opts = q.get('options', [])
                    choice = st.radio(f"בחר תשובה לשאלה {i}", opts, key=f'q_{i}')
                    if st.button(f'בדוק שאלה {i}', key=f'check_{i}'):
                        if opts.index(choice) == q.get('answer'):
                            st.success('תשובה נכונה ✅')
                            score += 1
                        else:
                            st.error('תשובה שגויה ❌')
                            st.info(f"פתרון: {opts[q.get('answer')]}\n\nהסבר: {q.get('explanation','לא זמין')}")
                else:
                    ans = st.text_input(f"תשובתך לשאלה {i}", key=f'free_{i}')
                    if st.button(f'בדוק שאלה {i}', key=f'check_free_{i}'):
                        if ans.strip().lower() == q.get('answer_text','').strip().lower():
                            st.success('תשובה נכונה ✅')
                            score += 1
                        else:
                            st.error('תשובה שגויה ❌')
            st.balloons()
            st.success(f'ניקוד סופי: {score}/{len(quiz)}')

with col2:
    st.markdown("""
    <div class='card'>
        <h3>כניסה מהירה</h3>
        <p>כניסה באמצעות Gmail (מומלץ להגדיר Firebase/Auth) או הרשמה מקומית.</p>
        <div id='google-signin'></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(render_clean_html('''
    ### שדרוגים מוצעים
    * אימות אימייל
    * Google Sign-In (Firebase)
    * ייצוא/יבוא שאלות
    '''), unsafe_allow_html=True)

# ==================================================================================================
# חלק 5: ממשק לטעינת שאלות חדש (Admin)
# ==================================================================================================

st.markdown('---')
st.header('כלי שאלות (Admin)')
if st.checkbox('הצג כלי שאלות מתקדמים'):
    st.markdown('ניתן להעלות קובץ JSON עם שאלות במבנה המתואר במסמך README.')
    uploaded = st.file_uploader('בחר קובץ JSON של שאלות', type=['json'])
    if uploaded is not None:
        try:
            content = json.load(uploaded)
            # basic validation
            if isinstance(content.get('questions', None), list):
                # overwrite local file
                with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                st.success('השאלות עודכנו בהצלחה')
            else:
                st.error('הקובץ אינו תקין - צריך לכלול root.questions כמערך')
        except Exception as e:
            st.error(f'שגיאה בקריאת הקובץ: {e}')

st.markdown('\n\n---\n\n')
st.info('לסקירה: אם תרצה, אני יכול להמשיך ולחבר Firebase Sign-In ולעשות עיצוב נוסף.')

# Footer
st.markdown("<div style='margin-top:30px; color:#546e7a;'>נוצר על ידי צוות PICU Pro — שיפורים אוטומטיים: איסוף אימיילים, UI משופר, כלי ניהול ושאלות.</div>", unsafe_allow_html=True)
