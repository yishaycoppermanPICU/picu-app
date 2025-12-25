import streamlit as st
import random
import time
import html
from datetime import datetime
from streamlit.components.v1 import html as st_html
import json
import io
import csv
import os
import requests
import secrets as _secrets  # for secure random state

# Local modules
from signup_store import init_db, add_user, list_users, add_or_update_google_user

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
except Exception:
    pass

# Initialize DB
init_db()

# Helper: read Google credentials from st.secrets or env
def get_google_creds():
    """
    Returns tuple (client_id, client_secret, redirect_uri)
    Prefers structured st.secrets['google'] then flat secrets then environment variables.
    """
    client_id = None
    client_secret = None
    redirect_uri = None

    try:
        # structured
        if isinstance(st.secrets, dict) and 'google' in st.secrets:
            google = st.secrets.get('google', {})
            client_id = client_id or google.get('client_id')
            client_secret = client_secret or google.get('client_secret')
            redirect_uri = redirect_uri or google.get('redirect_uri')
    except Exception:
        # st.secrets may raise if not present, ignore
        pass

    # flat secrets fallback from st.secrets
    try:
        client_id = client_id or (st.secrets.get('GOOGLE_CLIENT_ID') if hasattr(st, 'secrets') else None)
        client_secret = client_secret or (st.secrets.get('GOOGLE_CLIENT_SECRET') if hasattr(st, 'secrets') else None)
        redirect_uri = redirect_uri or (st.secrets.get('GOOGLE_REDIRECT_URI') if hasattr(st, 'secrets') else None)
    except Exception:
        pass

    # environment fallback
    client_id = client_id or os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = client_secret or os.environ.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = redirect_uri or os.environ.get('GOOGLE_REDIRECT_URI')

    return client_id, client_secret, redirect_uri

# Build Google OAuth2 authorization URL (Authorization Code flow)
def build_auth_url(client_id, redirect_uri, state=None):
    scope = "openid email profile"
    base = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    if state:
        params['state'] = state
    # build query safely
    qs = '&'.join([f"{k}={requests.utils.quote(str(v), safe='')" for k, v in params.items()])
    return f"{base}?{qs}"

# Verify id_token using Google's tokeninfo endpoint
def verify_id_token(id_token, expected_aud=None):
    """
    Verifies an ID token by calling Google's tokeninfo endpoint.
    Returns token info dict on success, otherwise None.
    """
    try:
        resp = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={requests.utils.quote(id_token)}', timeout=10)
        if resp.status_code != 200:
            return None
        info = resp.json()
        # optional: check audience
        if expected_aud and info.get('aud') != expected_aud:
            return None
        # basic required fields
        if not info.get('email'):
            return None
        return info
    except Exception:
        return None

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

# Google credentials check
client_id, client_secret, redirect_uri = get_google_creds()

if not client_id:
    st.sidebar.warning('Google client_id לא מוגדר. כדי להפעיל Google Sign-In, הוסף GOOGLE_CLIENT_ID ל-st.secrets או environment variables.')

if not client_secret:
    st.sidebar.info('Google client_secret לא מוגדר. כדי להשלים Authorization Code flow השרת חייב client_secret (אל תשמור אותו בקוד). ניתן להוסיף GOOGLE_CLIENT_SECRET ל-st.secrets או environment variables.')

if not redirect_uri:
    st.sidebar.info('Google redirect URI לא מוגדר. הוסף GOOGLE_REDIRECT_URI ל-st.secrets או environment variables.')

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
        writer.writerow(['id','name','email','created_at','uid','provider','photo_url','last_login'])
        for u in users:
            writer.writerow(u)
        st.download_button('הורד CSV', data=output.getvalue(), file_name='users.csv', mime='text/csv')

# Build or display Google Sign-In link/button
with st.sidebar:
    st.markdown('---')
    st.subheader('Google Sign-In')
    if client_id and redirect_uri:
        # generate state for CSRF protection
        if 'oauth_state' not in st.session_state:
            st.session_state['oauth_state'] = _secrets.token_urlsafe(16)
        auth_url = build_auth_url(client_id, redirect_uri, state=st.session_state['oauth_state'])
        # show link - open in same tab using styled anchor
        st.markdown(f"<a class='google-btn' href='{auth_url}' target='_self'>התחבר עם Google</a>", unsafe_allow_html=True)
        st.caption('הקישור יפתח חלון חדש ויחזיר אותך חזרה ליישום לאחר התחברות.')
    else:
        st.info('לא ניתן לבנות לינק התחברות - הוסף את GOOGLE_CLIENT_ID ו-GOOGLE_REDIRECT_URI ל-st.secrets או ל-env')

# Detect if redirected back with code (and optional state)
query_params = st.experimental_get_query_params()

# Process OAuth2 callback only if we have a code and credentials
if 'code' in query_params:
    # We only proceed if we have client_id and client_secret and redirect_uri
    if not (client_id and client_secret and redirect_uri):
        st.error('חסרים פרטי Google OAuth (client_id / client_secret /redirect_uri). בדוק את ההגדרות.')
        # clear query params to avoid loops
        st.experimental_set_query_params()
    else:
        code = query_params.get('code')[0]
        returned_state = query_params.get('state', [None])[0]
        # verify state
        expected_state = st.session_state.get('oauth_state')
        if not expected_state:
            st.error('Missing expected OAuth state (session expired?). הבקשה נדחתה.')
            st.experimental_set_query_params()
        elif returned_state != expected_state:
            st.error('Mismatch in OAuth state parameter. הבקשה נדחתה (state לא תואם).')
            # clear params to avoid loops
            st.experimental_set_query_params()
        else:
            # exchange code for tokens (server-side)
            token_url = 'https://oauth2.googleapis.com/token'
            data = {
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            try:
                r = requests.post(token_url, data=data, timeout=10)
                if r.status_code == 200:
                    tok = r.json()
                    id_token = tok.get('id_token')
                    access_token = tok.get('access_token')
                    info = None
                    if id_token:
                        info = verify_id_token(id_token, expected_aud=client_id)
                    # fallback: if no id_token or verification failed, try userinfo endpoint with access token
                    if not info and access_token:
                        try:
                            resp = requests.get('https://www.googleapis.com/oauth2/v3/userinfo',
                                                headers={'Authorization': f'Bearer {access_token}'},
                                                timeout=10)
                            if resp.status_code == 200:
                                info = resp.json()
                        except Exception:
                            info = None
                    if info:
                        # store user in DB
                        uid = info.get('sub') or info.get('id') or ''
                        name = info.get('name') or ''
                        email = info.get('email') or ''
                        picture = info.get('picture') or ''
                        ok = add_or_update_google_user(uid, name, email, picture)
                        if ok:
                            st.success(f'מחובר כ {email}')
                            st.session_state['email'] = email
                            st.session_state['user_info'] = info
                            # rotate oauth_state to avoid reuse
                            st.session_state['oauth_state'] = _secrets.token_urlsafe(16)
                        else:
                            st.error('שגיאה בשמירת המשתמש במסד הנתונים.')
                    else:
                        # fixed: use double quotes so internal apostrophe doesn't break the string
                        st.error("אימות ה'id_token נכשל או לא התקבל מידע משתמש תקין.")
                else:
                    # show helpful error (do not leak client_secret)
                    try:
                        err = r.json()
                    except Exception:
                        err = r.text
                    st.error(f'קבלת tokens נכשלה: {err}')
            except Exception as e:
                st.error(f'שגיאה בתקשורת עם Google: {e}')
            finally:
                # clear query params so code isn't re-used and to clean the URL
                st.experimental_set_query_params()

# Logout
if st.sidebar.button('התנתק'):
    st.session_state.pop('email', None)
    st.session_state.pop('user_info', None)
    st.session_state.pop('oauth_state', None)
    st.success('התנתקת')

# ==================================================================================================
# חלק 4: תוכן ראשי - כותרת, תיאור, ושילוב כרטיסים
# ==================================================================================================

st.title('PICU Pro Master')
st.markdown(render_clean_html('''
## ברוכים הבאים למערכת הלמידה והסימולציה
מטרת המערכת היא לספק מבחנים קליניים, חומר לימודי ושיעורי מעבדה לקבוצת ה-PICU.
**המערכת שופצה:** איסוף משתמשים, שיפור עיצוב ותשתית לשאלות.
'''), unsafe_allow_html=True)

if 'user_info' in st.session_state:
    info = st.session_state['user_info']
    email = info.get('email', '')
    picture = info.get('picture', '')
    st.markdown(f"<div class='card'><strong>מחובר:</strong> {email}<br><img src=\"{picture}\" style='width:64px;border-radius:8px;margin-top:8px;'></div>", unsafe_allow_html=True)

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
                st.markdown(f"**שאלה {i}:** {q.get('stem')}\\n")
                if q.get('type') == 'mcq':
                    opts = q.get('options', [])
                    choice = st.radio(f"בחר תשובה לשאלה {i}", opts, key=f'q_{i}')
                    if st.button(f'בדוק שאלה {i}', key=f'check_{i}'):
                        if opts.index(choice) == q.get('answer'):
                            st.success('תשובה נכונה ✅')
                            score += 1
                        else:
                            st.error('תשובה שגויה ❌')
                            st.info(f"פתרון: {opts[q.get('answer')]}\\n\\nהסבר: {q.get('explanation','לא זמין')}")
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
        <p>כניסה באמצעות Gmail (מומלץ להגדיר secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(render_clean_html('''
    ### שדרוגים מוצעים
    * אימות אימייל
    * Google Sign-In (OAuth) מחובר ל-DB
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
