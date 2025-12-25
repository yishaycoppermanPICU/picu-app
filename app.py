import streamlit as st

# --- 1. הגדרת העמוד (חייבת להיות הפקודה הראשונה ב-Streamlit) ---
st.set_page_config(page_title="PICU Master Pro", layout="wide")

# --- 2. מסך התחברות (Login Block) ---
# הבדיקה הזו מוודאה אם המשתמש מחובר. אם לא - מציגים מסך כניסה ועוצרים.
if not st.experimental_user.is_logged_in:
    
    # עיצוב הכותרת (כפי שראיתי בצילום המסך שלך)
    st.markdown("""
    <div style='direction: rtl; text-align: center; padding: 20px;'>
        <h1>PICU Master Pro 🏥</h1>
        <h3>מערכת אימון וסימולציה לצוות טיפול נמרץ ילדים</h3>
        <br>
        <p>אנא התחבר באמצעות חשבון Google:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # כפתור ההתחברות של גוגל
    # הפקודה הזו תשלח את המשתמש לגוגל ותחזיר אותו אוטומטית
    st.login(provider="google")
    
    # הפקודה הזו קריטית! היא עוצרת את טעינת שאר האפליקציה עד שהמשתמש מתחבר
    st.stop()


# --- 3. האפליקציה עצמה (רץ רק אחרי שהמשתמש התחבר בהצלחה) ---

# תפריט צד - כפתור יציאה + פרטי משתמש
with st.sidebar:
    st.write(f"מחובר כ: **{st.experimental_user.name}**")
    st.write(f"מייל: {st.experimental_user.email}")
    if st.button("התנתק / Log out"):
        st.logout()

# =========================================================
#       מכאן והלאה - תדביק את הקוד המקורי של האפליקציה שלך
# =========================================================

st.title("ברוך הבא למערכת PICU Master Pro")
st.success("ההתחברות עברה בהצלחה!")

# דוגמה (תמחק את זה ותשים את הקוד שלך):
# st.write("כאן יופיעו הסימולציות...")
