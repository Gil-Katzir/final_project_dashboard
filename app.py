import streamlit as st
import pandas as pd
import plotly.express as px
import time
import uuid
from datetime import datetime, timedelta
import random
import json
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from supabase import create_client, Client

# -----------------------------
# Page config - must be first Streamlit command
# -----------------------------
st.set_page_config(
    page_title="Data Analysis Experiment",
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
        direction: ltr;
        text-align: left;
    }

    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 2rem;
        direction: ltr;
        text-align: left;
    }

    /* ---- Welcome screen ---- */
    .welcome-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 28px;
        padding: 44px 52px;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.08);
        direction: ltr;
        text-align: left;
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
        border-left: 4px solid #3b82f6;
        padding-left: 10px;
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
        border-left: 4px solid #3b82f6;
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
        direction: ltr;
        text-align: left;
        max-width: 520px;
        margin: 0 auto;
    }

    .reg-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.4rem;
        border-left: 4px solid #3b82f6;
        padding-left: 10px;
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
        padding-left: 12px;
        border-left: 5px solid #3b82f6;
        direction: ltr;
        text-align: left;
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
        direction: ltr;
        text-align: left;
        font-family: 'Varela Round', sans-serif;
        letter-spacing: -0.02em;
    }

    .story-box {
        background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
        border: 1px solid #dbeafe;
        border-left: 4px solid #3b82f6;
        border-radius: 14px;
        padding: 12px 15px;
        color: #1e40af;
        font-size: 0.93rem;
        line-height: 1.7;
        margin-bottom: 1.1rem;
        direction: ltr;
        text-align: left;
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
        direction: ltr;
    }

    @keyframes popIn {
        from { opacity: 0; transform: scale(0.7); }
        to   { opacity: 1; transform: scale(1); }
    }

    /* ---- Inputs & Buttons ---- */

    /* ---- Modern radio answers - Fixed Width & Alignment ---- */
    
    /* Ensures the component takes full width */
    div[data-testid="stRadio"] {
        width: 100% !important;
        direction: ltr !important;
    }

    /* Ensures the inner radio group takes full width */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
    }

    /* Radio option as a full-width button */
    div[data-testid="stRadio"] [role="radiogroup"] label {
        display: flex !important; /* changed from block to flex */
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
        
        /* left alignment */
        justify-content: flex-start !important;
        text-align: left !important;
        direction: ltr !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    }

    /* Hover color change */
    div[data-testid="stRadio"] [role="radiogroup"] label:hover {
        border-color: #3b82f6 !important;
        background: #f8fbff !important;
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.10) !important;
    }

    /* Hide original radio circle */
    div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }

    /* Style text inside the button */
    div[data-testid="stRadio"] [role="radiogroup"] label p,
    div[data-testid="stRadio"] [role="radiogroup"] label span {
        width: 100% !important;
        text-align: left !important;
        direction: ltr !important;
        font-family: 'Varela Round', sans-serif !important;
        font-size: 0.98rem !important;
        color: #1e293b !important;
        margin: 0 !important;
        display: block !important;
    }

    


    /* All Streamlit button types */
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

    /* Text inside the button */
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
        direction: ltr;
    }

    .rtl-title, .rtl-question, .rtl-label {
        direction: ltr;
        text-align: left;
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
        direction: ltr;
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

        /* General selectbox text */
    div[data-testid="stSelectbox"] {
        direction: ltr;
        text-align: left;
        font-family: 'Varela Round', sans-serif;
    }

    /* Selected text */
    div[data-testid="stSelectbox"] div {
        text-align: left !important;
        direction: ltr;
        font-family: 'Varela Round', sans-serif !important;
    }

    /* dropdown options */
    ul[role="listbox"] li {
        text-align: left !important;
        direction: ltr;
        font-family: 'Varela Round', sans-serif !important;
    }

        /* Selectbox itself */
    div[data-testid="stSelectbox"] > div {
        border-radius: 12px;
    }

    /* All text inputs */
    div[data-testid="stTextInput"] {
        direction: ltr;
        text-align: left;
        font-family: 'Varela Round', sans-serif;
    }

    /* Input field text */
    div[data-testid="stTextInput"] input {
        text-align: left !important;
        direction: ltr;
        font-family: 'Varela Round', sans-serif !important;
    }

    /* Placeholder */
    div[data-testid="stTextInput"] input::placeholder {
        text-align: left;
        direction: ltr;
        font-family: 'Varela Round', sans-serif;
    }

    div[data-testid="stTextInput"] label {
        direction: ltr;
        text-align: left;
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
        direction: ltr;
        text-align: left;
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
        direction: ltr;
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
        direction: ltr;
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
        direction: ltr;
    }

    .post-survey-question {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 20px;
        direction: ltr;
        text-align: left;
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
    direction: ltr;
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
        "text": "In May, on which day were the store revenues the highest?",
        "options": ["20", "16", "3", "10"],
        "correct_answer": "16"
    },
    {
        "id": 2,
        "text": "In which month were the store revenues at the beginning of the month higher than at the end of the month?",
        "options": ["February", "April", "May", "March"],
        "correct_answer": "February"
    },
    {
        "id": 3,
        "text": "What were the store expenses approximately in March?",
        "options": ["35K-38K", "49K-55K", "43K-45K", "13K-15K"],
        "correct_answer": "43K-45K"
    },
    {
        "id": 4,
        "text": "In which month were the store expenses the highest?",
        "options": ["January", "June", "March", "April"],
        "correct_answer": "June"
    },
    {
        "id": 5,
        "text": "What were the expenses in the month when the store revenues were the lowest?",
        "options": ["35K-38K", "40K-42K", "53K-55K", "13K-15K"],
        "correct_answer": "40K-42K"
    },

    {
        "id": 6,
        "text": "In the month when the store revenues were the highest, what were the revenues from the T-Shirt category?",
        "options": ["49K", "18K", "18.5K", "15.5K"],
        "correct_answer": "18.5K"
    },
    {
        "id": 7,
        "text": "In the month when store revenues were between $57K and $60K and profits were between $11K and $12K, what were the revenues from the Dress category?",
        "options": ["24K", "25.5K", "18.3K", "27K"],
        "correct_answer": "25.5K"
    },
    {
        "id": 8,
        "text": "In the category where profits and revenues show an opposite trend, in the month when the category profit was $4,619.85, what was the total store profit?",
        "options": ["$56.1K", "$12,855.75", "$55K", "Cannot be determined"],
        "correct_answer": "12,85575$"
    },
    {
        "id": 9,
        "text": "In the month when the revenue difference between the T-Shirt and Jeans categories was $3K, which category had the highest campaign expense percentage?",
        "options": [
            "T-Shirt",
            "Dress",
            "Jeans",
            "Cannot be determined"
        ],
        "correct_answer": "Dress"
    },
    {
        "id": 10,
        "text": "What is the main business conclusion from the data?",
        "options": [
            "The store should reduce campaign spending across all categories",
            "An increase in company revenues from July is expected to increase store profits over time",
            "An increase in campaign expenses in a specific category may lead to a decrease in profits",
            "The T-Shirt and Jeans categories are not generating enough profit for the store, and improvement actions should be taken"
        ],
        "correct_answer": "An increase in campaign expenses in a specific category may lead to a decrease in profits"
    },
]

chart_narratives = {
    "chart1": "📈 Revenue overview: This chart presents the clothing store’s total monthly revenues over time.",
    "chart2": "💰 To complete the picture, this chart now presents the company’s net profit over time.",
    "chart3": "🏷️ To deepen the analysis, the store’s revenues are displayed by clothing category.",
    "chart4": "📉 This chart presents the store’s total profit alongside the average campaign expense percentage over time. You can examine the data by selected category."
}

# Questions where a new chart is added (storytelling) — key = question index (0-based)
NEW_CHART_AT = {2: "Chart 2 added", 4: "Chart 3 added", 8: "Chart 4 added"}

# Initial comprehension questions
# IDs 100-101
initial_comprehension_questions = [
    {
        "id": 100,
        "text": "What is 10% of 105?",
        "options": ["10.5", "15", "9.5", "12"],
        "correct_answer": "10.5",
        "question_type": "initial_comprehension"
    },
    {
        "id": 101,
        "text": "What is 9 multiplied by 9 minus 2?",
        "options": ["79", "81", "77", "72"],
        "correct_answer": "79",
        "question_type": "initial_comprehension"
    },
]

# Middle attention questions
# IDs 102-103
middle_attention_questions = [
    {
        "id": 102,
        "text": "Please select the answer \"Option 3\" for this question.",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "correct_answer": "Option 3",
        "show_after_question_index": 4,
        "question_type": "middle_attention"
    },
    {
        "id": 103,
        "text": "Please select the answer \"Blue\".",
        "options": ["Red", "Green", "Blue", "Yellow"],
        "correct_answer": "Blue",
        "show_after_question_index": 8,
        "question_type": "middle_attention"
    },
]

# Final comprehension questions
# IDs 104-105
final_comprehension_questions = [
    {
        "id": 104,
        "text": "What is 20% of 250?",
        "options": ["40", "45", "50", "55"],
        "correct_answer": "50",
        "question_type": "final_comprehension"
    },
    {
        "id": 105,
        "text": "What is 12 plus 18 divided by 3?",
        "options": ["10", "18", "20", "30"],
        "correct_answer": "18",
        "question_type": "final_comprehension"
    },
]

# Post-experiment survey questions
# IDs 110-113
post_experiment_survey_questions = [
    {
        "id": 110,
        "text": "To what extent did you enjoy the task?",
        "question_type": "post_survey_enjoyment"
    },
    {
        "id": 111,
        "text": "To what extent do you think you succeeded in the experiment?",
        "question_type": "post_survey_perceived_success"
    },
    {
        "id": 112,
        "text": "To what extent did you feel information overload during the experiment?",
        "question_type": "post_survey_information_overload"
    },
    {
        "id": 113,
        "text": "To what extent did you feel that the data were presented as part of a story or conceptual sequence?",
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

    # Kept for backward compatibility with older summaries
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
    "filters_ready_for_tracking": False,
    "tracked_filters_initialized": {},

    
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

    if st.session_state.current_question >= len(questions):
        return

    current_val = st.session_state.get(widget_key)
    prev_key = f"__prev_{widget_key}"

    if "tracked_filters_initialized" not in st.session_state:
        st.session_state.tracked_filters_initialized = {}

    # If this filter has not appeared on the screen before —
    # Initialize it only and do not count an interaction
    if not st.session_state.tracked_filters_initialized.get(widget_key, False):
        st.session_state[prev_key] = current_val
        st.session_state.tracked_filters_initialized[widget_key] = True
        return

    prev_val = st.session_state.get(prev_key)

    # Count only if the participant actually changed the value
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

        # Kept for backward compatibility
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

def db_israel_time():
    """
    Returns current time shifted +3 hours for DB display.
    This is used because Supabase displays timestamps 3 hours behind Israel time.
    """
    return (datetime.utcnow() + timedelta(hours=3)).isoformat(sep=" ", timespec="seconds")


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
        st.error("Error saving session")
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
        "created_at": db_israel_time(),
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
        st.error("Error saving responses")
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
    panel_header("Revenue by Month", chart_narratives["chart1"])

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
                "Select a month for details:", months_order,
                key="chart1_month_select",
                #on_change=track_filter_change,
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
        if st.button("⬅️ Back", key="chart1_back_btn", use_container_width=True):
            st.session_state.chart1_drilled = False
            track_dashboard_click("chart1_back", st.session_state.chart1_month)
            st.rerun()


def show_chart2():
    panel_header("Net Profit by Month", chart_narratives["chart2"])

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
                "Select a month for details:", months_order,
                key="chart2_month_select",
                #on_change=track_filter_change,
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
        if st.button("⬅️ Back", key="chart2_back_btn", use_container_width=True):
            st.session_state.chart2_drilled = False
            track_dashboard_click("chart2_back", st.session_state.chart2_month)
            st.rerun()


def show_chart3():
    panel_header("Revenue by Category", chart_narratives["chart3"])

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
                "Category:", ["T-shirt", "Dress", "Jeans"],
                key="chart3_category_select",
                #on_change=track_filter_change,
                args=("chart3_category_select", "chart3_filter_category_change")
            )
        with c2:
            st.write("")
            if st.button("Revenue vs. Profit 🔍", key="chart3_drill_btn", use_container_width=True):
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

        if st.button("⬅️ Back", key="chart3_back_btn", use_container_width=True):
            st.session_state.chart3_drilled = False
            track_dashboard_click("chart3_back", st.session_state.chart3_category)
            st.rerun()


def show_chart4():
    panel_header("Profit and Average Campaign Expense Percentage", chart_narratives["chart4"])

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
                "Select a category for details:",
                ["T-shirt", "Dress", "Jeans"],
                key="chart4_category_select",
                #on_change=track_filter_change,
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

        if st.button("⬅️ Back", key="chart4_back_btn", use_container_width=True):
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
Welcome to the <span>Data Analysis Experiment</span>
</div>

<div class="opening-subtitle">
During the experiment, you will be presented with an interactive dashboard of a fashion store.
Your task is to answer questions based on the data displayed.
The following screens will provide additional information about the experiment process.
Please enter the participant number you received in the designated field below.
</div>

<div class="opening-info-row">
<div class="opening-info-pill">⏱️ Estimated duration: about 20 minutes</div>
<div class="opening-info-pill">📊 Interactive dashboard</div>
<div class="opening-info-pill">🔒 Data are stored anonymously</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="max-width:520px;margin:1.5rem auto 1rem auto;">
<div class="reg-card">
<div class="opening-form-title">Start the Experiment</div>
</div>
</div>
""", unsafe_allow_html=True)

    col_l, col_form, col_r = st.columns([1, 2, 1])

    with col_form:
        participant_id_input = st.text_input(
            "Participant ID",
            placeholder="Enter your participant ID"
        )

        manual_group = None

        if participant_id_input.strip() == "999":
            manual_group = st.selectbox(
                "Test experiment group",
                ["control", "storytelling"]
            )

        st.write("")

        if st.button("Continue to Consent Form ▶", use_container_width=True):
            if participant_id_input.strip() == "":
                st.warning("Please enter a participant ID")
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
<div class="welcome-title">Demographic Questionnaire</div>
<div class="welcome-subtitle">This questionnaire is intended for research purposes only and is stored anonymously</div>
<hr class="welcome-divider">

<div class="welcome-text">
Before starting the experiment, please answer a few general questions. The information will be used for research purposes only.
</div>
</div>
</div>
""",
        unsafe_allow_html=True
    )

    col_l, col_form, col_r = st.columns([1, 2, 1])

    with col_form:
        age = st.selectbox(
            "Age range",
            ["", "18–21", "22–27", "28–35", "35 and above"]
        )

        gender = st.selectbox(
            "Gender",
            ["", "Female", "Male", "Other", "Prefer not to say"]
        )

        experience = st.selectbox(
            "What is your education level?",
            ["", "High school education", "Undergraduate student", "Bachelor’s degree", "Master’s degree or higher"]
        )

        education = st.selectbox(
            "What is your main background?",
            ["", "Student", "Business field employee", "Technology field employee", "Other"]
        )

        ai_experience = st.selectbox(
            "Have you previously used prediction tools, algorithms, or artificial intelligence systems?",
            ["", "No", "Yes, a little", "Yes, to a moderate extent", "Yes, to a great extent"]
        )

        bi_experience = st.selectbox(
            "Have you previously used Business Intelligence (BI) systems?",
            ["", "No", "Yes, a little", "Yes, to a moderate extent", "Yes, to a great extent"]
        )

        st.write("")

        if st.button("Submit and Continue ▶", use_container_width=True):
            if (
                age == "" or gender == "" or experience == "" or education == "" or
                ai_experience == "" or bi_experience == ""
            ):
                st.warning("Please complete all fields before continuing")
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
<div class="welcome-title">Experiment Instructions</div>
<div class="welcome-subtitle">Final Project — Department of Industrial Engineering and Management, Ben-Gurion University</div>
<hr class="welcome-divider">

<div class="welcome-section-title">What should I do?</div>
<div class="welcome-text">
Review the interactive dashboard and answer <strong>10 questions</strong> based on the data presented.
After submitting an answer, you will not be able to go back to it. No real-time feedback will be provided regarding answer correctness.
</div>
<div class="welcome-text">
You can explore the data using the magnifying glass icon (🔍), which allows you to perform Drill Down or display more detailed views of the data.
</div>
<div class="welcome-text">
💡 Please note: the Y-axis values in the charts may not always start at 0.
</div>
<div class="welcome-section-title">Reward</div>
<div class="welcome-text">
As part of the experiment, three prizes of NIS 300 each will be raffled. Each participant’s chance of winning is determined by the number of correct answers.
</div>
<div class="welcome-section-title">Experiment duration</div>
<div class="welcome-text">
The experiment is expected to take about <strong>20 minutes</strong>. There is no time limit for each individual question.
</div>


<hr class="welcome-divider">
</div>
</div>""",
        unsafe_allow_html=True
    )

    col_l, col_btn, col_r = st.columns([2, 2, 2])
    with col_btn:
        if st.button("Continue ▶", use_container_width=True):
            st.session_state.screen = "initial_comprehension"
            st.rerun()





# ==============================
# SCREEN: INITIAL COMPREHENSION
# ==============================
elif st.session_state.screen == "initial_comprehension":

    if st.session_state.question_start_time is None:
        st.session_state.question_start_time = time.time()

    st.markdown('''
<div style="max-width:820px;margin:2rem auto;">
<div class="welcome-card">
<div class="welcome-title">Answer the Following Questions</div>
</div>
</div>
''', unsafe_allow_html=True)

    cq_check = st.session_state.initial_comprehension_current

    if cq_check < len(initial_comprehension_questions):
        check_q = initial_comprehension_questions[cq_check]
        st.markdown(
            f'<div class="rtl-title" style="font-size:1.35rem;font-weight:700;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            f'Please answer the following question:</div>',
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

        if st.button("Submit Answer ▶", use_container_width=True):
            if selected_check is None:
                st.warning("Please select an answer before continuing")
                st.stop()

            response_time = time.time() - st.session_state.question_start_time
            is_check_correct = selected_check == check_q["correct_answer"]
            st.session_state.initial_comprehension_answers.append({
                "question_id": check_q["id"],
                "question_text": check_q["text"],
                "selected_answer": selected_check,
                "correct_answer": check_q["correct_answer"],
                "is_correct": is_check_correct,
                "response_time_seconds": round(response_time, 2),
                "question_type": check_q["question_type"],
            })

            st.session_state.comprehension_answers.append({
                "stage": "initial",
                "question_id": check_q["id"],
                "question_text": check_q["text"],
                "selected_answer": selected_check,
                "correct_answer": check_q["correct_answer"],
                "is_correct": is_check_correct,
                "response_time_seconds": round(response_time, 2),
                "question_type": check_q["question_type"],
            })

            st.session_state.initial_comprehension_current += 1
            st.session_state.question_start_time = time.time()

            if st.session_state.initial_comprehension_current >= len(initial_comprehension_questions):
                st.session_state.experiment_started = True
                st.session_state.session_start_time = time.time()
                st.session_state.started_at = db_israel_time()
                st.session_state.question_start_time = time.time()
                st.session_state.db_saved = False
                st.session_state.filters_ready_for_tracking = False

                st.session_state.tracked_filters_initialized = {}

                st.session_state["__prev_chart1_month_select"] = None
                st.session_state["__prev_chart2_month_select"] = None
                st.session_state["__prev_chart3_category_select"] = None
                st.session_state["__prev_chart4_category_select"] = None

                # Initializes filter values so they are not counted as interactions
                #st.session_state["__prev_chart1_month_select"] = st.session_state["chart1_month_select"]
                #st.session_state["__prev_chart2_month_select"] = st.session_state["chart2_month_select"]
                #st.session_state["__prev_chart3_category_select"] = st.session_state["chart3_category_select"]
                #st.session_state["__prev_chart4_category_select"] = st.session_state["chart4_category_select"]
                #st.session_state["__filters_initialized"] = True

                st.session_state.screen = "experiment"

            st.rerun()


# ==============================
# SCREEN: FINAL COMPREHENSION
# ==============================
elif st.session_state.screen == "final_comprehension":

    if st.session_state.question_start_time is None:
        st.session_state.question_start_time = time.time()

    st.markdown('''
<div style="max-width:820px;margin:2rem auto;">
<div class="welcome-card">
<div class="welcome-title">Final Questions</div>
</div>
</div>
''', unsafe_allow_html=True)

    cq_check = st.session_state.final_comprehension_current

    if cq_check < len(final_comprehension_questions):
        check_q = final_comprehension_questions[cq_check]
        st.markdown(
            f'<div class="rtl-title" style="font-size:1.35rem;font-weight:700;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            f'Please answer the following question:</div>',
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

        if st.button("Submit Answer ▶", use_container_width=True):
            if selected_check is None:
                st.warning("Please select an answer before continuing")
                st.stop()

            response_time = time.time() - st.session_state.question_start_time
            is_check_correct = selected_check == check_q["correct_answer"]
            st.session_state.final_comprehension_answers.append({
                "question_id": check_q["id"],
                "question_text": check_q["text"],
                "selected_answer": selected_check,
                "correct_answer": check_q["correct_answer"],
                "is_correct": is_check_correct,
                "response_time_seconds": round(response_time, 2),
                "question_type": check_q["question_type"],
            })

            st.session_state.comprehension_answers.append({
            "stage": "final",
            "question_id": check_q["id"],
            "question_text": check_q["text"],
            "selected_answer": selected_check,
            "correct_answer": check_q["correct_answer"],
            "is_correct": is_check_correct,
            "response_time_seconds": round(response_time, 2),
            "question_type": check_q["question_type"],
            })

            st.session_state.final_comprehension_current += 1
            st.session_state.question_start_time = time.time()

            if st.session_state.final_comprehension_current >= len(final_comprehension_questions):
                st.session_state.screen = "post_experiment_survey"

            st.rerun()

# ==============================
# SCREEN: POST EXPERIMENT SURVEY
# ==============================

elif st.session_state.screen == "post_experiment_survey":

    st.markdown("""<div class="post-survey-card">
<div class="post-survey-title">Post-Experiment Survey</div>
<div class="post-survey-subtitle">
Please rate your feeling regarding each of the following questions.
<br>
Please move the scale between 1 and 7.
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="likert-banner">
<div class="likert-banner-main">Rating Scale</div>

<div class="likert-label-row">
<span>To a very great extent</span>
<span>To a very small extent</span>
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
            "Select a rating from 1 to 7",
            options=[1, 2, 3, 4, 5, 6, 7],
            value=4,
            key=f"post_survey_{survey_q['id']}",
            label_visibility="collapsed"
        )

    st.write("")

    if st.button("Finish and Submit Answers ▶", use_container_width=True):
        # The slider always has a value; the default is 4
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
        st.session_state.ended_at = db_israel_time()
        if not st.session_state.db_saved:
            session_ok, _ = save_session_to_db(total_duration)
            responses_ok, _ = save_responses_to_db()

            if session_ok and responses_ok:
                st.session_state.db_saved = True
            else:
                st.warning("Saving to the database was not completed, but the experiment has ended.")

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
    st.markdown('<div class="section-title">  The displayed information describes sales behavior in a clothing store 🛍️ ---> </div>', unsafe_allow_html=True)

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

    #if not st.session_state.filters_ready_for_tracking:
    #   st.session_state.filters_ready_for_tracking = True

    st.markdown(
        '<div class="dashboard-note">💡 Note! You can change your selection before clicking "Submit Answer".</div>',
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
                f'Please answer the following question:</div>',
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

            if st.button("Submit Answer ✨", key=f"middle_attention_submit_{attention_q['id']}", use_container_width=True):
                if attention_selected is None:
                    st.warning("Please select an answer before continuing")
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
                f'<div class="new-chart-badge">✨ {NEW_CHART_AT[cq]} — Please review the dashboard before answering</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="rtl-title" style="font-size:1.35rem;font-weight:700;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            f'Question {q["id"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="rtl-question" style="font-size:1.1rem;font-weight:600;margin-bottom:1rem;font-family:Varela Round, sans-serif;">'
            f'{q["text"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="rtl-label" style="font-weight:600;margin-bottom:0.4rem;font-family:Varela Round, sans-serif;">'
            'Select the best answer:</div>',
            unsafe_allow_html=True
        )

        selected = st.radio(
            "",
            q["options"],
            key=f"question_{q['id']}",
            label_visibility="collapsed",
            index=None
        )

        if st.button("Submit Answer ✨", use_container_width=True):

            if selected is None:
                st.warning("Please select an answer before continuing")
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
    st.session_state.ended_at = db_israel_time()

    export_df = build_export_df(total_duration)
    interactions_df = build_interactions_df()

    if not st.session_state.db_saved:
        session_ok, _ = save_session_to_db(total_duration)
        responses_ok, _ = save_responses_to_db()

        if session_ok and responses_ok:
            st.session_state.db_saved = True
        else:
            st.warning("Saving to the database was not completed, but you can still download the data as CSV.")

    st.balloons()
    st.markdown('<div class="big-title">📋 Performance Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">The experiment has ended — below are the session results</div>', unsafe_allow_html=True)

    x, y, z = st.columns(3)
    with x:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Total Time (seconds)</div>'
            f'<div class="metric-value">{round(total_duration, 2)}</div></div>',
            unsafe_allow_html=True
        )
    with y:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Total Interactions</div>'
            f'<div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>',
            unsafe_allow_html=True
        )
    with z:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Correct Answers</div>'
            f'<div class="metric-value">{st.session_state.correct_count} / {len(questions)}</div></div>',
            unsafe_allow_html=True
        )

    st.subheader("Response Summary")
    st.dataframe(export_df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        csv_results = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 Download Results CSV",
            data=csv_results,
            file_name=f"results_{st.session_state.participant_id}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        csv_interactions = interactions_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 Download Interaction Log",
            data=csv_interactions,
            file_name=f"interactions_{st.session_state.participant_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    btn1, btn2, btn3 = st.columns([1, 2, 1])
    with btn2:
        if st.button("✅ Finish", use_container_width=True):
            st.session_state.screen = "thankyou"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Restart 🔄", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ==============================
# SCREEN: THANK YOU
# ==============================
elif st.session_state.screen == "thankyou":

    final_redirect_url = (
        st.session_state.redirect_url
        if st.session_state.redirect_url
        else "https://app.prolific.com/submissions/complete?cc=TESTCODE"
    )

    st.markdown("""<div class="thankyou-card">
<div class="thankyou-emoji">🎉</div>
<div class="thankyou-title">Thank You for Participating!</div>
<div class="thankyou-sub">
Your participation contributes to important academic research in the field of business information systems.<br>
The results will be used for research purposes only.<br><br>
To register in the system that you completed the experiment, please click the finish button.
</div>
</div>""", unsafe_allow_html=True)

    col_l, col_btn, col_r = st.columns([2, 2, 2])

    with col_btn:
        st.markdown(
            f"""<form action="{final_redirect_url}" method="get" target="_self">
<input type="submit" value="Finish" style="
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
box-sizing:border-box;
">
</form>""",
            unsafe_allow_html=True
        )

