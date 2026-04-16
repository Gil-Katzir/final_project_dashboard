import streamlit as st
import pandas as pd
import plotly.express as px
import time
import uuid
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from supabase import create_client, Client

# -----------------------------
# Page config - must be first Streamlit command
# -----------------------------
st.set_page_config(
    page_title="ניסוי ניתוח נתונים",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Supabase connection
# -----------------------------
supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# -----------------------------
# Helpers / constants
# -----------------------------
TEST_PARTICIPANT_ID = "9999"


def is_test_mode() -> bool:
    return str(st.session_state.get("participant_id", "")).strip() == TEST_PARTICIPANT_ID


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
<style>
    html, body, [class*="css"], input, textarea, select, button, label, p, div, span {
        font-family: Arial, 'Arial', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(96,165,250,0.16), transparent 24%),
            radial-gradient(circle at top left, rgba(14,165,233,0.10), transparent 20%),
            linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%);
    }

    .block-container {
        max-width: 1360px;
        padding: 1.2rem 2.2rem 2rem 2.2rem;
    }

    .big-title {
        font-size: 3.05rem;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 0.45rem;
        letter-spacing: -0.04em;
        background: linear-gradient(90deg, #0f172a, #2563eb 55%, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        direction: rtl;
        text-align: right;
    }

    .sub-title {
        font-size: 1.06rem;
        color: #64748b;
        margin-bottom: 1.8rem;
        direction: rtl;
        text-align: right;
    }

    .hero-card,
    .form-card,
    .thankyou-card,
    .summary-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(226,232,240,0.95);
        border-radius: 30px;
        box-shadow: 0 20px 50px -20px rgba(15,23,42,0.18);
        backdrop-filter: blur(10px);
    }

    .hero-card {
        padding: 42px 48px;
        max-width: 640px;
        margin: 1rem auto 0 auto;
        direction: rtl;
        text-align: right;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        text-align: right;
        margin-bottom: 0.35rem;
        color: #0f172a;
    }

    .hero-subtitle {
        font-size: 0.98rem;
        color: #64748b;
        text-align: right;
        margin-bottom: 1.2rem;
    }

    .section-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 14px;
        background: linear-gradient(135deg, #dbeafe, #eff6ff);
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .hero-section-title {
        font-size: 1.03rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.25rem 0 0.45rem 0;
        padding-right: 12px;
        border-right: 4px solid #3b82f6;
    }

    .hero-text {
        font-size: 0.97rem;
        color: #475569;
        line-height: 1.9;
    }

    .hero-highlight {
        background: linear-gradient(135deg, #eff6ff, #f8fbff);
        border: 1px solid #dbeafe;
        border-right: 4px solid #3b82f6;
        border-radius: 18px;
        padding: 16px 18px;
        color: #1e3a8a;
        font-size: 0.94rem;
        margin: 1.15rem 0;
        line-height: 1.8;
    }

    .form-card {
        max-width: 560px;
        margin: 2rem auto;
        padding: 34px 36px;
        direction: rtl;
        text-align: right;
    }

    .form-title {
        font-size: 1.32rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.35rem;
    }

    .form-subtitle {
        font-size: 0.96rem;
        color: #64748b;
        margin-bottom: 1.4rem;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.96));
        border: 1px solid rgba(226,232,240,0.95);
        border-radius: 24px;
        padding: 18px 20px;
        box-shadow: 0 14px 30px -18px rgba(15,23,42,0.25);
        min-height: 102px;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.73rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 9px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 1.52rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .metric-sub {
        color: #94a3b8;
        font-size: 0.84rem;
        margin-top: 7px;
    }

    .section-title {
        font-size: 1.48rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.85rem 0 1rem 0;
        padding-right: 14px;
        border-right: 5px solid #2563eb;
        direction: rtl;
        text-align: right;
    }

    .chart-card {
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(226,232,240,0.95);
        border-radius: 28px;
        padding: 22px;
        box-shadow: 0 20px 40px -25px rgba(15,23,42,0.22);
        min-height: 480px;
        animation: fadeIn 0.45s ease;
    }

    .chart-card-empty {
        background: rgba(255,255,255,0.22);
        border: 1px dashed rgba(148,163,184,0.30);
        border-radius: 28px;
        min-height: 480px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chart-title {
        font-size: 1.42rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.8rem;
        direction: rtl;
        text-align: right;
        font-family: Arial, sans-serif !important;
        letter-spacing: 0;
    }

    .story-box {
        background: linear-gradient(135deg, #eff6ff, #f8fbff);
        border: 1px solid #dbeafe;
        border-right: 4px solid #2563eb;
        border-radius: 18px;
        padding: 13px 16px;
        color: #1e3a8a;
        font-size: 0.96rem;
        line-height: 1.7;
        margin-bottom: 1rem;
        direction: rtl;
        text-align: right;
    }

    .new-chart-badge {
        display: inline-flex;
        justify-content: flex-end;
        text-align: right;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #0ea5e9, #2563eb);
        color: white;
        font-size: 0.86rem;
        font-weight: 700;
        padding: 8px 15px;
        border-radius: 999px;
        margin-bottom: 1rem;
        box-shadow: 0 12px 24px -14px rgba(37,99,235,0.95);
        direction: rtl;
        text-align: right;
    }

    .dashboard-note {
        background: linear-gradient(135deg, #fff7ed, #fffbeb);
        color: #9a3412;
        border: 1px solid #fed7aa;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 0.92rem;
        margin-top: 1rem;
        display: inline-block;
        direction: rtl;
        text-align: right;
        line-height: 1.7;
    }

    .question-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(226,232,240,0.95);
        border-radius: 28px;
        padding: 28px 30px;
        box-shadow: 0 18px 35px -24px rgba(15,23,42,0.24);
        direction: rtl;
        text-align: right;
    }

    .question-kicker {
        color: #2563eb;
        font-size: 0.86rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        margin-bottom: 0.45rem;
    }

    .question-title {
        font-size: 1.26rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.9rem;
        line-height: 1.55;
    }

    .question-label {
        font-size: 0.98rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.4rem;
    }

    .thankyou-card,
    .summary-card {
        max-width: 640px;
        margin: 2rem auto;
        padding: 38px 42px;
        direction: rtl;
        text-align: right;
    }

    .thankyou-title,
    .summary-title {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.7rem;
        text-align: center;
    }

    .thankyou-sub,
    .summary-sub {
        font-size: 1rem;
        color: #64748b;
        line-height: 1.8;
        text-align: center;
        margin-bottom: 1.3rem;
    }

    .thankyou-emoji,
    .summary-emoji {
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 0.8rem;
    }

    .rtl-title, .rtl-question, .rtl-label {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stRadio"] {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stRadio"] > div {
        direction: rtl;
        align-items: flex-end;
        gap: 8px;
    }

    div[data-testid="stRadio"] label {
        background: linear-gradient(180deg, #ffffff, #f8fafc);
        border: 1.5px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 16px !important;
        transition: all 0.18s ease;
        cursor: pointer;
        direction: rtl;
        text-align: right;
        justify-content: flex-end;
        flex-direction: row-reverse;
        margin-bottom: 6px;
    }

    div[data-testid="stRadio"] label:hover {
        border-color: #60a5fa;
        background: #eff6ff;
        transform: translateY(-1px);
    }

    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] p {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 14px !important;
    }

    div.stButton > button {
        border-radius: 16px;
        font-weight: 700;
        padding: 0.72rem 1.4rem;
        background: linear-gradient(135deg, #2563eb, #0ea5e9);
        color: white;
        border: none;
        box-shadow: 0 16px 30px -18px rgba(37,99,235,0.7);
        transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 20px 35px -18px rgba(37,99,235,0.75);
        opacity: 0.96;
    }

    .secondary-button-note {
        color: #64748b;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 0.8rem;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label {
        direction: rtl !important;
        text-align: right !important;
        width: 100%;
        justify-content: flex-end;
        font-weight: 700;
        color: #334155;
    }

    div[data-testid="stTextInput"] input {
        text-align: right;
    }

    div[data-testid="stSelectbox"] {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
        text-align: right !important;
    }

    .narrow-button {
        max-width: 260px;
        margin: 0 auto;
    }

    .narrow-button-wide {
        max-width: 320px;
        margin: 0 auto;
    }

    .compact-center {
        max-width: 560px;
        margin: 0 auto;
    }

</style>
""",
    unsafe_allow_html=True
)

# -----------------------------
# Data
# -----------------------------
df = pd.read_csv("data.csv")
df["Date"] = pd.to_datetime(df["Date"])
months_order = list(df["Month"].drop_duplicates())

monthly_total = (
    df.groupby("Month", as_index=False)
    .agg(**{
        "Revenue Total": ("Revenue", "sum"),
        "Profit Total": ("Profit", "sum")
    })
)
monthly_total["Month"] = pd.Categorical(monthly_total["Month"], categories=months_order, ordered=True)
monthly_total = monthly_total.sort_values("Month")

monthly_category = (
    df.groupby(["Month", "Category"], as_index=False)
    .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
)
monthly_category["Month"] = pd.Categorical(monthly_category["Month"], categories=months_order, ordered=True)
monthly_category = monthly_category.sort_values(["Month", "Category"])

monthly_dress = (
    df[df["Category"] == "Dress"]
    .groupby("Month", as_index=False)
    .agg(**{
        "Discount Dress": ("Discount", "mean"),
        "Profit Dress": ("Profit", "sum")
    })
)
monthly_dress["Month"] = pd.Categorical(monthly_dress["Month"], categories=months_order, ordered=True)
monthly_dress = monthly_dress.sort_values("Month")

# -----------------------------
# Questions and narratives
# -----------------------------
questions = [
    {
        "id": 1,
        "text": "מהי המגמה הכללית של ההכנסות הכוללות לאורך התקופה?",
        "options": ["ירידה", "יציבות עם עלייה קלה", "ירידה חדה", "לא ניתן לדעת"],
        "correct_answer": "יציבות עם עלייה קלה"
    },
    {
        "id": 2,
        "text": "האם בחודש האחרון נרשמה עלייה בהכנסות ביחס לחודש הקודם?",
        "options": ["כן", "לא", "אין שינוי", "לא ניתן לדעת"],
        "correct_answer": "כן"
    },
    {
        "id": 3,
        "text": "מהי המגמה הכללית של הרווח הכולל לאורך התקופה?",
        "options": ["עלייה", "יציבות", "ירידה", "לא ניתן לדעת"],
        "correct_answer": "ירידה"
    },
    {
        "id": 4,
        "text": "האם ניתן להסביר בוודאות את הירידה ברווח רק על בסיס שני הגרפים הראשונים?",
        "options": ["כן", "לא", "כן, בגלל ירידה במכירות", "כן, בגלל עלייה בעלויות"],
        "correct_answer": "לא"
    },
    {
        "id": 5,
        "text": "איזו קטגוריה מייצרת את ההכנסות הגבוהות ביותר לאורך רוב התקופה?",
        "options": ["T-shirt", "Dress", "Jeans", "כל הקטגוריות שוות"],
        "correct_answer": "Dress"
    },
    {
        "id": 6,
        "text": "האם גרף הקטגוריות יכול לסייע להסביר את הפער בין הכנסות לרווח?",
        "options": ["כן", "לא", "רק באופן חלקי", "לא ניתן לדעת"],
        "correct_answer": "רק באופן חלקי"
    },
    {
        "id": 7,
        "text": "איזו קטגוריה נראית כמועמדת מרכזית לבדיקה מעמיקה יותר?",
        "options": ["T-shirt", "Dress", "Jeans", "אי אפשר לדעת"],
        "correct_answer": "Dress"
    },
    {
        "id": 8,
        "text": "מה הקשר הנראה בין שיעור ההנחה על Dress לבין הרווח בקטגוריה זו?",
        "options": ["ככל שההנחה עולה, הרווח עולה", "ככל שההנחה עולה, הרווח יורד", "אין קשר נראה לעין", "לא ניתן לדעת"],
        "correct_answer": "ככל שההנחה עולה, הרווח יורד"
    },
    {
        "id": 9,
        "text": "מהו ההסבר הסביר ביותר לירידה ברווח הכולל?",
        "options": [
            "ירידה בהכנסות הכוללות",
            "ירידה במכירות של כל הקטגוריות",
            "גידול במכירות ב-Dress לצד הנחות גבוהות שפוגעות ברווחיות",
            "עלייה ברווח של Dress"
        ],
        "correct_answer": "גידול במכירות ב-Dress לצד הנחות גבוהות שפוגעות ברווחיות"
    },
    {
        "id": 10,
        "text": "מהי המסקנה העסקית המרכזית מהנתונים?",
        "options": [
            "יש להמשיך להגדיל הנחות בכל הקטגוריות",
            "עלייה במכירות תמיד משפרת ביצועים עסקיים",
            "הגידול במכירות אינו מתורגם בהכרח לשיפור עסקי כאשר הרווחיות נשחקת",
            "אין בעיה עסקית נראית לעין"
        ],
        "correct_answer": "הגידול במכירות אינו מתורגם בהכרח לשיפור עסקי כאשר הרווחיות נשחקת"
    },
]

chart_narratives = {
    "chart1": "אנחנו מתחילים מהתמונה הרחבה: ההכנסות הכוללות נשארות יחסית יציבות ואף מראות שיפור קל, ולכן בשלב הזה העסק נראה בריא במבט ראשון.",
    "chart2": "כעת התמונה מסתבכת: למרות שההכנסות אינן נחלשות, הרווח הכולל דווקא נשחק. הפער הזה מרמז שמשהו בתמהיל או ברווחיות דורש בדיקה עמוקה יותר.",
    "chart3": "כדי להבין מאיפה הפער מגיע, צריך לפרק את הסיפור לקטגוריות. כאן אפשר לראות איזו קטגוריה מובילה את המחזור, ואיפה כדאי להתמקד כדי להסביר את השחיקה ברווח.",
    "chart4": "אחרי שזיהינו את Dress כחשודה מרכזית, נבחן אותה מקרוב. כעת אפשר לראות כיצד ההנחות בקטגוריה הזו עשויות להסביר למה עלייה במכירות לא הופכת בהכרח לשיפור בביצועים העסקיים."
}

NEW_CHART_AT = {2: "גרף 2 נוסף", 4: "גרף 3 נוסף", 7: "גרף 4 נוסף"}

# -----------------------------
# Session state
# -----------------------------
def get_defaults():
    return {
        "screen": "participant",
        "experiment_started": False,
        "participant_id": "",
        "experiment_group": "",
        "session_id": str(uuid.uuid4()),
        "consent_given": False,
        "session_start_time": None,
        "session_end_time": None,
        "question_start_time": None,
        "current_question": 0,
        "answers": [],
        "correct_count": 0,
        "dashboard_interaction_clicks": 0,
        "interaction_log": [],
        "db_saved": False,
        "show_test_banner": False,
        "demographics": {
            "gender": "",
            "age_range": "",
            "experience_level": "",
        },
        "chart1_drilled": False,
        "chart1_month": months_order[0],
        "chart2_drilled": False,
        "chart2_month": months_order[0],
        "chart3_drilled": False,
        "chart3_category": "Dress",
        "chart4_drilled": False,
        "chart4_month": months_order[0],
    }


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


for key, value in get_defaults().items():
    if key not in st.session_state:
        st.session_state[key] = value

widget_defaults = {
    "chart1_month_select": months_order[0],
    "chart2_month_select": months_order[0],
    "chart3_category_select": "Dress",
    "chart4_month_select": months_order[0],
}
for key, value in widget_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

prev_defaults = {
    "__prev_chart1_month_select": months_order[0],
    "__prev_chart2_month_select": months_order[0],
    "__prev_chart3_category_select": "Dress",
    "__prev_chart4_month_select": months_order[0],
}
for key, value in prev_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# Helper functions
# -----------------------------
def get_total_duration() -> float:
    if not st.session_state.session_start_time:
        return 0.0
    if st.session_state.session_end_time is not None:
        return max(0.0, st.session_state.session_end_time - st.session_state.session_start_time)
    return max(0.0, time.time() - st.session_state.session_start_time)



def track_dashboard_click(action_type: str, action_value: str = ""):
    if not st.session_state.experiment_started:
        return
    if st.session_state.current_question >= len(questions):
        return
    st.session_state.dashboard_interaction_clicks += 1
    st.session_state.interaction_log.append({
        "session_id": st.session_state.session_id,
        "participant_id": st.session_state.participant_id,
        "experiment_group": st.session_state.experiment_group,
        "timestamp": round(time.time(), 3),
        "question_index_at_time": st.session_state.current_question + 1,
        "action_type": action_type,
        "action_value": action_value
    })



def track_filter_change(widget_key: str, action_type: str):
    current_val = st.session_state.get(widget_key)
    prev_key = f"__prev_{widget_key}"
    prev_val = st.session_state.get(prev_key)
    if current_val != prev_val:
        track_dashboard_click(action_type, f"{widget_key}={current_val}")
        st.session_state[prev_key] = current_val



def build_export_df(total_duration: float) -> pd.DataFrame:
    summary = {
        "participant_id": st.session_state.participant_id,
        "experiment_group": st.session_state.experiment_group,
        "session_id": st.session_state.session_id,
        "gender": st.session_state.demographics.get("gender", ""),
        "age_range": st.session_state.demographics.get("age_range", ""),
        "experience_level": st.session_state.demographics.get("experience_level", ""),
        "total_duration_seconds": round(total_duration, 2),
        "dashboard_interaction_clicks": st.session_state.dashboard_interaction_clicks,
        "correct_answers_count": st.session_state.correct_count,
        "total_questions": len(questions),
    }
    rows = []
    for answer in st.session_state.answers:
        row = {}
        row.update(summary)
        row.update(answer)
        rows.append(row)
    return pd.DataFrame(rows)



def build_interactions_df() -> pd.DataFrame:
    if not st.session_state.interaction_log:
        return pd.DataFrame(columns=[
            "session_id", "participant_id", "experiment_group",
            "timestamp", "question_index_at_time", "action_type", "action_value"
        ])
    return pd.DataFrame(st.session_state.interaction_log)



def save_session_to_db(total_duration):
    data = {
        "session_id": str(st.session_state.session_id),
        "participant_id": str(st.session_state.participant_id),
        "experiment_group": str(st.session_state.experiment_group),
        "total_duration_seconds": float(round(total_duration, 2)),
        "dashboard_interaction_clicks": int(st.session_state.dashboard_interaction_clicks),
        "correct_answers_count": int(st.session_state.correct_count),
        "total_questions": int(len(questions)),
    }

    try:
        result = (
            supabase
            .table("sessions")
            .upsert(data, on_conflict="session_id")
            .execute()
        )
        return True, result
    except Exception:
        return False, None



def save_responses_to_db():
    rows = []
    for answer in st.session_state.answers:
        rows.append({
            "session_id": str(st.session_state.session_id),
            "participant_id": str(st.session_state.participant_id),
            "experiment_group": str(st.session_state.experiment_group),
            "question_id": int(answer["question_id"]),
            "question_text": str(answer["question_text"]) if answer["question_text"] is not None else None,
            "selected_answer": str(answer["selected_answer"]) if answer["selected_answer"] is not None else None,
            "correct_answer": str(answer["correct_answer"]) if answer["correct_answer"] is not None else None,
            "is_correct": bool(answer["is_correct"]) if answer["is_correct"] is not None else None,
            "response_time_seconds": float(answer["response_time_seconds"]) if answer["response_time_seconds"] is not None else None,
        })

    if not rows:
        return True, None

    try:
        result = supabase.table("responses").insert(rows).execute()
        return True, result
    except Exception:
        return False, None



def save_demographics_to_db():
    data = {
        "session_id": str(st.session_state.session_id),
        "participant_id": str(st.session_state.participant_id),
        "experiment_group": str(st.session_state.experiment_group),
        "gender": st.session_state.demographics.get("gender") or None,
        "age_range": st.session_state.demographics.get("age_range") or None,
        "experience_level": st.session_state.demographics.get("experience_level") or None,
    }
    try:
        result = supabase.table("demographics").upsert(data, on_conflict="session_id").execute()
        return True, result
    except Exception:
        return False, None



def persist_all_results():
    total_duration = get_total_duration()
    results = {
        "session": save_session_to_db(total_duration),
        "responses": save_responses_to_db(),
        "demographics": save_demographics_to_db(),
    }
    st.session_state.db_saved = True
    return total_duration, results



def month_daily_totals(month_name: str):
    d = df[df["Month"] == month_name].groupby(["Day"], as_index=False).agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    )
    return d.sort_values("Day")



def dress_month_daily(month_name: str):
    d = df[
        (df["Month"] == month_name) & (df["Category"] == "Dress")
    ].sort_values("Day")
    return d[["Day", "Profit", "Discount"]].copy()



def category_monthly_totals(category_name):
    d = (
        df[df["Category"] == category_name]
        .groupby("Month", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    )
    d["Month"] = pd.Categorical(d["Month"], categories=months_order, ordered=True)
    return d.sort_values("Month")



def apply_common_layout(fig, title_text=""):
    fig.update_layout(
        title=dict(text=title_text or "", font=dict(size=1, color="#334155", family="Arial")),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=12, r=12, t=18, b=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.7)",
            font=dict(family="Arial", size=12)
        ),
        font=dict(family="Arial, sans-serif", size=13, color="#334155"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_xaxes(
        showgrid=False,
        showline=False,
        tickfont=dict(size=12, color="#475569", family="Arial"),
        title=None,
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(148,163,184,0.16)',
        gridwidth=1,
        tickfont=dict(size=12, color="#475569", family="Arial"),
        zeroline=False,
        rangemode="normal"
    )
    return fig

def set_padded_yaxis(fig, values, secondary_y=False, is_percent=False):
    vals = pd.Series(values).dropna()
    if vals.empty:
        return fig
    vmin = float(vals.min())
    vmax = float(vals.max())
    if vmin == vmax:
        pad = abs(vmax) * 0.08 if vmax != 0 else 1
    else:
        pad = (vmax - vmin) * 0.18
    lower = vmin - pad
    upper = vmax + pad
    if is_percent:
        lower = max(0, lower)
    fig.update_yaxes(range=[lower, upper], secondary_y=secondary_y)
    return fig



def apply_currency_axis(fig, axis="y"):
    if axis == "y":
        fig.update_yaxes(tickprefix="$", separatethousands=True)
    elif axis == "y2":
        fig.update_yaxes(tickprefix="$", separatethousands=True, secondary_y=False)
    return fig



def panel_header(title: str, narrative: str):
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    if st.session_state.experiment_group == "storytelling":
        st.markdown(f'<div class="story-box">{narrative}</div>', unsafe_allow_html=True)


# -----------------------------
# Chart renderers
# -----------------------------
def show_chart1():
    panel_header("גרף 1: מגמת הכנסות", chart_narratives["chart1"])

    if not st.session_state.chart1_drilled:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=monthly_total["Month"],
                y=monthly_total["Revenue Total"],
                mode="lines+markers",
                name="Revenue",
                line=dict(color="#2563eb", width=4, shape="spline", smoothing=0.7),
                marker=dict(size=9, color="#ffffff", line=dict(color="#2563eb", width=3)),
                fill="none",
                hovertemplate="חודש: %{x}<br>הכנסות: $%{y:,.0f}<extra></extra>"
            )
        )
        fig = apply_common_layout(fig)
        fig.update_yaxes(tickprefix="$", separatethousands=True, title_text="Revenue")
        fig = set_padded_yaxis(fig, monthly_total["Revenue Total"])
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([1, 2.2])
        with c2:
            st.selectbox(
                "בחר/י חודש לפירוט:", months_order,
                key="chart1_month_select",
                on_change=track_filter_change,
                args=("chart1_month_select", "chart1_filter_month_change")
            )
        with c1:
            st.write("")
            if st.button("Drill Down 🔍", key="chart1_drill_btn", use_container_width=True):
                st.session_state.chart1_month = st.session_state.chart1_month_select
                st.session_state.chart1_drilled = True
                track_dashboard_click("chart1_drill_down", st.session_state.chart1_month)
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart1_month)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=drill_df["Day"],
                y=drill_df["Revenue"],
                name="Revenue",
                marker=dict(color="#60a5fa"),
                hovertemplate="יום: %{x}<br>הכנסות: $%{y:,.0f}<extra></extra>"
            )
        )
        fig = apply_common_layout(fig)
        fig.update_yaxes(tickprefix="$", separatethousands=True, title_text="Revenue")
        fig = set_padded_yaxis(fig, drill_df["Revenue"])
        st.plotly_chart(fig, use_container_width=True)
        if st.button("⬅️ חזרה", key="chart1_back_btn", use_container_width=True):
            st.session_state.chart1_drilled = False
            track_dashboard_click("chart1_back", st.session_state.chart1_month)
            st.rerun()



def show_chart2():
    panel_header("גרף 2: מגמת רווח", chart_narratives["chart2"])

    if not st.session_state.chart2_drilled:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=monthly_total["Month"],
                y=monthly_total["Profit Total"],
                mode="lines+markers",
                name="Profit",
                line=dict(color="#10b981", width=4, shape="spline", smoothing=0.7),
                marker=dict(size=9, color="#ffffff", line=dict(color="#10b981", width=3)),
                fill="none",
                hovertemplate="חודש: %{x}<br>רווח: $%{y:,.0f}<extra></extra>"
            )
        )
        fig = apply_common_layout(fig)
        fig.update_yaxes(tickprefix="$", separatethousands=True, title_text="Profit")
        fig = set_padded_yaxis(fig, monthly_total["Profit Total"])
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([1, 2.2])
        with c2:
            st.selectbox(
                "בחר/י חודש לפירוט:", months_order,
                key="chart2_month_select",
                on_change=track_filter_change,
                args=("chart2_month_select", "chart2_filter_month_change")
            )
        with c1:
            st.write("")
            if st.button("Drill Down 🔍", key="chart2_drill_btn", use_container_width=True):
                st.session_state.chart2_month = st.session_state.chart2_month_select
                st.session_state.chart2_drilled = True
                track_dashboard_click("chart2_drill_down", st.session_state.chart2_month)
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart2_month)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=drill_df["Day"],
                y=drill_df["Profit"],
                name="Profit",
                marker=dict(color="#34d399"),
                hovertemplate="יום: %{x}<br>רווח: $%{y:,.0f}<extra></extra>"
            )
        )
        fig = apply_common_layout(fig)
        fig.update_yaxes(tickprefix="$", separatethousands=True, title_text="Profit")
        fig = set_padded_yaxis(fig, drill_df["Profit"])
        st.plotly_chart(fig, use_container_width=True)
        if st.button("⬅️ חזרה", key="chart2_back_btn", use_container_width=True):
            st.session_state.chart2_drilled = False
            track_dashboard_click("chart2_back", st.session_state.chart2_month)
            st.rerun()



def show_chart3():
    panel_header("גרף 3: הכנסות לפי קטגוריה", chart_narratives["chart3"])

    if not st.session_state.chart3_drilled:
        fig = px.line(
            monthly_category,
            x="Month",
            y="Revenue",
            color="Category",
            markers=True,
            color_discrete_map={"T-shirt": "#2563eb", "Dress": "#ec4899", "Jeans": "#8b5cf6"}
        )
        fig.update_traces(line=dict(width=4, shape="spline"), marker=dict(size=8))
        fig = apply_common_layout(fig)
        fig.update_yaxes(tickprefix="$", separatethousands=True, title_text="Revenue")
        fig = set_padded_yaxis(fig, monthly_category["Revenue"])
        fig.update_traces(hovertemplate="חודש: %{x}<br>הכנסות: $%{y:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([1, 2.2])
        with c2:
            st.selectbox(
                "קטגוריה:", ["T-shirt", "Dress", "Jeans"],
                key="chart3_category_select",
                on_change=track_filter_change,
                args=("chart3_category_select", "chart3_filter_category_change")
            )
        with c1:
            st.write("")
            if st.button("הכנסות מול רווח 🔍", key="chart3_drill_btn", use_container_width=True):
                st.session_state.chart3_category = st.session_state.chart3_category_select
                st.session_state.chart3_drilled = True
                track_dashboard_click("chart3_drill_down", st.session_state.chart3_category)
                st.rerun()
    else:
        drill_df = category_monthly_totals(st.session_state.chart3_category)
        months_list = drill_df["Month"].astype(str).tolist()

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=months_list,
                y=drill_df["Revenue"],
                name="Revenue",
                marker=dict(color="#93c5fd"),
                hovertemplate="חודש: %{x}<br>הכנסות: $%{y:,.0f}<extra></extra>"
            )
        )
        fig.add_trace(
            go.Bar(
                x=months_list,
                y=drill_df["Profit"],
                name="Profit",
                marker=dict(color="#1d4ed8"),
                hovertemplate="חודש: %{x}<br>רווח: $%{y:,.0f}<extra></extra>"
            )
        )
        fig.update_layout(barmode="group")
        fig = apply_common_layout(fig)
        fig.update_yaxes(tickprefix="$", separatethousands=True, title_text="Amount")
        fig = set_padded_yaxis(fig, pd.concat([drill_df["Revenue"], drill_df["Profit"]]))
        st.plotly_chart(fig, use_container_width=True)

        if st.button("⬅️ חזרה", key="chart3_back_btn", use_container_width=True):
            st.session_state.chart3_drilled = False
            track_dashboard_click("chart3_back", st.session_state.chart3_category)
            st.rerun()



def show_chart4():
    panel_header("גרף 4: הנחה ורווח ב-Dress", chart_narratives["chart4"])

    if not st.session_state.chart4_drilled:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=monthly_dress["Month"],
                y=monthly_dress["Profit Dress"],
                name="Profit",
                marker=dict(color="#7c3aed"),
                width=0.48,
                hovertemplate="חודש: %{x}<br>רווח: $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=monthly_dress["Month"],
                y=monthly_dress["Discount Dress"],
                mode="lines+markers",
                name="Discount %",
                line=dict(color="#f59e0b", width=3.5, dash="dot", shape="spline", smoothing=0.7),
                marker=dict(size=8),
                hovertemplate="חודש: %{x}<br>הנחה: %{y:.1f}%<extra></extra>"
            ),
            secondary_y=True
        )
        fig.update_yaxes(title_text="Profit", tickprefix="$", separatethousands=True, secondary_y=False)
        fig.update_yaxes(title_text="Discount (%)", ticksuffix="%", secondary_y=True)
        fig = apply_common_layout(fig)
        fig = set_padded_yaxis(fig, monthly_dress["Profit Dress"], secondary_y=False)
        fig = set_padded_yaxis(fig, monthly_dress["Discount Dress"], secondary_y=True, is_percent=True)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([1, 2.2])
        with c2:
            st.selectbox(
                "בחר/י חודש לפירוט:", months_order,
                key="chart4_month_select",
                on_change=track_filter_change,
                args=("chart4_month_select", "chart4_filter_month_change")
            )
        with c1:
            st.write("")
            if st.button("Drill Down 🔍", key="chart4_drill_btn", use_container_width=True):
                st.session_state.chart4_month = st.session_state.chart4_month_select
                st.session_state.chart4_drilled = True
                track_dashboard_click("chart4_drill_down", st.session_state.chart4_month)
                st.rerun()
    else:
        drill_df = dress_month_daily(st.session_state.chart4_month)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=drill_df["Day"],
                y=drill_df["Profit"],
                name="Profit",
                marker=dict(color="#c4b5fd"),
                hovertemplate="יום: %{x}<br>רווח: $%{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=drill_df["Day"],
                y=drill_df["Discount"],
                mode="lines+markers",
                name="Discount %",
                line=dict(color="#f59e0b", width=3),
                marker=dict(size=7),
                hovertemplate="יום: %{x}<br>הנחה: %{y:.1f}%<extra></extra>"
            ),
            secondary_y=True
        )
        fig.update_yaxes(title_text="Profit", tickprefix="$", separatethousands=True, secondary_y=False)
        fig.update_yaxes(title_text="Discount (%)", ticksuffix="%", secondary_y=True)
        fig = apply_common_layout(fig)
        fig = set_padded_yaxis(fig, drill_df["Profit"], secondary_y=False)
        fig = set_padded_yaxis(fig, drill_df["Discount"], secondary_y=True, is_percent=True)
        st.plotly_chart(fig, use_container_width=True)

        if st.button("⬅️ חזרה", key="chart4_back_btn", use_container_width=True):
            st.session_state.chart4_drilled = False
            track_dashboard_click("chart4_back", st.session_state.chart4_month)
            st.rerun()



def show_or_empty(show_flag, func):
    if show_flag:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        func()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="chart-card-empty"></div>', unsafe_allow_html=True)


# ==============================
# SCREEN: PARTICIPANT SELECTION
# ==============================
if st.session_state.screen == "participant":
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">תחילת הניסוי</div>
            <div class="hero-subtitle">יש להזין מספר משתתף ולבחור את קבוצת הניסוי.</div>
            <div class="hero-text">
                מספר משתתף <strong>9999</strong> מפעיל מצב בדיקה שבו יוצגו באנר המעקב ומסך הסיכום המלא בסיום.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">פרטי פתיחה</div>', unsafe_allow_html=True)
    st.markdown('<div class="form-subtitle">הזיני את פרטי המשתתף לפני המעבר לשאלון הדמוגרפי.</div>', unsafe_allow_html=True)

    side_l, center, side_r = st.columns([1.2, 2, 1.2])
    with center:
        participant_id_input = st.text_input("מספר משתתף", placeholder="למשל 105 או 9999")
        experiment_group_input = st.selectbox("קבוצת ניסוי", ["control", "storytelling"])

    st.markdown('<div class="narrow-button-wide">', unsafe_allow_html=True)
    if st.button("המשך לשאלון הדמוגרפי", use_container_width=True):
        if participant_id_input.strip() == "":
            st.warning("יש להזין מספר משתתף.")
        else:
            st.session_state.participant_id = participant_id_input.strip()
            st.session_state.experiment_group = experiment_group_input
            st.session_state.show_test_banner = is_test_mode()
            st.session_state.screen = "demographics"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# SCREEN: DEMOGRAPHICS
# ==============================
elif st.session_state.screen == "demographics":
    st.markdown(
        """
        <div class="form-card">
            <div class="form-title">שאלון דמוגרפי קצר</div>
            <div class="form-subtitle">לפני תחילת הניסוי נבקש ממך לענות על כמה שאלות כלליות וקצרות. המענה אנונימי ומשמש לצורכי המחקר בלבד.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    side_l, center, side_r = st.columns([1.2, 2, 1.2])
    with center:
        gender = st.selectbox(
            "מגדר",
            ["", "נקבה", "זכר", "אחר", "מעדיפ/ה לא לציין"],
            index=["", "נקבה", "זכר", "אחר", "מעדיפ/ה לא לציין"].index(st.session_state.demographics.get("gender", ""))
                if st.session_state.demographics.get("gender", "") in ["", "נקבה", "זכר", "אחר", "מעדיפ/ה לא לציין"] else 0
        )
        age_range = st.selectbox(
            "טווח גיל",
            ["", "18-24", "25-34", "35-44", "45+", "מעדיפ/ה לא לציין"],
            index=["", "18-24", "25-34", "35-44", "45+", "מעדיפ/ה לא לציין"].index(st.session_state.demographics.get("age_range", ""))
                if st.session_state.demographics.get("age_range", "") in ["", "18-24", "25-34", "35-44", "45+", "מעדיפ/ה לא לציין"] else 0
        )
        experience_level = st.selectbox(
            "עד כמה יש לך ניסיון קודם בקריאת דשבורדים או גרפים עסקיים?",
            ["", "ללא ניסיון", "מעט", "בינוני", "גבוה"],
            index=["", "ללא ניסיון", "מעט", "בינוני", "גבוה"].index(st.session_state.demographics.get("experience_level", ""))
                if st.session_state.demographics.get("experience_level", "") in ["", "ללא ניסיון", "מעט", "בינוני", "גבוה"] else 0
        )

    st.markdown('<div class="narrow-button-wide">', unsafe_allow_html=True)
    if st.button("המשך לטופס ההסכמה", use_container_width=True):
        st.session_state.demographics = {
            "gender": gender,
            "age_range": age_range,
            "experience_level": experience_level,
        }
        st.session_state.screen = "consent"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# SCREEN: CONSENT + WELCOME
# ==============================
elif st.session_state.screen == "consent":
    st.markdown(
        """
<div class="hero-card">
<div class="hero-title">ברוך/ה הבא/ה לניסוי</div>
<div class="hero-subtitle">לפני תחילת המשימה, חשוב לקרוא את ההנחיות בקצרה</div>

<div class="hero-section-title">מהו הניסוי?</div>
<div class="hero-text">
ניסוי זה בוחן כיצד אופן הצגת מידע בדשבורדים עסקיים משפיע על איכות קבלת ההחלטות
ועל רמת המעורבות של המשתמש. יוצגו בפניכם גרפים אינטראקטיביים ועל בסיסם תתבקשו
לענות על <strong>10 שאלות</strong>.
</div>

<div class="hero-section-title">איך עובדים עם הדשבורד?</div>
<div class="hero-text">
בחלק מהגרפים ניתן לבחור חודש או קטגוריה, ולאחר מכן ללחוץ על אייקון <strong>הזכוכית המגדלת 🔍</strong>
כדי לבצע <strong>Drill Down</strong> — כלומר להיכנס פנימה לרמת פירוט עמוקה יותר. לדוגמה, לעבור ממבט חודשי
למבט יומי, או להשוות בתוך קטגוריה מסוימת. לאחר הצפייה בפירוט ניתן ללחוץ על <strong>חזרה</strong> כדי לשוב
למבט הראשי.
</div>

<div class="hero-section-title">זמן הניסוי</div>
<div class="hero-text">
המדידה של משך השהייה הכולל בדשבורד <strong>מתחילה רק לאחר לחיצה על "אני מסכים/ה — התחל ניסוי"</strong>.
כלומר, הזמן במסכים הקודמים אינו נספר בניסוי.
</div>

<div class="hero-highlight">
🔒 <strong>פרטיות וסודיות:</strong> ההשתתפות אנונימית. לא נאסף מידע מזהה אישי מעבר למספר משתתף לצורכי המחקר.<br><br>
✅ <strong>הסכמה:</strong> לחיצה על כפתור ההתחלה מהווה הסכמה מדעת להשתתפות מרצון בניסוי. ניתן להפסיק בכל עת.
</div>
</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="narrow-button">', unsafe_allow_html=True)
    if st.button("אני מסכים/ה — התחל ניסוי", use_container_width=True):
        st.session_state.consent_given = True
        st.session_state.experiment_started = True
        st.session_state.session_start_time = time.time()
        st.session_state.session_end_time = None
        st.session_state.question_start_time = time.time()
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.correct_count = 0
        st.session_state.dashboard_interaction_clicks = 0
        st.session_state.interaction_log = []
        st.session_state.db_saved = False
        st.session_state.chart1_drilled = False
        st.session_state.chart2_drilled = False
        st.session_state.chart3_drilled = False
        st.session_state.chart4_drilled = False
        st.session_state.screen = "experiment"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# SCREEN: EXPERIMENT
# ==============================
elif st.session_state.screen == "experiment":
    if is_test_mode():
        a, b, c, d = st.columns(4)
        with a:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Participant ID</div>'
                f'<div class="metric-value">{st.session_state.participant_id}</div>'
                f'<div class="metric-sub">מצב בדיקה פעיל</div></div>',
                unsafe_allow_html=True
            )
        with b:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Group</div>'
                f'<div class="metric-value">{st.session_state.experiment_group.capitalize()}</div>'
                f'<div class="metric-sub">קבוצת הניסוי שנבחרה</div></div>',
                unsafe_allow_html=True
            )
        with c:
            progress_display = min(st.session_state.current_question + 1, len(questions))
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Progress</div>'
                f'<div class="metric-value">{progress_display} <span style="font-size:1rem;color:#94a3b8">/ {len(questions)}</span></div>'
                f'<div class="metric-sub">השאלות שנצפו עד כה</div></div>',
                unsafe_allow_html=True
            )
        with d:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Interactions</div>'
                f'<div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div>'
                f'<div class="metric-sub">אינטראקציות עם הדשבורד</div></div>',
                unsafe_allow_html=True
            )

    is_storytelling = (st.session_state.experiment_group == "storytelling")
    cq = st.session_state.current_question

    if not is_storytelling:
        show_fig2 = show_fig3 = show_fig4 = True
    else:
        show_fig2 = cq >= 2
        show_fig3 = cq >= 4
        show_fig4 = cq >= 7

    top_left, top_right = st.columns(2)
    bottom_left, bottom_right = st.columns(2)

    with top_left:
        show_or_empty(True, show_chart1)
    with top_right:
        show_or_empty(show_fig2, show_chart2)
    with bottom_left:
        show_or_empty(show_fig3, show_chart3)
    with bottom_right:
        show_or_empty(show_fig4, show_chart4)

    st.markdown(
        '<div class="dashboard-note">💡 אפשר לחקור את הגרפים דרך בחירה בשדות הסינון ולחיצה על 🔍. התשובה ננעלת רק אחרי לחיצה על "שלח/י תשובה".</div>',
        unsafe_allow_html=True
    )

    if cq < len(questions):
        q = questions[cq]

        if is_storytelling and cq in NEW_CHART_AT:
            st.markdown(
                f'<div class="new-chart-badge">✨ {NEW_CHART_AT[cq]} — מומלץ לעיין בגרף החדש לפני המענה</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="question-kicker">שאלה {q["id"]} מתוך {len(questions)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-title">{q["text"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="question-label">בחר/י את התשובה המתאימה ביותר:</div>', unsafe_allow_html=True)

        selected = st.radio(
            "",
            q["options"],
            key=f"question_{q['id']}",
            label_visibility="collapsed"
        )

        if st.button("שלח/י תשובה ✨", use_container_width=True):
            response_time = time.time() - st.session_state.question_start_time
            is_correct_answer = selected == q["correct_answer"]

            st.session_state.answers.append({
                "question_id": q["id"],
                "question_text": q["text"],
                "selected_answer": selected,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct_answer,
                "response_time_seconds": round(response_time, 2)
            })

            if is_correct_answer:
                st.session_state.correct_count += 1

            is_last_question = q["id"] == len(questions)
            if is_last_question:
                st.session_state.session_end_time = time.time()
            else:
                st.session_state.question_start_time = time.time()

            st.session_state.current_question += 1
            st.markdown('</div>', unsafe_allow_html=True)
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if not st.session_state.db_saved:
            persist_all_results()

        if is_test_mode():
            st.session_state.screen = "summary"
        else:
            st.session_state.screen = "thankyou"
        st.rerun()

# ==============================
# SCREEN: SUMMARY (TEST MODE)
# ==============================
elif st.session_state.screen == "summary":
    total_duration = get_total_duration()
    export_df = build_export_df(total_duration)
    interactions_df = build_interactions_df()

    st.markdown(
        """
        <div class="summary-card">
            <div class="summary-emoji">📋</div>
            <div class="summary-title">סיכום מצב בדיקה</div>
            <div class="summary-sub">המסך הזה מוצג רק עבור משתתף 9999, כדי שתוכלי לבדוק מדדים, תשובות ולוג אינטראקציות.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    x, y, z = st.columns(3)
    with x:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">זמן כולל (שניות)</div>'
            f'<div class="metric-value">{round(total_duration, 2)}</div>'
            f'<div class="metric-sub">נספר רק מרגע ההסכמה</div></div>',
            unsafe_allow_html=True
        )
    with y:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">סה״כ אינטראקציות</div>'
            f'<div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div>'
            f'<div class="metric-sub">כולל drill down ושינויי סינון</div></div>',
            unsafe_allow_html=True
        )
    with z:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">תשובות נכונות</div>'
            f'<div class="metric-value">{st.session_state.correct_count} / {len(questions)}</div>'
            f'<div class="metric-sub">סיכום איכות ההחלטות</div></div>',
            unsafe_allow_html=True
        )

    st.subheader("סיכום תשובות")
    st.dataframe(export_df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        csv_results = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 הורדת תוצאות CSV",
            data=csv_results,
            file_name=f"results_{st.session_state.participant_id}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        csv_interactions = interactions_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 הורדת לוג אינטראקציות",
            data=csv_interactions,
            file_name=f"interactions_{st.session_state.participant_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("למסך תודה", use_container_width=True):
            st.session_state.screen = "thankyou"
            st.rerun()
    with btn2:
        if st.button("התחל מחדש 🔄", use_container_width=True):
            reset_app()
            st.rerun()

# ==============================
# SCREEN: THANK YOU
# ==============================
elif st.session_state.screen == "thankyou":
    st.markdown(
        """
        <div class="thankyou-card">
            <div class="thankyou-emoji">🎉</div>
            <div class="thankyou-title">תודה רבה על השתתפותך</div>
            <div class="thankyou-sub">
                השלמת את הניסוי בהצלחה.<br>
                תשובותיך נשמרו לצורכי המחקר האקדמי.<br><br>
                אפשר לסגור את הדפדפן או להתחיל מחדש.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, middle, right = st.columns([1.3, 1.8, 1.3])
    with middle:
        if st.button("התחל מחדש 🔄", use_container_width=True):
            reset_app()
            st.rerun()
