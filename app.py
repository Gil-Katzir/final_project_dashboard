import streamlit as st
import pandas as pd
import plotly.express as px
import time
import uuid
from datetime import datetime
import random
from zoneinfo import ZoneInfo
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
# Styling
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Varela+Round&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', "Segoe UI", sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%),
        radial-gradient(circle at top left, #eef6ff 0%, transparent 30%),
        linear-gradient(180deg, #f8fbff 0%, #edf3f8 100%);
    }

    .block-container {
        max-width: 1400px;
        padding: 2rem 3rem;
    }

    .big-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #1e293b, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        direction: rtl;
        text-align: right;
    }

    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 2rem;
        direction: rtl;
        text-align: right;
    }

    /* ---- Welcome screen ---- */
    .welcome-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 28px;
        padding: 44px 52px;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.08);
        direction: rtl;
        text-align: right;
        max-width: 820px;
        margin: 0 auto;
    }

    .welcome-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #1e293b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        text-align: center;
        font-family: 'Varela Round', sans-serif;
    }

    .welcome-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Varela Round', sans-serif;
    }

    .welcome-section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1e293b;
        margin: 1.4rem 0 0.45rem 0;
        border-right: 4px solid #3b82f6;
        padding-right: 10px;
        font-family: 'Varela Round', sans-serif;
    }

    .welcome-text {
        font-size: 0.95rem;
        margin-bottom: 12px;
        color: #475569;
        line-height: 1.85;
        font-family: 'Varela Round', sans-serif;
    }

    .welcome-highlight {
        background: #eff6ff;
        border-right: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 13px 16px;
        color: #1e40af;
        font-size: 0.93rem;
        margin: 1.3rem 0;
        line-height: 1.75;
        font-family: 'Varela Round', sans-serif;
    }

    .welcome-highlight strong {
        font-family: 'Varela Round', sans-serif;
    }

    .welcome-divider {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 1.8rem 0;
    }

    /* ---- Registration ---- */
    .reg-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 32px 36px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.07);
        direction: rtl;
        text-align: right;
        max-width: 520px;
        margin: 0 auto;
    }

    .reg-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.4rem;
        border-right: 4px solid #3b82f6;
        padding-right: 10px;
        font-family: 'Varela Round', sans-serif;
    }

    /* ---- Metric cards ---- */
    .metric-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(255,255,255,0.4);
        border-radius: 20px;
        padding: 18px 22px;
        box-shadow: 0 8px 20px -4px rgba(0,0,0,0.07);
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px -4px rgba(0,0,0,0.1);
    }

    .metric-label {
        color: #64748b;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 6px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 800;
    }

    .section-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        margin: 1.8rem 0 1.1rem 0;
        padding-right: 12px;
        border-right: 5px solid #3b82f6;
        direction: rtl;
        text-align: right;
        font-family: 'Varela Round', sans-serif;
    }

    /* ---- Chart cards ---- */
    .chart-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 28px;
        padding: 24px;
        box-shadow:
            0 10px 30px rgba(15, 23, 42, 0.06),
            0 2px 8px rgba(15, 23, 42, 0.04);
        backdrop-filter: blur(10px);
        height: 100%;
        animation: fadeIn 0.45s ease;
    }

    .chart-card-empty {
        border-radius: 24px;
        height: 100%;
        min-height: 420px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .chart-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.9rem;
        direction: rtl;
        text-align: right;
        font-family: 'Varela Round', sans-serif;
        letter-spacing: -0.02em;
    }

    .story-box {
        background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
        border: 1px solid #dbeafe;
        border-right: 4px solid #3b82f6;
        border-radius: 14px;
        padding: 12px 15px;
        color: #1e40af;
        font-size: 0.93rem;
        line-height: 1.7;
        margin-bottom: 1.1rem;
        direction: rtl;
        text-align: right;
        font-family: 'Varela Round', sans-serif;
    }

    /* ---- New chart badge ---- */
    .new-chart-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 20px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(16,185,129,0.35);
        animation: popIn 0.4s cubic-bezier(0.34,1.56,0.64,1);
        direction: rtl;
    }

    @keyframes popIn {
        from { opacity: 0; transform: scale(0.7); }
        to   { opacity: 1; transform: scale(1); }
    }

    /* ---- Inputs & Buttons ---- */

    /* ---- Modern radio answers - Fixed Width & Alignment ---- */
    
    /* מוודא שהקומפוננטה עצמה תופסת 100% */
    div[data-testid="stRadio"] {
        width: 100% !important;
        direction: rtl !important;
    }

    /* מוודא שהמיכל הפנימי (הקבוצה) תופס 100% */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
    }

    /* הכפתור עצמו - הופך אותו לבלוק מלא שמתנהג כמו כפתור */
    div[data-testid="stRadio"] [role="radiogroup"] label {
        display: flex !important; /* שינוי מ-block ל-flex */
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;

        background: #ffffff !important;
        border: 1.5px solid #dbe4ee !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        margin: 0 !important;

        cursor: pointer !important;
        transition: all 0.2s ease !important;
        
        /* יישור לימין */
        justify-content: flex-start !important;
        text-align: right !important;
        direction: rtl !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    }

    /* שינוי צבע ב-Hover */
    div[data-testid="stRadio"] [role="radiogroup"] label:hover {
        border-color: #3b82f6 !important;
        background: #f8fbff !important;
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.10) !important;
    }

    /* הסתרת עיגול הבחירה המקורי */
    div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }

    /* עיצוב הטקסט בתוך הכפתור */
    div[data-testid="stRadio"] [role="radiogroup"] label p,
    div[data-testid="stRadio"] [role="radiogroup"] label span {
        width: 100% !important;
        text-align: right !important;
        direction: rtl !important;
        font-family: 'Varela Round', sans-serif !important;
        font-size: 0.98rem !important;
        color: #1e293b !important;
        margin: 0 !important;
        display: block !important;
    }

    


    /* כל סוגי הכפתורים ב-Streamlit */
    div.stButton > button,
    div[data-testid="stButton"] button,
    button[kind="primary"],
    button[kind="secondary"],
    button {
        font-family: 'Varela Round', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        background-color: #ffffff;
        color: #1e293b;
        border: 1.5px solid #e2e8f0;
        transition: all 0.18s ease;
    }

    /* הטקסט שבתוך הכפתור */
    div.stButton > button *,
    div[data-testid="stButton"] button *,
    button[kind="primary"] *,
    button[kind="secondary"] *,
    button * {
        font-family: 'Varela Round', sans-serif !important;
    }

    div.stButton > button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59,130,246,0.12);
    }

    div[data-baseweb="select"] > div {
        border-radius: 12px;
        border: 1.5px solid #e2e8f0;
    }

    .dashboard-note {
        background: #fff7ed;
        color: #9a3412;
        padding: 10px 18px;
        border-radius: 10px;
        font-size: 0.87rem;
        margin-top: 1.1rem;
        display: inline-block;
        direction: rtl;
    }

    .rtl-title, .rtl-question, .rtl-label {
        direction: rtl;
        text-align: right;
    }

    /* ---- Thank-you screen ---- */
    .thankyou-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 28px;
        padding: 60px 48px;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.08);
        text-align: center;
        max-width: 620px;
        margin: 4rem auto;
        animation: fadeIn 0.6s ease;
        direction: rtl;
        font-family: 'Varela Round', sans-serif;
    }

    .thankyou-emoji { font-size: 4rem; margin-bottom: 1rem; }

    .thankyou-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.8rem;
        font-family: 'Varela Round', sans-serif;
    }

    .thankyou-sub {
        font-size: 1rem;
        color: #64748b;
        line-height: 1.8;
        font-family: 'Varela Round', sans-serif;
    }

        /* selectbox טקסט כללי */
    div[data-testid="stSelectbox"] {
        direction: rtl;
        text-align: right;
        font-family: 'Varela Round', sans-serif;
    }

    /* הטקסט שנבחר */
    div[data-testid="stSelectbox"] div {
        text-align: right !important;
        direction: rtl;
        font-family: 'Varela Round', sans-serif !important;
    }

    /* dropdown options */
    ul[role="listbox"] li {
        text-align: right !important;
        direction: rtl;
        font-family: 'Varela Round', sans-serif !important;
    }

        /* תיבת הבחירה עצמה */
    div[data-testid="stSelectbox"] > div {
        border-radius: 12px;
    }

    /* כל ה-text input */
    div[data-testid="stTextInput"] {
        direction: rtl;
        text-align: right;
        font-family: 'Varela Round', sans-serif;
    }

    /* ה-input עצמו (מה שכותבים בו) */
    div[data-testid="stTextInput"] input {
        text-align: right !important;
        direction: rtl;
        font-family: 'Varela Round', sans-serif !important;
    }

    /* ה-placeholder */
    div[data-testid="stTextInput"] input::placeholder {
        text-align: right;
        direction: rtl;
        font-family: 'Varela Round', sans-serif;
    }

    div[data-testid="stTextInput"] label {
        direction: rtl;
        text-align: right;
        font-family: 'Varela Round', sans-serif;
    }

    /* consent checkbox - LTR */
    div[data-testid="stCheckbox"] label {
        font-family: 'Varela Round', sans-serif !important;
        font-size: 0.97rem !important;
        color: #1e293b !important;

        direction: ltr !important;
        text-align: left !important;

        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;

        gap: 10px !important;
        line-height: 1.7 !important;
    }

    /* ---- Post experiment survey ---- */
    .post-survey-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 28px;
        padding: 38px 44px;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.08);
        direction: rtl;
        text-align: right;
        max-width: 900px;
        margin: 2rem auto;
        font-family: 'Varela Round', sans-serif;
    }

    .post-survey-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.6rem;
        font-family: 'Varela Round', sans-serif;
    }

    .post-survey-subtitle {
        font-size: 1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 1.8rem;
        line-height: 1.7;
        font-family: 'Varela Round', sans-serif;
    }

    .likert-banner {
        background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
        border: 1px solid #dbeafe;
        border-radius: 20px;
        padding: 18px 22px;
        margin-bottom: 28px;
        box-shadow: 0 8px 20px rgba(59,130,246,0.08);
        direction: rtl;
        text-align: center;
        font-family: 'Varela Round', sans-serif;
    }

    .likert-banner-main {
        font-size: 1.25rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 10px;
    }

    .likert-scale-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        direction: rtl;
        margin-top: 12px;
    }

    .likert-number {
        flex: 1;
        background: #ffffff;
        border: 1px solid #dbe4ee;
        border-radius: 12px;
        padding: 8px 0;
        font-weight: 800;
        color: #334155;
    }

    .likert-label-row {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        color: #475569;
        font-weight: 700;
        font-size: 0.95rem;
        direction: rtl;
    }

    .post-survey-question {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 20px;
        direction: rtl;
        text-align: right;
        font-family: 'Varela Round', sans-serif;
    }

    .post-survey-question-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 10px;
        font-family: 'Varela Round', sans-serif;
    }

/* ---- Opening register screen ---- */
.opening-wrapper {
    max-width: 760px;
    margin: 2.5rem auto 1.5rem auto;
    direction: rtl;
    text-align: center;
}

.opening-hero {
    background: linear-gradient(135deg, #ffffff 0%, #f8fbff 55%, #eff6ff 100%);
    border: 1px solid #dbe4ee;
    border-radius: 32px;
    padding: 44px 48px;
    box-shadow: 0 22px 45px rgba(15, 23, 42, 0.08);
    font-family: 'Varela Round', sans-serif;
}

.opening-badge {
    display: inline-block;
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    border-radius: 999px;
    padding: 7px 16px;
    font-size: 0.88rem;
    font-weight: 700;
    margin-bottom: 18px;
}

.opening-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 12px;
    letter-spacing: -0.03em;
}

.opening-title span {
    background: linear-gradient(90deg, #2563eb, #1e293b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.opening-subtitle {
    color: #64748b;
    font-size: 1.05rem;
    line-height: 1.9;
    max-width: 620px;
    margin: 0 auto 22px auto;
}

.opening-info-row {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 22px;
}

.opening-info-pill {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: #334155;
    border-radius: 16px;
    padding: 10px 16px;
    font-size: 0.92rem;
    font-weight: 700;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05);
}

.opening-form-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1e293b;
    text-align: center;
    margin-bottom: 18px;
    font-family: 'Varela Round', sans-serif;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
df = pd.read_csv("data.csv")
df["Date"] = pd.to_datetime(df["Date"])
months_order = list(df["Month"].drop_duplicates())

monthly_total = (
    df.groupby("Month", as_index=False)
    .agg(**{
        "Total Revenue": ("Revenue", "sum"),
        "Total Profit":  ("Profit",  "sum")
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
        "Profit Dress":   ("Profit",   "sum")
    })
)
monthly_dress["Month"] = pd.Categorical(monthly_dress["Month"], categories=months_order, ordered=True)
monthly_dress = monthly_dress.sort_values("Month")

monthly_discount_total = (
    df.groupby("Month", as_index=False)
    .agg(**{
        "Campaign Expense Total": ("Discount", "mean")
    })
)
monthly_discount_total["Month"] = pd.Categorical(monthly_discount_total["Month"], categories=months_order, ordered=True)
monthly_discount_total = monthly_discount_total.sort_values("Month")

# -----------------------------
# Questions and narratives
# -----------------------------
questions = [
    {
        "id": 1,
        "text": "בחודש מאי - מה היה היום בו הכנסות החנות היו הגבוהות ביותר?",
        "options": ["20", "16", "3", "10"],
        "correct_answer": "16"
    },
    {
        "id": 2,
        "text": "באיזה חודש הכנסות החנות בתחילת החודש היו גבוהות מההכנסות בסוף החודש?",
        "options": ["פברואר", "אפריל", "מאי", "מרץ"],
        "correct_answer": "פברואר"
    },
    {
        "id": 3,
        "text": "מה היו הוצאות החנות בקירוב בחודש מרץ?",
        "options": ["35K-38K", "49K-55K", "43K-45K", "13K-15K"],
        "correct_answer": "43K-45K"
    },
    {
        "id": 4,
        "text": "באיזה חודש הוצאות החנות היו הגבוהות ביותר?",
        "options": ["ינואר", "יוני", "מרץ", "אפריל"],
        "correct_answer": "יוני"
    },
    {
        "id": 5,
        "text": "מהם ההוצאות בחודש שבו ההכנסות של החנות היו הנמוכות ביותר?",
        "options": ["35K-38K", "40K-42K", "53K-55K", "13K-15K"],
        "correct_answer": "40K-42K"
    },

    {
        "id": 6,
        "text": "בחודש שהכנסות החנות היו הגבוהות ביותר, מה היו ההכנסות מקטגוריית T-Shirt?",
        "options": ["49K", "18K", "18.5K", "15.5K"],
        "correct_answer": "18.5K"
    },
    {
        "id": 7,
        "text": "בחודש שבו ההכנסות החנות היו בין 57K-60K והרווחים היו בין 11K-12K, מה היו ההכנסות בקטגוריית DRESS?",
        "options": ["24K", "25.5K", "18.3K", "27K"],
        "correct_answer": "25.5K"
    },
    {
        "id": 8,
        "text": "בקטגוריה שבה ישנה מגמה הפוכה בין הרווחים להכנסות, בחודש בו הרווחים מהקטגוריה היו 4,619.85$ מה היה הרווח הכולל של החנות?",
        "options": ["56.1k $", "12,85575$", "55k $", "לא ניתן לדעת"],
        "correct_answer": "12,85575$"
    },
    {
        "id": 9,
        "text": "בחודש בו הפרשי ההכנסות בין קטגוריית T-Shirt לקטגוריית Jeans היו 3K$ ,מי הקטגורייה בה אחוז ההוצאות על הקמפיניים היה הגבוה ביותר?",
        "options": [
            "T-Shirt",
            "Dress",
            "Jeans",
            "לא ניתן לדעת"
        ],
        "correct_answer": "Dress"
    },
    {
        "id": 10,
        "text": "מהי המסקנה העסקית המרכזית מהנתונים?",
        "options": [
            "יש להפחית בהשקעה בהוצאות על קמפיניים בכל אחת מהקטגוריות בחנות",
            "עלייה בהכנסות החברה מחודש יולי צפויה להגדיל לאורך זמן את הרווחים של החנות",
            "הגידול בהוצאות על הקמפיינים בקטגוריה מסויימת עשוי לגרום לירידה ברווחים",
            "קטגוריית החולצות והג'ינסים אינן מניבות מספיק רווחים לחנות, יש לנקוט בפעולות לשיפור"
        ],
        "correct_answer": "הגידול בהוצאות על הקמפיינים בקטגוריה מסויימת עשוי לגרום לירידה ברווחים"
    },
]

chart_narratives = {
    "chart1": "📈 בחינת מצב של הכנסות החברה: הגרף מציג את סך ההכנסות החודשיות של חנות הבגדים לאורך זמן.",
    "chart2": "💰 על מנת להמשיך השלים את התמונה, כעת מוצגים בגרף זה גם הרווח הנקי של החברה לאורך זמן",
    "chart3": "🏷️ לשם העמקת הבחינה, מוצגות ההכנסות של חנות הבגדים בחלוקה לפי קטגוריות הלבוש השונות בחנות",
    "chart4": "📉 בגרף מוצג הרווח הכולל של החנות, לצד שיעור ממוצע של הוצאות על קמפיינים הכולל לאורך זמן. ניתן לבחון לפי קטגוריה לבחירתך."
}

# שאלות שבהן נוסף גרף (storytelling) — מפתח = index שאלה (0-based)
NEW_CHART_AT = {2: "גרף 2 נוסף", 4: "גרף 3 נוסף", 8: "גרף 4 נוסף"}

# שאלות קליטה בתחילת הניסוי
# IDs 100-101
initial_comprehension_questions = [
    {
        "id": 100,
        "text": "כמה זה 10% מתוך 105?",
        "options": ["10.5", "15", "9.5", "12"],
        "correct_answer": "10.5",
        "question_type": "initial_comprehension"
    },
    {
        "id": 101,
        "text": "כמה זה 9 כפול 9 פחות 2?",
        "options": ["79", "81", "77", "72"],
        "correct_answer": "79",
        "question_type": "initial_comprehension"
    },
]

# שאלות קשב באמצע הניסוי
# IDs 102-103
middle_attention_questions = [
    {
        "id": 102,
        "text": "נא לבחור בתשובה \"אפשרות 3\" בשאלה זו.",
        "options": ["אפשרות 1", "אפשרות 2", "אפשרות 3", "אפשרות 4"],
        "correct_answer": "אפשרות 3",
        "show_after_question_index": 4,
        "question_type": "middle_attention"
    },
    {
        "id": 103,
        "text": "יש לבחור בתשובה \"כחול\".",
        "options": ["אדום", "ירוק", "כחול", "צהוב"],
        "correct_answer": "כחול",
        "show_after_question_index": 8,
        "question_type": "middle_attention"
    },
]

# שאלות קליטה בסוף הניסוי
# IDs 104-105
final_comprehension_questions = [
    {
        "id": 104,
        "text": "כמה זה 20% מתוך 250?",
        "options": ["40", "45", "50", "55"],
        "correct_answer": "50",
        "question_type": "final_comprehension"
    },
    {
        "id": 105,
        "text": "כמה זה 12 ועוד 18 חלקי 3?",
        "options": ["10", "18", "20", "30"],
        "correct_answer": "18",
        "question_type": "final_comprehension"
    },
]

# שאלות סיכום בסוף הניסוי
# IDs 110-113
post_experiment_survey_questions = [
    {
        "id": 110,
        "text": "עד כמה נהנית מהמשימה?",
        "question_type": "post_survey_enjoyment"
    },
    {
        "id": 111,
        "text": "עד כמה אתה חושב שהצלחת בניסוי?",
        "question_type": "post_survey_perceived_success"
    },
    {
        "id": 112,
        "text": "עד כמה הרגשת עומס מידע במהלך הניסוי?",
        "question_type": "post_survey_information_overload"
    },
    {
        "id": 113,
        "text": "עד כמה הרגשת כי הנתונים הוצגו כחלק מסיפור או רצף רעיוני?",
        "question_type": "post_survey_storytelling_feeling"
    },
]

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "screen": "register",   # register | consent | demographics | instructions | initial_comprehension | experiment | final_comprehension | post_experiment_survey | summary | thankyou
    "experiment_started": False,
    "participant_id": "",
    "experiment_group": "",

    "demographic_age": "",
    "demographic_gender": "",
    "demographic_experience": "",
    "demographic_education": "",
    "demographic_country": "",
    "demographic_occupation": "",
    "demographic_ai_experience": "",
    "demographic_bi_experience": "",
    "consent_given": False,
    "redirect_url": "",

    "initial_comprehension_current": 0,
    "initial_comprehension_answers": [],

    "middle_attention_current": 0,
    "middle_attention_answers": [],

    "final_comprehension_current": 0,
    "final_comprehension_answers": [],

    "post_experiment_survey_answers": [],

    # נשארים לצורך תאימות לאחור אם השתמשת בהם בסיכומים ישנים
    "comprehension_current": 0,
    "comprehension_answers": [],
    "attention_check_shown": False,
    "attention_check_answer": None,
    "attention_check_is_correct": None,
    "attention_check_time_seconds": None,

    "session_id": str(uuid.uuid4()),
    "session_start_time": None,
    "started_at": None,
    "ended_at": None,
    "question_start_time": None,
    "current_question": 0,
    "answers": [],
    "correct_count": 0,
    "dashboard_interaction_clicks": 0,
    "interaction_log": [],

    
    "db_saved": False,
    

    "chart1_drilled": False,
    "chart1_month": months_order[0],

    "chart2_drilled": False,
    "chart2_month": months_order[0],

    "chart3_drilled": False,
    "chart3_category": "Dress",

    "chart4_drilled": False,
    "chart4_category": "Dress",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# Read redirect_url from URL
# -----------------------------
try:
    query_params = st.query_params
    if "redirect_url" in query_params and st.session_state.redirect_url == "":
        st.session_state.redirect_url = query_params["redirect_url"]
except Exception:
    pass



widget_defaults = {
    "chart1_month_select": months_order[0],
    "chart2_month_select": months_order[0],
    "chart3_category_select": "Dress",
    "chart4_category_select": "Dress",
}
for key, value in widget_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

prev_defaults = {
    "__prev_chart1_month_select": None,
    "__prev_chart2_month_select": None,
    "__prev_chart3_category_select": None,
    "__prev_chart4_category_select": None,
}
for key, value in prev_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# Helper functions
# -----------------------------
def is_admin_participant() -> bool:
    return str(st.session_state.participant_id).strip() == "999"


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
    if not st.session_state.experiment_started:
        return

    current_val = st.session_state.get(widget_key)
    prev_key = f"__prev_{widget_key}"
    prev_val = st.session_state.get(prev_key)

    # First automatic widget sync should not count as a dashboard interaction
    if prev_val is None:
        st.session_state[prev_key] = current_val
        return

    if current_val != prev_val:
        track_dashboard_click(action_type, f"{widget_key}={current_val}")
        st.session_state[prev_key] = current_val


def build_export_df(total_duration: float) -> pd.DataFrame:
    summary = {
        "participant_id": st.session_state.participant_id,
        "experiment_group": st.session_state.experiment_group,
        "session_id": st.session_state.session_id,
        "total_duration_seconds": round(total_duration, 2),
        "dashboard_interaction_clicks": st.session_state.dashboard_interaction_clicks,
        "correct_answers_count": st.session_state.correct_count,
        "total_questions": len(questions),
        "demographic_age": st.session_state.demographic_age,
        "demographic_gender": st.session_state.demographic_gender,
        "demographic_experience": st.session_state.demographic_experience,
        "demographic_education": st.session_state.demographic_education,
        "demographic_country": st.session_state.demographic_country,
        "demographic_occupation": st.session_state.demographic_occupation,
        "demographic_ai_experience": st.session_state.demographic_ai_experience,
        "demographic_bi_experience": st.session_state.demographic_bi_experience,
        "initial_comprehension_answers": str(st.session_state.initial_comprehension_answers),
        "middle_attention_answers": str(st.session_state.middle_attention_answers),
        "final_comprehension_answers": str(st.session_state.final_comprehension_answers),
        "post_experiment_survey_answers": str(st.session_state.post_experiment_survey_answers),

        # נשארים לצורך תאימות לאחור
        "comprehension_answers": str(st.session_state.comprehension_answers),
        "attention_check_answer": st.session_state.attention_check_answer,
        "attention_check_is_correct": st.session_state.attention_check_is_correct,
        "attention_check_time_seconds": st.session_state.attention_check_time_seconds,
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
        "started_at": st.session_state.started_at,
        "ended_at": st.session_state.ended_at,
        "total_duration_seconds": float(round(total_duration, 2)),
        "dashboard_interaction_clicks": int(st.session_state.dashboard_interaction_clicks),
        "correct_answers_count": int(st.session_state.correct_count),
        "total_questions": int(len(questions)),
        "demographic_age": str(st.session_state.demographic_age),
        "demographic_gender": str(st.session_state.demographic_gender),
        "demographic_experience": str(st.session_state.demographic_experience),
        "demographic_education": str(st.session_state.demographic_education),
        "demographic_ai_experience": str(st.session_state.demographic_ai_experience),
        "demographic_bi_experience": str(st.session_state.demographic_bi_experience),
    }

    try:
        result = (
            supabase
            .table("sessions")
            .upsert(data, on_conflict="session_id")
            .execute()
        )
        return True, result
    except Exception as e:
        st.error("שגיאה בשמירת session")
        st.code(str(e))
        return False, None


def build_response_row(answer, default_question_type="regular_experiment"):
    selected_answer = answer.get("selected_answer")

    return {
        "session_id": str(st.session_state.session_id),
        "participant_id": str(st.session_state.participant_id),
        "experiment_group": str(st.session_state.experiment_group),

        "question_id": int(answer["question_id"]),
        "question_text": str(answer["question_text"]) if answer.get("question_text") is not None else None,
        "selected_answer": str(selected_answer) if selected_answer is not None else None,
        "correct_answer": str(answer["correct_answer"]) if answer.get("correct_answer") is not None else None,
        "is_correct": bool(answer["is_correct"]) if answer.get("is_correct") is not None else None,
        "response_time_seconds": float(answer["response_time_seconds"]) if answer.get("response_time_seconds") is not None else None,

        # New fields for easier analysis
        "question_type": str(answer.get("question_type", default_question_type)),
    }


def save_responses_to_db():
    rows = []

    # Regular experiment questions: 1-10
    for answer in st.session_state.answers:
        rows.append(build_response_row(answer, "regular_experiment"))

    # Initial comprehension questions: 100-101
    for answer in st.session_state.initial_comprehension_answers:
        rows.append(build_response_row(answer, "initial_comprehension"))

    # Middle attention questions: 102-103
    for answer in st.session_state.middle_attention_answers:
        rows.append(build_response_row(answer, "middle_attention"))

    # Final comprehension questions: 104-105
    for answer in st.session_state.final_comprehension_answers:
        rows.append(build_response_row(answer, "final_comprehension"))

    # Post experiment survey questions: 110-113
    for answer in st.session_state.post_experiment_survey_answers:
        rows.append(build_response_row(answer, "post_experiment_survey"))

    if not rows:
        return True, None

    try:
        result = supabase.table("responses").insert(rows).execute()
        return True, result
    except Exception as e:
        st.error("שגיאה בשמירת responses")
        st.code(str(e))
        return False, None


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


def category_monthly_profit_discount(category_name: str):
    d = (
        df[df["Category"] == category_name]
        .groupby("Month", as_index=False)
        .agg(**{
            "Profit": ("Profit", "sum"),
            "Discount": ("Discount", "mean")
        })
    )
    d["Month"] = pd.Categorical(d["Month"], categories=months_order, ordered=True)
    return d.sort_values("Month")


def category_monthly_totals(category_name):
    d = (
        df[df["Category"] == category_name]
        .groupby("Month", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    )
    d["Month"] = pd.Categorical(d["Month"], categories=months_order, ordered=True)
    return d.sort_values("Month")


def apply_common_layout(fig, title_text):
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.02,
            xanchor="left",
            font=dict(
                size=15,
                color="#1e293b",
                family="Inter, sans-serif"
            )
        ),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=8, r=8, t=52, b=8),
        font=dict(
            family="Inter, sans-serif",
            color="#334155",
            size=12
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.72)",
            bordercolor="rgba(226,232,240,0.8)",
            borderwidth=1,
            font=dict(size=11, color="#475569")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fbfdff",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#dbe4ee",
            font=dict(
                family="Inter, sans-serif",
                size=11,
                color="#334155"
            )
        )
    )

    fig.update_xaxes(
        showgrid=False,
        showline=False,
        tickfont=dict(size=11, color="#64748b"),
        zeroline=False,
        ticks=""
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#edf2f7",
        gridwidth=1,
        showline=False,
        tickfont=dict(size=11, color="#64748b"),
        zeroline=False,
        ticks=""
    )


    return fig

def panel_header(title: str, narrative: str):
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    if st.session_state.experiment_group == "storytelling":
        st.markdown(f'<div class="story-box">{narrative}</div>', unsafe_allow_html=True)


# -----------------------------
# Chart renderers
# -----------------------------
def show_chart1():
    panel_header("הכנסות לפי חודש", chart_narratives["chart1"])

    if not st.session_state.chart1_drilled:
        fig = px.line(
            monthly_total,
            x="Month",
            y="Total Revenue",
            markers=True,
            color_discrete_sequence=["#3b82f6"],
            line_shape="spline"
        )
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=7, line=dict(width=2, color="white"))
        )

        
        fig = apply_common_layout(fig, "Total Revenue by Month")
        fig.update_yaxes(tickprefix="$")

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )

        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2.2, 1])
        with c1:
            st.selectbox(
                "בחר/י חודש לפירוט:", months_order,
                key="chart1_month_select",
                on_change=track_filter_change,
                args=("chart1_month_select", "chart1_filter_month_change")
            )
        with c2:
            st.write("")
            if st.button("Drill Down 🔍", key="chart1_drill_btn", use_container_width=True):
                st.session_state.chart1_month = st.session_state.chart1_month_select
                st.session_state.chart1_drilled = True
                track_dashboard_click("chart1_drill_down", st.session_state.chart1_month)
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart1_month)
        fig = px.line(drill_df, x="Day", y="Revenue", color_discrete_sequence=['#60a5fa'])
        fig = apply_common_layout(fig, f"Daily Revenue — {st.session_state.chart1_month}")
        fig.update_yaxes(tickprefix="$")

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )

        st.plotly_chart(fig, use_container_width=True)
        if st.button("⬅️ חזרה", key="chart1_back_btn", use_container_width=True):
            st.session_state.chart1_drilled = False
            track_dashboard_click("chart1_back", st.session_state.chart1_month)
            st.rerun()


def show_chart2():
    panel_header("רווחים נטו לפי חודש", chart_narratives["chart2"])

    if not st.session_state.chart2_drilled:
        fig = px.line(
            monthly_total,
            x="Month",
            y="Total Profit",
            markers=True,
            color_discrete_sequence=["#10b981"],
            line_shape="spline"
        )
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=7, line=dict(width=2, color="white"))
        )

        fig = apply_common_layout(fig, "Total Profit by Month")
        fig.update_yaxes(tickprefix="$")

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )

        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2.2, 1])
        with c1:
            st.selectbox(
                "בחר/י חודש לפירוט:", months_order,
                key="chart2_month_select",
                on_change=track_filter_change,
                args=("chart2_month_select", "chart2_filter_month_change")
            )
        with c2:
            st.write("")
            if st.button("Drill Down 🔍", key="chart2_drill_btn", use_container_width=True):
                st.session_state.chart2_month = st.session_state.chart2_month_select
                st.session_state.chart2_drilled = True
                track_dashboard_click("chart2_drill_down", st.session_state.chart2_month)
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart2_month)
        fig = px.line(drill_df, x="Day", y="Profit", color_discrete_sequence=['#34d399'])
        fig = apply_common_layout(fig, f"Daily Profit — {st.session_state.chart2_month}")
        fig.update_yaxes(tickprefix="$")

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )

        st.plotly_chart(fig, use_container_width=True)
        if st.button("⬅️ חזרה", key="chart2_back_btn", use_container_width=True):
            st.session_state.chart2_drilled = False
            track_dashboard_click("chart2_back", st.session_state.chart2_month)
            st.rerun()


def show_chart3():
    panel_header("הכנסות לפי קטגוריה", chart_narratives["chart3"])

    if not st.session_state.chart3_drilled:
        fig = px.line(
            monthly_category, x="Month", y="Revenue", color="Category",
            markers=True,
            color_discrete_map={"T-shirt": "#3b82f6", "Dress": "#f43f5e", "Jeans": "#8b5cf6"}
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=7, line=dict(width=2, color="white"))
        )

        fig.update_layout(legend_title_text="")

        fig = apply_common_layout(fig, "Revenue by Category and Month")
        fig.update_yaxes(tickprefix="$")

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )

        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2.2, 1])
        with c1:
            st.selectbox(
                "קטגוריה:", ["T-shirt", "Dress", "Jeans"],
                key="chart3_category_select",
                on_change=track_filter_change,
                args=("chart3_category_select", "chart3_filter_category_change")
            )
        with c2:
            st.write("")
            if st.button("הכנסות vs. רווח 🔍", key="chart3_drill_btn", use_container_width=True):
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
                opacity=0.9
            ),

        )

        fig.add_trace(
            go.Bar(
                x=months_list,
                y=drill_df["Profit"],
                name="Profit",
                opacity=0.9
            ),

        )

        fig.update_layout(barmode="group")
        fig = apply_common_layout(
            fig,
            f"{st.session_state.chart3_category} — Monthly Revenue vs Profit"
        )

        fig.update_yaxes(tickprefix="$")

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )

        st.plotly_chart(fig, use_container_width=True)

        if st.button("⬅️ חזרה", key="chart3_back_btn", use_container_width=True):
            st.session_state.chart3_drilled = False
            track_dashboard_click("chart3_back", st.session_state.chart3_category)
            st.rerun()


def show_chart4():
    panel_header("רווחים וממוצע אחוזי השקעה בקמפיינים", chart_narratives["chart4"])

    if not st.session_state.chart4_drilled:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=monthly_total["Month"],
                y=monthly_total["Total Profit"],
                name="Total Profit",
                marker=dict(
                    color="#8b5cf6",
                    line=dict(width=0)
                ),
                width=0.45,
                opacity=0.9
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=monthly_discount_total["Month"],
                y=monthly_discount_total["Campaign Expense Total"],
                mode="lines+markers",
                name="Campaign Expense %",
                line=dict(color="#f59e0b", width=3, dash="dot"),
                marker=dict(size=7, line=dict(width=2, color="white"))
            ),
            secondary_y=True
        )

        fig = apply_common_layout(fig, "Profit & Campaign Expense (%) by Month")
        fig.update_yaxes(title_text="Profit", secondary_y=False, tickprefix="$")
        fig.update_yaxes(title_text="Average Campaign Expense (%)", secondary_y=True)

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )

        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2.2, 1])
        with c1:
            st.selectbox(
                "בחר/י קטגוריה לפירוט:",
                ["T-shirt", "Dress", "Jeans"],
                key="chart4_category_select",
                on_change=track_filter_change,
                args=("chart4_category_select", "chart4_filter_category_change")
            )
        with c2:
            st.write("")
            if st.button("Drill Through 🔍", key="chart4_drill_btn", use_container_width=True):
                st.session_state.chart4_category = st.session_state.chart4_category_select
                st.session_state.chart4_drilled = True
                track_dashboard_click("chart4_drill_down", st.session_state.chart4_category)
                st.rerun()
    else:
        drill_df = category_monthly_profit_discount(st.session_state.chart4_category)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=drill_df["Month"],
                y=drill_df["Profit"],
                name="Profit",
                marker=dict(
                    color="#8b5cf6",
                    line=dict(width=0)
                ),
                width=0.45,
                opacity=0.9
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=drill_df["Month"],
                y=drill_df["Discount"],
                mode="lines+markers",
                name="Campaign Expense (%)",
                line=dict(color="#f59e0b", width=3, dash="dot"),
                marker=dict(size=7, line=dict(width=2, color="white"))
            ),
            secondary_y=True
        )

        fig = apply_common_layout(
            fig,
            f"{st.session_state.chart4_category}: Profit & Campaign Expense (%) by Month"
        )
        fig.update_yaxes(title_text="Profit", secondary_y=False, tickprefix="$")
        fig.update_yaxes(title_text="Campaign Expense (%)", secondary_y=True)

        fig.update_layout(
            plot_bgcolor="#f7f7f7",
            paper_bgcolor="#f7f7f7"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        if st.button("⬅️ חזרה", key="chart4_back_btn", use_container_width=True):
            st.session_state.chart4_drilled = False
            track_dashboard_click("chart4_back", st.session_state.chart4_category)
            st.rerun()

def show_or_empty(show_flag, func, is_storytelling=False):
    if show_flag:
        func()
    else:
        pass


def get_pending_middle_attention_question(current_question_index: int):
    for attention_q in middle_attention_questions:
        already_answered = any(
            ans["question_id"] == attention_q["id"]
            for ans in st.session_state.middle_attention_answers
        )
        if current_question_index == attention_q["show_after_question_index"] and not already_answered:
            return attention_q
    return None


# ==============================
# SCREEN: REGISTER
# ==============================
# ==============================
# SCREEN: REGISTER
# ==============================
if st.session_state.screen == "register":

    st.markdown("""<div class="opening-wrapper">
<div class="opening-hero">

<div class="opening-title">
ברוכים הבאים ל<span>ניסוי ניתוח נתונים</span>
</div>

<div class="opening-subtitle">
במהלך הניסוי יוצג בפניך דשבורד אינטראקטיבי של חנות אופנה.
המטרה היא לענות על שאלות המבוססות על הנתונים המוצגים BI.
במסכים הבאים יינתן הסבר נוסף על מהלך הניסוי.
אנא הזן את מספר המשתתף שקיבלת
</div>

<div class="opening-info-row">
<div class="opening-info-pill">⏱️ משך משוער: כ-20 דקות</div>
<div class="opening-info-pill">📊 דשבורד אינטראקטיבי</div>
<div class="opening-info-pill">🔒 הנתונים נשמרים באופן אנונימי</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="max-width:520px;margin:1.5rem auto 1rem auto;">
<div class="reg-card">
<div class="opening-form-title">התחלת הניסוי</div>
</div>
</div>
""", unsafe_allow_html=True)

    col_l, col_form, col_r = st.columns([1, 2, 1])

    with col_form:
        participant_id_input = st.text_input(
            "מספר משתתף",
            placeholder="הזינו את מספר המשתתף"
        )

        manual_group = None

        if participant_id_input.strip() == "999":
            manual_group = st.selectbox(
                "קבוצת ניסוי לבדיקה",
                ["control", "storytelling"]
            )

        st.write("")

        if st.button("המשך לטופס ההסכמה ▶", use_container_width=True):
            if participant_id_input.strip() == "":
                st.warning("יש להזין מספר משתתף")
            else:
                st.session_state.participant_id = participant_id_input.strip()

                if participant_id_input.strip() == "999":
                    st.session_state.experiment_group = manual_group
                else:
                    # Random assignment: 50% control, 50% storytelling
                    st.session_state.experiment_group = random.choice(["control", "storytelling"])

                st.session_state.screen = "consent"
                st.rerun()


# ==============================
# SCREEN: CONSENT
# ==============================
elif st.session_state.screen == "consent":
    st.markdown(
"""
<div style="max-width:900px;margin:2rem auto; direction:ltr; text-align:left;">
<div class="welcome-card" style="direction:ltr; text-align:left;">

<div class="welcome-title" style="direction:ltr; text-align:center;">
Informed Consent to Participate in a Study
</div>

<hr class="welcome-divider">

<div class="welcome-text" style="direction:ltr; text-align:left;">
<ol style="line-height:1.9; padding-left:22px;">
<li>You are about to participate in a decision-making study.</li>
<li>During the study, you will be presented with Business Intelligence (BI) dashboards and asked to answer several business analytics questions.</li>
<li>You can withdraw your participation at any time or refuse to answer any question; however, participants who withdraw before completing all the tasks will not receive credit for their participation.</li>
<li>Upon completion of the study, you will reach a completion page where you will receive a verification code confirming your participation. This code may be used, where applicable, to receive compensation or credit for participation.</li>
<li>Confidentiality as to the identity of each participant is guaranteed, and only summary data will be published. It is impossible to connect the personal details of the participant with the answers and data provided during the study.</li>
<li>There is no time limit for completing the study, which should take about 15 minutes.</li>
<li>The study has been approved by the institutional ethics committee of the Department of Industrial Engineering and Management at Ben-Gurion University.</li>
<li>If you have any questions about the study, you may contact Amit Hadad at <b>hadadami@post.bgu.ac.il</b>, Department of Industrial Engineering and Management, Ben-Gurion University of the Negev.</li>
<li>Please check one of the following boxes:</li>
</ol>
</div>

<hr class="welcome-divider">

</div>
</div>
""",
        unsafe_allow_html=True
    )

    col_l, col_form, col_r = st.columns([1, 2, 1])

    with col_form:
        consent_confirm = st.checkbox(
            "I hereby confirm that I have understood the above and freely give my consent to participate in this study. Continue."
        )

        consent_decline = st.checkbox(
            "I do not confirm. Exit."
        )

        st.write("")

        if st.button("Continue ▶", use_container_width=True):

            if consent_decline:
                st.warning("You cannot continue without providing consent.")

            elif not consent_confirm:
                st.warning("Please confirm your consent before continuing.")

            else:
                st.session_state.consent_given = True
                st.session_state.screen = "demographics"
                st.rerun()


# ==============================
# SCREEN: DEMOGRAPHICS
# ==============================
elif st.session_state.screen == "demographics":
    st.markdown(
"""
<div style="max-width:820px;margin:2rem auto;">
<div class="welcome-card">
<div class="welcome-title">שאלון דמוגרפי</div>
<div class="welcome-subtitle">השאלון מיועד לצורכי מחקר בלבד ונשמר באופן אנונימי</div>
<hr class="welcome-divider">

<div class="welcome-text">
לפני תחילת הניסוי, נבקש למלא מספר פרטים כלליים. המידע ישמש לצורכי מחקר בלבד.
</div>
</div>
</div>
""",
        unsafe_allow_html=True
    )

    col_l, col_form, col_r = st.columns([1, 2, 1])

    with col_form:
        age = st.selectbox(
            "טווח גילאים",
            ["", "18–21", "22–27", "28–35", "35 ומעלה"]
        )

        gender = st.selectbox(
            "מגדר",
            ["", "אישה", "גבר", "אחר", "מעדיפ/ה לא לציין"]
        )

        experience = st.selectbox(
            "מהי רמת ההשכלה שלך?",
            ["", "השכלה תיכונית", "סטודנט לתואר ראשון", "בעל תואר רא שון", "בעל תואר שני ומעלה"]
        )

        education = st.selectbox(
            "מהו הרקע העיקרי שלך?",
            ["", "סטודנט/ית", "עובד/ת בתחום עסקי", "עובד/ת בתחום טכנולוגי", "אחר"]
        )

        ai_experience = st.selectbox(
            "האם השתמשת בעבר בכלי חיזוי, אלגוריתמים או מערכות בינה מלאכותית?",
            ["", "לא", "כן, מעט", "כן, במידה בינונית", "כן, במידה רבה"]
        )

        bi_experience = st.selectbox(
            "האם השתמשת בעבר במערכות Business Intelligence (BI)?",
            ["", "לא", "כן, מעט", "כן, במידה בינונית", "כן, במידה רבה"]
        )

        st.write("")

        if st.button("שלח/י והמשך ▶", use_container_width=True):
            if (
                age == "" or gender == "" or experience == "" or education == "" or
                ai_experience == "" or bi_experience == ""
            ):
                st.warning("יש למלא את כל השדות לפני ההמשך")
            else:
                st.session_state.demographic_age = age
                st.session_state.demographic_gender = gender
                st.session_state.demographic_experience = experience
                st.session_state.demographic_education = education
                st.session_state.demographic_ai_experience = ai_experience
                st.session_state.demographic_bi_experience = bi_experience

                st.session_state.screen = "instructions"
                st.rerun()

# ==============================
# SCREEN: INSTRUCTIONS
# ==============================
elif st.session_state.screen == "instructions":
    st.markdown(
"""<div style="max-width:820px;margin:2rem auto;">
<div class="welcome-card">
<div class="welcome-title">הוראות הניסוי</div>
<div class="welcome-subtitle">פרויקט גמר — המחלקה להנדסת תעשייה וניהול, אוניברסיטת בן-גוריון תשפ"ו</div>
<hr class="welcome-divider">

<div class="welcome-section-title">מה עלי לעשות?</div>
<div class="welcome-text">
יש לעיין בדשבורד האינטראקטיבי ולענות על <strong>10 שאלות</strong> המבוססות על הנתונים המוצגים.
לאחר שליחת תשובה לא ניתן לחזור אליה. לא יינתן משוב בזמן אמת לגבי נכונות התשובה.
</div>
<div class="welcome-text">
ניתן לחקור את הנתונים באמצעות סמל הזכוכית המגדלת (🔍), המאפשר לבצע Drill Down (ירידה לפרטים עמוקים יותר) או להציג תצוגות מפורטות יותר של הנתונים.
</div>
<div class="welcome-text">
💡 שימו לב - ערכי ציר ה-Y בגרפים לא תמיד יתחילו מ-0
</div>
<div class="welcome-section-title">תגמול</div>
<div class="welcome-text">
במסגרת הניסוי יוגרלו שלושה פרסים בסך 300 ש"ח כל אחד, כאשר סיכויי הזכייה של כל משתתף נקבעים בהתאם למספר התשובות הנכונות שלו.
</div>
<div class="welcome-section-title">משך הניסוי</div>
<div class="welcome-text">
הניסוי צפוי להימשך כ-<strong>20 דקות</strong>. אין הגבלת זמן לכל שאלה בנפרד.
</div>


<hr class="welcome-divider">
</div>
</div>""",
        unsafe_allow_html=True
    )

    col_l, col_btn, col_r = st.columns([2, 2, 2])
    with col_btn:
        if st.button("המשך ▶", use_container_width=True):
            st.session_state.screen = "initial_comprehension"
            st.rerun()





# ==============================
# SCREEN: INITIAL COMPREHENSION
# ==============================
elif st.session_state.screen == "initial_comprehension":
    st.markdown('''
<div style="max-width:820px;margin:2rem auto;">
<div class="welcome-card">
<div class="welcome-title">ענה על השאלות הבאות</div>
</div>
</div>
''', unsafe_allow_html=True)

    cq_check = st.session_state.initial_comprehension_current

    if cq_check < len(initial_comprehension_questions):
        check_q = initial_comprehension_questions[cq_check]
        st.markdown(
            f'<div class="rtl-title" style="font-size:1.35rem;font-weight:700;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            f'ענה/י על השאלה הבאה:</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'''
            <div style="
                text-align:center;
                font-size:2rem;
                font-weight:800;
                margin-top:4rem;
                margin-bottom:2rem;
                font-family:'Varela Round', sans-serif;
                color:#1e293b;
                direction:rtl;
            ">
                {check_q["text"]}
            </div>
            ''',
            unsafe_allow_html=True
        )

        selected_check = st.radio(
            "",
            check_q["options"],
            key=f"initial_comprehension_{check_q['id']}",
            label_visibility="collapsed",
            index=None
        )

        if st.button("שלח/י תשובה ▶", use_container_width=True):
            if selected_check is None:
                st.warning("יש לבחור תשובה לפני ההמשך")
                st.stop()

            is_check_correct = selected_check == check_q["correct_answer"]
            st.session_state.initial_comprehension_answers.append({
                "question_id": check_q["id"],
                "question_text": check_q["text"],
                "selected_answer": selected_check,
                "correct_answer": check_q["correct_answer"],
                "is_correct": is_check_correct,
                "response_time_seconds": None,
                "question_type": check_q["question_type"],
            })

            st.session_state.comprehension_answers.append({
                "stage": "initial",
                "question_id": check_q["id"],
                "question_text": check_q["text"],
                "selected_answer": selected_check,
                "correct_answer": check_q["correct_answer"],
                "is_correct": is_check_correct,
                "question_type": check_q["question_type"],
            })

            st.session_state.initial_comprehension_current += 1

            if st.session_state.initial_comprehension_current >= len(initial_comprehension_questions):
                st.session_state.experiment_started = True
                st.session_state.session_start_time = time.time()
                st.session_state.started_at = datetime.now(ZoneInfo("Asia/Jerusalem")).isoformat()
                st.session_state.question_start_time = time.time()
                st.session_state.db_saved = False

                # מאתחל את ערכי הפילטרים כדי שלא יספרו כאינטראקציה
                st.session_state["__prev_chart1_month_select"] = st.session_state["chart1_month_select"]
                st.session_state["__prev_chart2_month_select"] = st.session_state["chart2_month_select"]
                st.session_state["__prev_chart3_category_select"] = st.session_state["chart3_category_select"]
                st.session_state["__prev_chart4_category_select"] = st.session_state["chart4_category_select"]
                st.session_state["__filters_initialized"] = True

                st.session_state.screen = "experiment"

            st.rerun()


# ==============================
# SCREEN: FINAL COMPREHENSION
# ==============================
elif st.session_state.screen == "final_comprehension":
    st.markdown('''
<div style="max-width:820px;margin:2rem auto;">
<div class="welcome-card">
<div class="welcome-title">שאלות לסיום</div>
</div>
</div>
''', unsafe_allow_html=True)

    cq_check = st.session_state.final_comprehension_current

    if cq_check < len(final_comprehension_questions):
        check_q = final_comprehension_questions[cq_check]
        st.markdown(
            f'<div class="rtl-title" style="font-size:1.35rem;font-weight:700;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            f'ענה/י על השאלה הבאה:</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'''
            <div style="
                text-align:center;
                font-size:2rem;
                font-weight:800;
                margin-top:4rem;
                margin-bottom:2rem;
                font-family:'Varela Round', sans-serif;
                color:#1e293b;
                direction:rtl;
            ">
                {check_q["text"]}
            </div>
            ''',
            unsafe_allow_html=True
        )

        selected_check = st.radio(
            "",
            check_q["options"],
            key=f"final_comprehension_{check_q['id']}",
            label_visibility="collapsed",
            index=None
        )

        if st.button("שלח/י תשובה ▶", use_container_width=True):
            if selected_check is None:
                st.warning("יש לבחור תשובה לפני ההמשך")
                st.stop()

            is_check_correct = selected_check == check_q["correct_answer"]
            st.session_state.final_comprehension_answers.append({
                "question_id": check_q["id"],
                "question_text": check_q["text"],
                "selected_answer": selected_check,
                "correct_answer": check_q["correct_answer"],
                "is_correct": is_check_correct,
                "response_time_seconds": None,
                "question_type": check_q["question_type"],
            })

            st.session_state.comprehension_answers.append({
            "stage": "final",
            "question_id": check_q["id"],
            "question_text": check_q["text"],
            "selected_answer": selected_check,
            "correct_answer": check_q["correct_answer"],
            "is_correct": is_check_correct,
            "question_type": check_q["question_type"],
            })

            st.session_state.final_comprehension_current += 1

            if st.session_state.final_comprehension_current >= len(final_comprehension_questions):
                st.session_state.screen = "post_experiment_survey"

            st.rerun()

# ==============================
# SCREEN: POST EXPERIMENT SURVEY
# ==============================

elif st.session_state.screen == "post_experiment_survey":

    st.markdown("""<div class="post-survey-card">
<div class="post-survey-title">שאלות סיכום הניסוי</div>
<div class="post-survey-subtitle">
אנא דרג/י את התחושה שלך ביחס לכל אחת מהשאלות הבאות.
<br>
ניתן להזיז את הסקאלה בין 1 ל-7.
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="likert-banner">
<div class="likert-banner-main">סולם הדירוג</div>

<div class="likert-label-row">
<span>במידה רבה מאוד</span>
<span>במידה מועטה מאוד</span>
</div>

<div class="likert-scale-row">
<div class="likert-number">7</div>
<div class="likert-number">6</div>
<div class="likert-number">5</div>
<div class="likert-number">4</div>
<div class="likert-number">3</div>
<div class="likert-number">2</div>
<div class="likert-number">1</div>
</div>
</div>""", unsafe_allow_html=True)

    temp_answers = {}

    for survey_q in post_experiment_survey_questions:
        st.markdown(
            f"""<div class="post-survey-question">
<div class="post-survey-question-title">{survey_q["text"]}</div>
</div>""",
            unsafe_allow_html=True
        )

        temp_answers[survey_q["id"]] = st.select_slider(
            "בחר/י דירוג בין 1 ל-7",
            options=[1, 2, 3, 4, 5, 6, 7],
            value=4,
            key=f"post_survey_{survey_q['id']}",
            label_visibility="collapsed"
        )

    st.write("")

    if st.button("סיום ושליחת תשובות ▶", use_container_width=True):
        # בסקאלה נעה תמיד יש ערך, ברירת המחדל היא 4
        unanswered = []

        st.session_state.post_experiment_survey_answers = []

        for survey_q in post_experiment_survey_questions:
            selected_value = temp_answers[survey_q["id"]]

            st.session_state.post_experiment_survey_answers.append({
                "question_id": survey_q["id"],
                "question_text": survey_q["text"],
                "selected_answer": selected_value,
                "correct_answer": None,
                "is_correct": None,
                "response_time_seconds": None,
                "question_type": survey_q["question_type"],
            })

        total_duration = time.time() - st.session_state.session_start_time
        st.session_state.ended_at = datetime.now(ZoneInfo("Asia/Jerusalem")).isoformat()

        if not st.session_state.db_saved:
            session_ok, _ = save_session_to_db(total_duration)
            responses_ok, _ = save_responses_to_db()

            if session_ok and responses_ok:
                st.session_state.db_saved = True
            else:
                st.warning("השמירה למסד לא הושלמה, אבל הניסוי הסתיים.")

        st.session_state.screen = "summary" if is_admin_participant() else "thankyou"
        st.rerun()

# ==============================
# SCREEN: EXPERIMENT
# ==============================
elif st.session_state.screen == "experiment":
    st.markdown('<div class="big-title" style="direction:ltr; text-align:left;">Fashion Store Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title" style="direction:ltr; text-align:left;">Decision support & Performance analysis</div>', unsafe_allow_html=True)

    # metric bar - visible only for participant 999
    if is_admin_participant():
        a, b, c, d = st.columns(4)
        with a:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Participant ID</div>'
                f'<div class="metric-value">{st.session_state.participant_id}</div></div>',
                unsafe_allow_html=True
            )
        with b:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Group</div>'
                f'<div class="metric-value">{st.session_state.experiment_group.capitalize()}</div></div>',
                unsafe_allow_html=True
            )
        with c:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Progress</div>'
                f'<div class="metric-value">{min(st.session_state.current_question + 1, len(questions))} '
                f'<span style="font-size:1rem;color:#94a3b8">/ {len(questions)}</span></div></div>',
                unsafe_allow_html=True
            )
        with d:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Interactions</div>'
                f'<div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>',
                unsafe_allow_html=True
            )

    # reveal logic
    is_storytelling = (st.session_state.experiment_group == "storytelling")
    cq = st.session_state.current_question

    if not is_storytelling:
        show_fig2 = show_fig3 = show_fig4 = True
    else:
        show_fig2 = cq >= 2
        show_fig3 = cq >= 4
        show_fig4 = cq >= 7

    # dashboard grid
    st.markdown('<div class="section-title">  המידע המוצג מתאר את התנהגות המכירות בחנות בגדים 🛍️---> </div>', unsafe_allow_html=True)

    top_left, top_right = st.columns(2)
    bottom_left, bottom_right = st.columns(2)

    with top_left:
        show_or_empty(True, show_chart1, is_storytelling)
    with top_right:
        show_or_empty(show_fig2, show_chart2, is_storytelling)
    with bottom_left:
        show_or_empty(show_fig3, show_chart3, is_storytelling)
    with bottom_right:
        show_or_empty(show_fig4, show_chart4, is_storytelling)

    st.markdown(
        '<div class="dashboard-note">💡 שים לב! ניתן לשנות את הבחירה לפני לחיצה על "שלח/י תשובה"</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # question block
    if cq < len(questions):

        # middle attention checks - shown after selected regular questions, not counted as questions 1-10
        attention_q = get_pending_middle_attention_question(cq)

        if attention_q is not None:
            st.progress((st.session_state.current_question + 1) / len(questions))

            st.markdown(
                '<div class="rtl-title" style="font-size:1.35rem;font-weight:700;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
                f'ענה/י על השאלה הבאה:</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="rtl-question" style="font-size:1.1rem;font-weight:600;margin-bottom:1rem;font-family:Varela Round, sans-serif;">'
                f'{attention_q["text"]}</div>',
                unsafe_allow_html=True
            )

            attention_selected = st.radio(
                "",
                attention_q["options"],
                key=f"middle_attention_{attention_q['id']}",
                label_visibility="collapsed",
                index=None
            )

            if st.button("שלח/י תשובה ✨", key=f"middle_attention_submit_{attention_q['id']}", use_container_width=True):
                if attention_selected is None:
                    st.warning("יש לבחור תשובה לפני ההמשך")
                    st.stop()

                response_time = time.time() - st.session_state.question_start_time
                is_attention_correct = attention_selected == attention_q["correct_answer"]

                st.session_state.middle_attention_answers.append({
                    "question_id": attention_q["id"],
                    "question_text": attention_q["text"],
                    "selected_answer": attention_selected,
                    "correct_answer": attention_q["correct_answer"],
                    "is_correct": is_attention_correct,
                    "response_time_seconds": round(response_time, 2),
                    "question_type": attention_q["question_type"],
                })

                # backward compatibility for the first old attention-check fields
                if attention_q["id"] == 102:
                    st.session_state.attention_check_answer = attention_selected
                    st.session_state.attention_check_is_correct = is_attention_correct
                    st.session_state.attention_check_time_seconds = round(response_time, 2)

                st.session_state.middle_attention_current = len(st.session_state.middle_attention_answers)

                if len(st.session_state.middle_attention_answers) >= len(middle_attention_questions):
                    st.session_state.attention_check_shown = True

                st.session_state.question_start_time = time.time()
                st.rerun()

            st.stop()

        q = questions[cq]

        progress = (st.session_state.current_question + 1) / len(questions)
        st.progress(progress)

        # new chart badge (storytelling only, at trigger questions)
        if is_storytelling and cq in NEW_CHART_AT:
            st.markdown(
                f'<div class="new-chart-badge">✨ {NEW_CHART_AT[cq]} — עיינו בדשבורד לפני המענה</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="rtl-title" style="font-size:1.35rem;font-weight:700;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            f'שאלה {q["id"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="rtl-question" style="font-size:1.1rem;font-weight:600;margin-bottom:1rem;font-family:Varela Round, sans-serif;">'
            f'{q["text"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="rtl-label" style="font-weight:600;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            'בחר/י את התשובה הנכונה ביותר:</div>',
            unsafe_allow_html=True
        )

        selected = st.radio(
            "",
            q["options"],
            key=f"question_{q['id']}",
            label_visibility="collapsed",
            index=None
        )

        if st.button("שלח/י תשובה ✨", use_container_width=True):

            if selected is None:
                st.warning("יש לבחור תשובה לפני ההמשך")
                st.stop()

            response_time = time.time() - st.session_state.question_start_time
            is_correct = selected == q["correct_answer"]

            st.session_state.answers.append({
                "question_id": q["id"],
                "question_text": q["text"],
                "selected_answer": selected,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct,
                "response_time_seconds": round(response_time, 2),
                "question_type": "regular_experiment",
            })

            if is_correct:
                st.session_state.correct_count += 1

            st.session_state.current_question += 1
            st.session_state.question_start_time = time.time()
            st.rerun()

    else:
        st.session_state.question_start_time = time.time()
        st.session_state.screen = "final_comprehension"
        st.rerun()


# ==============================
# SCREEN: SUMMARY
# ==============================
elif st.session_state.screen == "summary":
    if not is_admin_participant():
        st.session_state.screen = "thankyou"
        st.rerun()

    total_duration = time.time() - st.session_state.session_start_time
    st.session_state.ended_at = datetime.now(ZoneInfo("Asia/Jerusalem")).isoformat()

    export_df = build_export_df(total_duration)
    interactions_df = build_interactions_df()

    if not st.session_state.db_saved:
        session_ok, _ = save_session_to_db(total_duration)
        responses_ok, _ = save_responses_to_db()

        if session_ok and responses_ok:
            st.session_state.db_saved = True
        else:
            st.warning("השמירה למסד לא הושלמה, אבל אפשר עדיין להוריד את הנתונים כ-CSV.")

    st.balloons()
    st.markdown('<div class="big-title">📋 סיכום ביצועים</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">הניסוי הסתיים — להלן תוצאות הסשן שלך</div>', unsafe_allow_html=True)

    x, y, z = st.columns(3)
    with x:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">זמן כולל (שניות)</div>'
            f'<div class="metric-value">{round(total_duration, 2)}</div></div>',
            unsafe_allow_html=True
        )
    with y:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">סה״כ אינטראקציות</div>'
            f'<div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>',
            unsafe_allow_html=True
        )
    with z:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">תשובות נכונות</div>'
            f'<div class="metric-value">{st.session_state.correct_count} / {len(questions)}</div></div>',
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

    st.markdown("<br>", unsafe_allow_html=True)
    btn1, btn2, btn3 = st.columns([1, 2, 1])
    with btn2:
        if st.button("✅ לחץ לסיום", use_container_width=True):
            st.session_state.screen = "thankyou"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("התחל מחדש 🔄", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ==============================
# SCREEN: THANK YOU
# ==============================
elif st.session_state.screen == "thankyou":

    final_redirect_url = st.session_state.redirect_url if st.session_state.redirect_url else "https://dashboard-experiment.streamlit.app/"

    st.markdown("""<div class="thankyou-card">
<div class="thankyou-emoji">🎉</div>
<div class="thankyou-title">תודה על השתתפותך!</div>
<div class="thankyou-sub">
השתתפותך בניסוי זה תורמת למחקר אקדמי חשוב בתחום מערכות מידע עסקיות.<br>
התוצאות ישמשו למחקר בלבד.<br><br>
על מנת להירשם במערכת על כך שביצעת את הניסוי - לחץ על הכפתור לסיום.
</div>
</div>""", unsafe_allow_html=True)

    col_l, col_btn, col_r = st.columns([2, 2, 2])

    with col_btn:
        st.markdown(
            f"""<a href="{final_redirect_url}" target="_self" style="text-decoration:none;">
<button style="
width:100%;
font-family:'Varela Round', sans-serif;
font-weight:700;
font-size:1rem;
border-radius:12px;
padding:0.75rem 2rem;
background-color:#2563eb;
color:white;
border:none;
cursor:pointer;
">
לחץ לסיום
</button>
</a>""",
            unsafe_allow_html=True
        )