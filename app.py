import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import uuid
from supabase import create_client, Client

# ─────────────────────────────────────────
# Page config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ניסוי ניתוח נתונים",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# Supabase
# ─────────────────────────────────────────
supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ─────────────────────────────────────────
# Design tokens
# ─────────────────────────────────────────
BLUE   = "#4361EE"
TEAL   = "#06D6A0"
CORAL  = "#EF476F"
AMBER  = "#FFD166"
PURPLE = "#7B2D8B"
NAVY   = "#0D1B2A"
SLATE  = "#475569"
BORDER = "#E2E8F0"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif;
    color: {NAVY};
  }}
  .main {{ background: linear-gradient(160deg, #F0F4FF 0%, #E8F5F0 100%); }}
  .block-container {{ max-width: 1440px; padding: 1.8rem 2.6rem; }}

  /* ── Titles ── */
  .page-title {{
    font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em;
    background: linear-gradient(135deg, {BLUE}, {TEAL});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    direction: rtl; text-align: right; margin-bottom: 0.3rem;
  }}
  .page-sub {{
    font-size: 0.98rem; color: {SLATE};
    direction: rtl; text-align: right; margin-bottom: 1.5rem;
  }}

  /* ── Metric cards ── */
  .metric-card {{
    background: rgba(255,255,255,.94); border: 1px solid {BORDER};
    border-radius: 16px; padding: 16px 20px;
    box-shadow: 0 2px 14px -2px rgba(67,97,238,.09);
    transition: transform .18s ease;
  }}
  .metric-card:hover {{ transform: translateY(-2px); }}
  .metric-label {{
    font-size: .68rem; font-weight: 700; color: {SLATE};
    text-transform: uppercase; letter-spacing: .08em; margin-bottom: 4px;
  }}
  .metric-value {{ font-size: 1.42rem; font-weight: 800; color: {NAVY}; }}

  /* ── Section divider ── */
  .section-title {{
    font-size: 1.22rem; font-weight: 800; color: {NAVY};
    margin: 1.5rem 0 1rem 0; padding-right: 12px;
    border-right: 5px solid {BLUE}; direction: rtl; text-align: right;
  }}

  /* ── Chart card ── */
  .chart-card {{
    background: #fff; border: 1px solid {BORDER}; border-radius: 20px;
    padding: 20px 22px;
    box-shadow: 0 4px 20px -4px rgba(67,97,238,.08);
    height: 100%; animation: fadeUp .45s cubic-bezier(.16,1,.3,1);
  }}
  .chart-card-empty {{ border-radius: 20px; height: 100%; min-height: 430px; }}

  @keyframes fadeUp {{
    from {{ opacity:0; transform:translateY(12px); }}
    to   {{ opacity:1; transform:translateY(0); }}
  }}

  /* ── Chart title ── */
  .chart-title {{
    font-size: 1.18rem; font-weight: 700; color: {NAVY};
    margin-bottom: 0.6rem; direction: rtl; text-align: right;
  }}

  /* ── Story box ── */
  .story-box {{
    background: linear-gradient(135deg,#EEF2FF,#E0F7F1);
    border-right: 4px solid {BLUE}; border-radius: 12px;
    padding: 12px 16px; color: #1e3a8a;
    font-size: .93rem; line-height: 1.65;
    margin-bottom: 1rem; direction: rtl; text-align: right;
  }}

  /* ── New chart badge ── */
  .new-chart-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg,{TEAL},{BLUE});
    color: #fff; font-size: .82rem; font-weight: 700;
    padding: 5px 14px; border-radius: 20px; margin-bottom: .9rem;
    box-shadow: 0 2px 10px rgba(6,214,160,.35);
    animation: popIn .4s cubic-bezier(.34,1.56,.64,1); direction: rtl;
  }}
  @keyframes popIn {{
    from {{ opacity:0; transform:scale(.7); }}
    to   {{ opacity:1; transform:scale(1); }}
  }}

  /* ── Generic form / welcome card ── */
  .form-card {{
    background: #fff; border: 1px solid {BORDER}; border-radius: 20px;
    padding: 32px 36px;
    box-shadow: 0 4px 24px -4px rgba(67,97,238,.09);
    direction: rtl; text-align: right; max-width: 540px; margin: 0 auto;
  }}
  .form-title {{
    font-size: 1.12rem; font-weight: 700; color: {NAVY}; margin-bottom: 1.2rem;
    border-right: 4px solid {BLUE}; padding-right: 10px;
  }}

  .welcome-card {{
    background: #fff; border: 1px solid {BORDER}; border-radius: 24px;
    padding: 44px 52px; box-shadow: 0 8px 40px -8px rgba(67,97,238,.12);
    direction: rtl; text-align: right; max-width: 840px; margin: 0 auto;
  }}
  .welcome-title {{
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg,{BLUE},{TEAL});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: .3rem; text-align: center;
  }}
  .welcome-subtitle {{
    font-size: .9rem; color:#94a3b8; text-align:center; margin-bottom:1.8rem;
  }}
  .welcome-section-title {{
    font-size: .98rem; font-weight: 700; color:{NAVY};
    margin: 1.3rem 0 .4rem 0;
    border-right: 4px solid {BLUE}; padding-right: 10px;
  }}
  .welcome-text {{ font-size:.93rem; color:{SLATE}; line-height:1.85; }}
  .welcome-highlight {{
    background: linear-gradient(135deg,#EEF2FF,#E0F7F1);
    border-right: 4px solid {TEAL}; border-radius: 12px;
    padding: 13px 16px; color: #1e3a8a;
    font-size: .91rem; margin: 1.2rem 0; line-height: 1.75;
  }}
  .welcome-divider {{ border:none; border-top:1px solid {BORDER}; margin:1.6rem 0; }}

  /* ── Dashboard note ── */
  .dashboard-note {{
    background:#FFF7ED; color:#92400e;
    padding: 9px 16px; border-radius: 10px; font-size: .85rem;
    margin-top: 1rem; display: inline-block; direction: rtl;
  }}

  /* ── RTL helpers ── */
  .rtl-title, .rtl-question, .rtl-label {{ direction:rtl; text-align:right; }}

  /* ── Radio ── */
  div[data-testid="stRadio"] {{ direction:rtl; text-align:right; }}
  div[data-testid="stRadio"] > div {{ direction:rtl; align-items:flex-end; gap:7px; }}
  div[data-testid="stRadio"] label {{
    background:#F8FAFC; border:1.5px solid {BORDER}; border-radius:12px;
    padding:10px 16px !important; cursor:pointer; direction:rtl;
    text-align:right; justify-content:flex-end; flex-direction:row-reverse;
    transition:all .15s ease;
  }}
  div[data-testid="stRadio"] label:hover {{ border-color:{BLUE}; background:#EEF2FF; }}
  div[data-testid="stRadio"] label span,
  div[data-testid="stRadio"] p {{ direction:rtl; text-align:right; }}

  /* ── Buttons ── */
  div.stButton > button {{
    border-radius:12px; font-weight:700; padding:.55rem 1.8rem;
    background:#fff; color:{NAVY}; border:1.5px solid {BORDER};
    transition:all .15s ease;
  }}
  div.stButton > button:hover {{
    border-color:{BLUE}; color:{BLUE};
    box-shadow:0 4px 12px rgba(67,97,238,.15);
  }}
  .btn-primary > div > button {{
    background: linear-gradient(135deg,{BLUE},{TEAL}) !important;
    color:#fff !important; border:none !important;
    box-shadow:0 4px 14px rgba(67,97,238,.3) !important;
  }}
  .btn-primary > div > button:hover {{
    opacity:.9 !important; box-shadow:0 6px 18px rgba(67,97,238,.4) !important;
  }}

  /* ── Selectbox ── */
  div[data-baseweb="select"] > div {{ border-radius:12px; border:1.5px solid {BORDER}; }}

  /* ── Thank-you ── */
  .thankyou-card {{
    background:#fff; border:1px solid {BORDER}; border-radius:24px;
    padding:60px 48px; box-shadow:0 8px 40px -8px rgba(67,97,238,.12);
    text-align:center; max-width:620px; margin:3rem auto;
    animation:fadeUp .6s ease; direction:rtl;
  }}
  .thankyou-emoji {{ font-size:4rem; margin-bottom:1rem; }}
  .thankyou-title {{ font-size:2rem; font-weight:800; color:{NAVY}; margin-bottom:.7rem; }}
  .thankyou-sub   {{ font-size:1rem; color:{SLATE}; line-height:1.8; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Data
# ─────────────────────────────────────────
df = pd.read_csv("data.csv")
df["Date"] = pd.to_datetime(df["Date"])
months_order = list(df["Month"].drop_duplicates())

monthly_total = (
    df.groupby("Month", as_index=False)
      .agg(**{"Revenue Total":("Revenue","sum"), "Profit Total":("Profit","sum")})
)
monthly_total["Month"] = pd.Categorical(monthly_total["Month"], categories=months_order, ordered=True)
monthly_total = monthly_total.sort_values("Month")

monthly_category = (
    df.groupby(["Month","Category"], as_index=False)
      .agg(Revenue=("Revenue","sum"), Profit=("Profit","sum"))
)
monthly_category["Month"] = pd.Categorical(monthly_category["Month"], categories=months_order, ordered=True)
monthly_category = monthly_category.sort_values(["Month","Category"])

monthly_dress = (
    df[df["Category"]=="Dress"]
      .groupby("Month", as_index=False)
      .agg(**{"Discount Dress":("Discount","mean"), "Profit Dress":("Profit","sum")})
)
monthly_dress["Month"] = pd.Categorical(monthly_dress["Month"], categories=months_order, ordered=True)
monthly_dress = monthly_dress.sort_values("Month")

# ─────────────────────────────────────────
# Questions
# ─────────────────────────────────────────
questions = [
    {"id":1,
     "text":"מהי המגמה הכללית של ההכנסות הכוללות לאורך התקופה?",
     "options":["ירידה","יציבות עם עלייה קלה","ירידה חדה","לא ניתן לדעת"],
     "correct_answer":"יציבות עם עלייה קלה"},
    {"id":2,
     "text":"האם בחודש האחרון נרשמה עלייה בהכנסות ביחס לחודש הקודם?",
     "options":["כן","לא","אין שינוי","לא ניתן לדעת"],
     "correct_answer":"כן"},
    {"id":3,
     "text":"מהי המגמה הכללית של הרווח הכולל לאורך התקופה?",
     "options":["עלייה","יציבות","ירידה","לא ניתן לדעת"],
     "correct_answer":"ירידה"},
    {"id":4,
     "text":"האם ניתן להסביר בוודאות את הירידה ברווח רק על בסיס שני הגרפים הראשונים?",
     "options":["כן","לא","כן, בגלל ירידה במכירות","כן, בגלל עלייה בעלויות"],
     "correct_answer":"לא"},
    {"id":5,
     "text":"איזו קטגוריה מייצרת את ההכנסות הגבוהות ביותר לאורך רוב התקופה?",
     "options":["T-shirt","Dress","Jeans","כל הקטגוריות שוות"],
     "correct_answer":"Dress"},
    {"id":6,
     "text":"האם גרף הקטגוריות יכול לסייע להסביר את הפער בין הכנסות לרווח?",
     "options":["כן","לא","רק באופן חלקי","לא ניתן לדעת"],
     "correct_answer":"רק באופן חלקי"},
    {"id":7,
     "text":"איזו קטגוריה נראית כמועמדת מרכזית לבדיקה מעמיקה יותר?",
     "options":["T-shirt","Dress","Jeans","אי אפשר לדעת"],
     "correct_answer":"Dress"},
    {"id":8,
     "text":"מה הקשר הנראה בין שיעור ההנחה על Dress לבין הרווח בקטגוריה זו?",
     "options":["ככל שההנחה עולה, הרווח עולה","ככל שההנחה עולה, הרווח יורד",
                "אין קשר נראה לעין","לא ניתן לדעת"],
     "correct_answer":"ככל שההנחה עולה, הרווח יורד"},
    {"id":9,
     "text":"מהו ההסבר הסביר ביותר לירידה ברווח הכולל?",
     "options":["ירידה בהכנסות הכוללות","ירידה במכירות של כל הקטגוריות",
                "גידול במכירות ב-Dress לצד הנחות גבוהות שפוגעות ברווחיות",
                "עלייה ברווח של Dress"],
     "correct_answer":"גידול במכירות ב-Dress לצד הנחות גבוהות שפוגעות ברווחיות"},
    {"id":10,
     "text":"מהי המסקנה העסקית המרכזית מהנתונים?",
     "options":["יש להמשיך להגדיל הנחות בכל הקטגוריות",
                "עלייה במכירות תמיד משפרת ביצועים עסקיים",
                "הגידול במכירות אינו מתורגם בהכרח לשיפור עסקי כאשר הרווחיות נשחקת",
                "אין בעיה עסקית נראית לעין"],
     "correct_answer":"הגידול במכירות אינו מתורגם בהכרח לשיפור עסקי כאשר הרווחיות נשחקת"},
]

# ─────────────────────────────────────────
# Narratives — connected story (req #8)
# ─────────────────────────────────────────
chart_narratives = {
    "chart1": (
        "📈 נתחיל מהתמונה הכוללת: ההכנסות החודשיות של החברה מראות יציבות עם נטייה לעלייה. "
        "לחצו על 🔍 כדי לצלול לרמת היום ולאמת את המגמה."
    ),
    "chart2": (
        "💰 אבל כשבוחנים את הרווח — הסיפור שונה לחלוטין. בעוד ההכנסות עולות, "
        "הרווח דווקא יורד. מה גורם לפער הזה? לחצו 🔍 לניתוח מעמיק."
    ),
    "chart3": (
        "🏷️ הפילוח לפי קטגוריה מתחיל לחשוף את התשובה: Dress מובילה בהכנסות — "
        "אך האם היא גם מובילה ברווחיות? בחרו קטגוריה ולחצו 🔍 לבדיקה."
    ),
    "chart4": (
        "📉 הנה השורה התחתונה: ב-Dress, ככל שההנחות עולות — הרווח נשחק. "
        "הגידול במכירות בא במחיר. לחצו 🔍 לראות את הדינמיקה הזו ברמת יום."
    ),
}

# Questions at which a new chart is revealed (storytelling, 0-based)
NEW_CHART_AT = {2: "גרף 2 נוסף", 4: "גרף 3 נוסף", 7: "גרף 4 נוסף"}

# Test participant
TEST_ID = "999"

# ─────────────────────────────────────────
# Session state
# ─────────────────────────────────────────
defaults = {
    "screen": "register",   # register | demographic | consent | experiment | summary | thankyou
    "experiment_started": False,
    "participant_id": "",
    "experiment_group": "",
    "session_id": str(uuid.uuid4()),
    "session_start_time": None,   # set only on consent click
    "question_start_time": None,
    "total_duration": None,
    "current_question": 0,
    "answers": [],
    "correct_count": 0,
    "dashboard_interaction_clicks": 0,
    "interaction_log": [],
    "db_saved": False,
    # demographic
    "demo_gender": "", "demo_age": "", "demo_faculty": "", "demo_bi_exp": "",
    # chart state
    "chart1_drilled": False, "chart1_month": months_order[0],
    "chart2_drilled": False, "chart2_month": months_order[0],
    "chart3_drilled": False, "chart3_category": "Dress",
    "chart4_drilled": False, "chart4_month": months_order[0],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

widget_defaults = {
    "chart1_month_select": months_order[0],
    "chart2_month_select": months_order[0],
    "chart3_category_select": "Dress",
    "chart4_month_select": months_order[0],
}
for k, v in widget_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

prev_defaults = {
    "__prev_chart1_month_select": months_order[0],
    "__prev_chart2_month_select": months_order[0],
    "__prev_chart3_category_select": "Dress",
    "__prev_chart4_month_select": months_order[0],
}
for k, v in prev_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def is_test():
    return st.session_state.participant_id == TEST_ID


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
        "action_value": action_value,
    })


def track_filter_change(widget_key: str, action_type: str):
    cur = st.session_state.get(widget_key)
    prev_key = f"__prev_{widget_key}"
    prev = st.session_state.get(prev_key)
    if cur != prev:
        track_dashboard_click(action_type, f"{widget_key}={cur}")
        st.session_state[prev_key] = cur


def build_export_df(total_duration: float) -> pd.DataFrame:
    summary = {
        "participant_id": st.session_state.participant_id,
        "experiment_group": st.session_state.experiment_group,
        "session_id": st.session_state.session_id,
        "total_duration_seconds": round(total_duration, 2),
        "dashboard_interaction_clicks": st.session_state.dashboard_interaction_clicks,
        "correct_answers_count": st.session_state.correct_count,
        "total_questions": len(questions),
        "gender": st.session_state.demo_gender,
        "age_group": st.session_state.demo_age,
        "faculty": st.session_state.demo_faculty,
        "bi_experience": st.session_state.demo_bi_exp,
    }
    rows = []
    for a in st.session_state.answers:
        row = {}; row.update(summary); row.update(a)
        rows.append(row)
    return pd.DataFrame(rows)


def build_interactions_df() -> pd.DataFrame:
    if not st.session_state.interaction_log:
        return pd.DataFrame(columns=[
            "session_id","participant_id","experiment_group",
            "timestamp","question_index_at_time","action_type","action_value",
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
        res = supabase.table("sessions").upsert(data, on_conflict="session_id").execute()
        return True, res
    except Exception as e:
        st.error("שגיאה בשמירת session")
        st.code(str(e))
        return False, None


def save_responses_to_db():
    rows = [{
        "session_id": str(st.session_state.session_id),
        "participant_id": str(st.session_state.participant_id),
        "experiment_group": str(st.session_state.experiment_group),
        "question_id": int(a["question_id"]),
        "question_text": str(a["question_text"]) if a.get("question_text") else None,
        "selected_answer": str(a["selected_answer"]) if a.get("selected_answer") else None,
        "correct_answer": str(a["correct_answer"]) if a.get("correct_answer") else None,
        "is_correct": bool(a["is_correct"]) if a.get("is_correct") is not None else None,
        "response_time_seconds": float(a["response_time_seconds"]) if a.get("response_time_seconds") is not None else None,
    } for a in st.session_state.answers]
    if not rows:
        return True, None
    try:
        res = supabase.table("responses").insert(rows).execute()
        return True, res
    except Exception as e:
        st.error("שגיאה בשמירת responses")
        st.code(str(e))
        return False, None


# ─────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────
def month_daily_totals(month_name):
    d = df[df["Month"]==month_name].groupby(["Day"],as_index=False).agg(
        Revenue=("Revenue","sum"), Profit=("Profit","sum"))
    return d.sort_values("Day")


def dress_month_daily(month_name):
    d = df[(df["Month"]==month_name)&(df["Category"]=="Dress")].sort_values("Day")
    return d[["Day","Profit","Discount"]].copy()


def category_monthly_totals(cat):
    d = (df[df["Category"]==cat]
         .groupby("Month",as_index=False)
         .agg(Revenue=("Revenue","sum"), Profit=("Profit","sum")))
    d["Month"] = pd.Categorical(d["Month"],categories=months_order,ordered=True)
    return d.sort_values("Month")


# ─────────────────────────────────────────
# Chart layout
# ─────────────────────────────────────────
def apply_chart_layout(fig, title_text: str, secondary_pct: bool = False):
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=14,color=SLATE,family="Outfit,sans-serif")),
        template=None,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        margin=dict(l=14,r=14,t=54,b=14),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,
                    font=dict(size=12,family="Outfit,sans-serif"),
                    bgcolor="rgba(255,255,255,0)"),
        font=dict(family="Outfit,sans-serif",color=SLATE),
        hoverlabel=dict(bgcolor="#fff",bordercolor=BORDER,
                        font=dict(family="Outfit,sans-serif",size=13)),
    )
    fig.update_xaxes(showgrid=False,zeroline=False,linecolor=BORDER,tickfont=dict(size=12))
    fig.update_yaxes(showgrid=True,gridcolor="#EEF2FF",zeroline=False,
                     linecolor=BORDER,tickfont=dict(size=12),tickprefix="$")
    return fig


def panel_header(title: str, narrative: str):
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    if st.session_state.experiment_group == "storytelling":
        st.markdown(f'<div class="story-box">{narrative}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
# Chart renderers
# ─────────────────────────────────────────
def show_chart1():
    panel_header("גרף 1 — מגמת הכנסות", chart_narratives["chart1"])
    if not st.session_state.chart1_drilled:
        fig = px.area(monthly_total, x="Month", y="Revenue Total",
                      color_discrete_sequence=[BLUE], markers=True)
        fig.update_traces(fill="tozeroy", fillcolor="rgba(67,97,238,.10)",
                          line=dict(width=2.5,color=BLUE),
                          marker=dict(size=7,color=BLUE,line=dict(width=2,color="#fff")))
        apply_chart_layout(fig, "הכנסות כוללות לפי חודש ($)")
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns([2.2,1])
        with c1:
            st.selectbox("בחר/י חודש לפירוט:", months_order, key="chart1_month_select",
                         on_change=track_filter_change,
                         args=("chart1_month_select","chart1_filter_month_change"))
        with c2:
            st.write("")
            if st.button("🔍 Drill Down", key="chart1_drill_btn", use_container_width=True):
                st.session_state.chart1_month = st.session_state.chart1_month_select
                st.session_state.chart1_drilled = True
                track_dashboard_click("chart1_drill_down", st.session_state.chart1_month)
                st.rerun()
    else:
        d = month_daily_totals(st.session_state.chart1_month)
        fig = px.bar(d, x="Day", y="Revenue", color_discrete_sequence=[BLUE])
        fig.update_traces(marker_color=BLUE, marker_opacity=0.82, marker_line_width=0)
        apply_chart_layout(fig, f"הכנסות יומיות — {st.session_state.chart1_month} ($)")
        st.plotly_chart(fig, use_container_width=True)
        if st.button("⬅️ חזרה", key="chart1_back_btn", use_container_width=True):
            st.session_state.chart1_drilled = False
            track_dashboard_click("chart1_back", st.session_state.chart1_month)
            st.rerun()


def show_chart2():
    panel_header("גרף 2 — מגמת רווח", chart_narratives["chart2"])
    if not st.session_state.chart2_drilled:
        fig = px.area(monthly_total, x="Month", y="Profit Total",
                      color_discrete_sequence=[TEAL], markers=True)
        fig.update_traces(fill="tozeroy", fillcolor="rgba(6,214,160,.10)",
                          line=dict(width=2.5,color=TEAL),
                          marker=dict(size=7,color=TEAL,line=dict(width=2,color="#fff")))
        apply_chart_layout(fig, "רווח כולל לפי חודש ($)")
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns([2.2,1])
        with c1:
            st.selectbox("בחר/י חודש לפירוט:", months_order, key="chart2_month_select",
                         on_change=track_filter_change,
                         args=("chart2_month_select","chart2_filter_month_change"))
        with c2:
            st.write("")
            if st.button("🔍 Drill Down", key="chart2_drill_btn", use_container_width=True):
                st.session_state.chart2_month = st.session_state.chart2_month_select
                st.session_state.chart2_drilled = True
                track_dashboard_click("chart2_drill_down", st.session_state.chart2_month)
                st.rerun()
    else:
        d = month_daily_totals(st.session_state.chart2_month)
        fig = px.bar(d, x="Day", y="Profit", color_discrete_sequence=[TEAL])
        fig.update_traces(marker_color=TEAL, marker_opacity=0.82, marker_line_width=0)
        apply_chart_layout(fig, f"רווח יומי — {st.session_state.chart2_month} ($)")
        st.plotly_chart(fig, use_container_width=True)
        if st.button("⬅️ חזרה", key="chart2_back_btn", use_container_width=True):
            st.session_state.chart2_drilled = False
            track_dashboard_click("chart2_back", st.session_state.chart2_month)
            st.rerun()


def show_chart3():
    panel_header("גרף 3 — הכנסות לפי קטגוריה", chart_narratives["chart3"])
    CAT_COLORS = {"T-shirt": BLUE, "Dress": CORAL, "Jeans": PURPLE}
    if not st.session_state.chart3_drilled:
        fig = px.line(monthly_category, x="Month", y="Revenue", color="Category",
                      markers=True, color_discrete_map=CAT_COLORS)
        fig.update_traces(line_width=2.5,
                          marker=dict(size=7,line=dict(width=2,color="#fff")))
        apply_chart_layout(fig, "הכנסות לפי קטגוריה ($)")
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns([2.2,1])
        with c1:
            st.selectbox("קטגוריה:", ["T-shirt","Dress","Jeans"],
                         key="chart3_category_select",
                         on_change=track_filter_change,
                         args=("chart3_category_select","chart3_filter_category_change"))
        with c2:
            st.write("")
            if st.button("🔍 הכנסות מול רווח", key="chart3_drill_btn", use_container_width=True):
                st.session_state.chart3_category = st.session_state.chart3_category_select
                st.session_state.chart3_drilled = True
                track_dashboard_click("chart3_drill_down", st.session_state.chart3_category)
                st.rerun()
    else:
        d = category_monthly_totals(st.session_state.chart3_category)
        ml = d["Month"].astype(str).tolist()
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=ml, y=d["Revenue"], name="Revenue ($)",
                             marker_color=BLUE, opacity=0.85, marker_line_width=0),
                      secondary_y=False)
        fig.add_trace(go.Scatter(x=ml, y=d["Profit"], mode="lines+markers",
                                 name="Profit ($)", line=dict(color=TEAL,width=2.5),
                                 marker=dict(size=7,color=TEAL,line=dict(width=2,color="#fff"))),
                      secondary_y=True)
        fig.update_yaxes(title_text="Revenue ($)", secondary_y=False,
                         showgrid=True, gridcolor="#EEF2FF", tickprefix="$")
        fig.update_yaxes(title_text="Profit ($)", secondary_y=True,
                         showgrid=False, tickprefix="$")
        apply_chart_layout(fig, f"{st.session_state.chart3_category} — הכנסות מול רווח ($)")
        st.plotly_chart(fig, use_container_width=True)
        if st.button("⬅️ חזרה", key="chart3_back_btn", use_container_width=True):
            st.session_state.chart3_drilled = False
            track_dashboard_click("chart3_back", st.session_state.chart3_category)
            st.rerun()


def show_chart4():
    panel_header("גרף 4 — הנחה ורווח ב-Dress", chart_narratives["chart4"])
    if not st.session_state.chart4_drilled:
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=monthly_dress["Month"], y=monthly_dress["Profit Dress"],
                             name="Profit ($)", marker_color=PURPLE,
                             opacity=0.85, marker_line_width=0),
                      secondary_y=False)
        fig.add_trace(go.Scatter(x=monthly_dress["Month"], y=monthly_dress["Discount Dress"],
                                 mode="lines+markers", name="Discount %",
                                 line=dict(color=AMBER,width=2.5),
                                 marker=dict(size=7,color=AMBER,line=dict(width=2,color="#fff"))),
                      secondary_y=True)
        fig.update_yaxes(title_text="Profit ($)", secondary_y=False,
                         showgrid=True, gridcolor="#EEF2FF", tickprefix="$")
        fig.update_yaxes(title_text="Discount (%)", secondary_y=True,
                         showgrid=False, ticksuffix="%")
        apply_chart_layout(fig, "Dress — הנחה מול רווח ($)")
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns([2.2,1])
        with c1:
            st.selectbox("בחר/י חודש לפירוט:", months_order, key="chart4_month_select",
                         on_change=track_filter_change,
                         args=("chart4_month_select","chart4_filter_month_change"))
        with c2:
            st.write("")
            if st.button("🔍 Drill Down", key="chart4_drill_btn", use_container_width=True):
                st.session_state.chart4_month = st.session_state.chart4_month_select
                st.session_state.chart4_drilled = True
                track_dashboard_click("chart4_drill_down", st.session_state.chart4_month)
                st.rerun()
    else:
        d = dress_month_daily(st.session_state.chart4_month)
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=d["Day"], y=d["Profit"], name="Profit ($)",
                             marker_color=PURPLE, opacity=0.85, marker_line_width=0),
                      secondary_y=False)
        fig.add_trace(go.Scatter(x=d["Day"], y=d["Discount"], mode="lines+markers",
                                 name="Discount %", line=dict(color=AMBER,width=2),
                                 marker=dict(size=6,color=AMBER,line=dict(width=2,color="#fff"))),
                      secondary_y=True)
        fig.update_yaxes(title_text="Profit ($)", secondary_y=False,
                         showgrid=True, gridcolor="#EEF2FF", tickprefix="$")
        fig.update_yaxes(title_text="Discount (%)", secondary_y=True,
                         showgrid=False, ticksuffix="%")
        apply_chart_layout(fig, f"Dress — נתונים יומיים ({st.session_state.chart4_month})")
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


# ══════════════════════════════════════════
# SCREEN 1 — REGISTER
# ══════════════════════════════════════════
if st.session_state.screen == "register":
    st.markdown("<div style='max-width:480px;margin:4rem auto 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="form-card"><div class="form-title">כניסה לניסוי</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([0.5, 3, 0.5])
    with col:
        pid = st.text_input("מספר משתתף", placeholder="הזינו את המספר שקיבלתם")
        grp = st.selectbox("קבוצת ניסוי", ["control", "storytelling"])
        st.write("")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("המשך ▶", use_container_width=True, key="reg_next"):
            if pid.strip() == "":
                st.warning("יש להזין מספר משתתף.")
            else:
                st.session_state.participant_id = pid.strip()
                st.session_state.experiment_group = grp
                st.session_state.screen = "demographic"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# SCREEN 2 — DEMOGRAPHIC
# ══════════════════════════════════════════
elif st.session_state.screen == "demographic":
    st.markdown("<div style='max-width:540px;margin:3rem auto 0;'>", unsafe_allow_html=True)
    st.markdown("""
        <div class="form-card">
          <div class="form-title">שאלון דמוגרפי</div>
          <div style="font-size:.88rem;color:#64748b;margin-bottom:1rem;">
            המידע נאסף לצרכי מחקר בלבד ואינו מזהה אתכם אישית.
          </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([0.3, 3, 0.3])
    with col:
        gender = st.radio("מגדר",
                          ["זכר", "נקבה", "אחר / מעדיף/ת שלא לציין"],
                          key="demo_gender_w")
        age = st.selectbox("גיל",
                           ["מתחת ל-20", "20–24", "25–29", "30–34", "35+"],
                           key="demo_age_w")
        faculty = st.selectbox("פקולטה / מחלקה",
                               ["הנדסת תעשייה וניהול", "מדעי המחשב", "מנהל עסקים",
                                "מדעים מדויקים", "אחר"],
                               key="demo_fac_w")
        bi_exp = st.radio("ניסיון קודם עם דשבורדים / מערכות BI?",
                          ["כן, ניסיון רב", "כן, ניסיון מועט", "לא"],
                          key="demo_bi_w")
        st.write("")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("המשך ▶", use_container_width=True, key="demo_next"):
            st.session_state.demo_gender  = gender
            st.session_state.demo_age     = age
            st.session_state.demo_faculty = faculty
            st.session_state.demo_bi_exp  = bi_exp
            st.session_state.screen = "consent"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# SCREEN 3 — CONSENT / WELCOME
# ══════════════════════════════════════════
elif st.session_state.screen == "consent":
    st.markdown("""
        <div style="max-width:840px;margin:2rem auto;">
          <div class="welcome-card">
            <div class="welcome-title">📊 ברוכים הבאים לניסוי</div>
            <div class="welcome-subtitle">
              פרויקט גמר — המחלקה להנדסת תעשייה וניהול, אוניברסיטת בן-גוריון תשפ"ו
            </div>
            <hr class="welcome-divider">

            <div class="welcome-section-title">מהו הניסוי?</div>
            <div class="welcome-text">
              ניסוי זה בוחן כיצד אופן הצגת מידע בדשבורדים עסקיים משפיע על איכות קבלת ההחלטות
              ועל רמת המעורבות של המשתמש. תוצגו בפניכם ויזואליזציות נתונים עסקיים ותתבקשו
              לנתח אותן ולענות על 10 שאלות.
            </div>

            <div class="welcome-section-title">כיצד לחקור את הגרפים? 🔍</div>
            <div class="welcome-text">
              בכל גרף תמצאו כפתור <strong>🔍 Drill Down</strong>. לחיצה עליו מעבירה אתכם
              מתצוגה <em>חודשית</em> לתצוגה <em>יומית</em> מפורטת — כך תוכלו להסתכל פנימה
              ולחקור את הנתונים לעומק. לחיצה על <strong>⬅️ חזרה</strong> תחזיר אתכם לתצוגה הכוללת.<br>
              <strong>מומלץ</strong> להשתמש ב-Drill Down לפני שמשיבים על שאלות שדורשות הסתכלות פנימה.
            </div>

            <div class="welcome-section-title">מה עלי לעשות?</div>
            <div class="welcome-text">
              יש לעיין בדשבורד ולענות על <strong>10 שאלות</strong>. לאחר שליחת תשובה לא ניתן לחזור.
              לא יינתן משוב לגבי נכונות התשובה בזמן אמת.
            </div>

            <div class="welcome-section-title">משך הניסוי</div>
            <div class="welcome-text">כ-<strong>15 דקות</strong>. אין הגבלת זמן לשאלה בנפרד.</div>

            <div class="welcome-section-title">תמריצים</div>
            <div class="welcome-text">
              נקודת בונוס בקורס BI. בנוסף, פרס כספי:
              פחות מ-3 נכונות — ללא פרס | 4–6 — 15 ₪ | 7–8 — 25 ₪ | 9–10 — 40 ₪
              <em>(בכפוף לאישור)</em>.
            </div>

            <div class="welcome-highlight">
              🔒 <strong>פרטיות:</strong> ההשתתפות אנונימית לחלוטין. הנתונים ישמשו למחקר בלבד.<br><br>
              ✋ <strong>הסכמה:</strong> לחיצה על "התחל" מהווה הסכמה מרצון. ניתן לעצור בכל עת,
              אך עצירה לפני השלמה לא תזכה בבונוס.
            </div>

            <hr class="welcome-divider">
          </div>
        </div>
    """, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([2, 2, 2])
    with btn_col:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        # ← Timer starts ONLY here, on explicit consent click
        if st.button("התחל ניסוי 🚀", use_container_width=True, key="consent_start"):
            st.session_state.session_start_time  = time.time()
            st.session_state.question_start_time = time.time()
            st.session_state.experiment_started  = True
            st.session_state.db_saved = False
            st.session_state.screen = "experiment"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
# SCREEN 4 — EXPERIMENT
# ══════════════════════════════════════════
elif st.session_state.screen == "experiment":
    st.markdown('<div class="page-title">Business Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Decision support & performance analysis</div>', unsafe_allow_html=True)

    # ── Metric bar — only for test participant ──
    if is_test():
        a, b, c, d = st.columns(4)
        with a:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Participant ID</div>'
                f'<div class="metric-value">{st.session_state.participant_id}</div></div>',
                unsafe_allow_html=True)
        with b:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Group</div>'
                f'<div class="metric-value">{st.session_state.experiment_group.capitalize()}</div></div>',
                unsafe_allow_html=True)
        with c:
            cq_disp = min(st.session_state.current_question + 1, len(questions))
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Progress</div>'
                f'<div class="metric-value">{cq_disp}'
                f'<span style="font-size:1rem;color:#94a3b8"> / {len(questions)}</span></div></div>',
                unsafe_allow_html=True)
        with d:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Interactions</div>'
                f'<div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>',
                unsafe_allow_html=True)

    # ── Reveal logic ──
    is_storytelling = (st.session_state.experiment_group == "storytelling")
    cq = st.session_state.current_question

    show_fig2 = True if not is_storytelling else cq >= 2
    show_fig3 = True if not is_storytelling else cq >= 4
    show_fig4 = True if not is_storytelling else cq >= 7

    # ── Dashboard grid ──
    st.markdown('<div class="section-title">דשבורד אינטראקטיבי</div>', unsafe_allow_html=True)

    tl, tr = st.columns(2)
    bl, br = st.columns(2)
    with tl: show_or_empty(True,      show_chart1)
    with tr: show_or_empty(show_fig2, show_chart2)
    with bl: show_or_empty(show_fig3, show_chart3)
    with br: show_or_empty(show_fig4, show_chart4)

    st.markdown(
        '<div class="dashboard-note">💡 ניתן לשנות את הבחירה לפני לחיצה על "שלח/י תשובה"</div>',
        unsafe_allow_html=True)

    st.divider()

    # ── Question block ──
    if cq < len(questions):
        q = questions[cq]

        if is_storytelling and cq in NEW_CHART_AT:
            st.markdown(
                f'<div class="new-chart-badge">✨ {NEW_CHART_AT[cq]} — עיינו בדשבורד לפני המענה</div>',
                unsafe_allow_html=True)

        st.markdown(
            f'<div class="rtl-title" style="font-size:1.28rem;font-weight:700;margin-bottom:.4rem;">'
            f'שאלה {q["id"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="rtl-question" style="font-size:1.07rem;font-weight:600;margin-bottom:.9rem;">'
            f'{q["text"]}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="rtl-label" style="font-weight:600;margin-bottom:.4rem;">'
            'בחר/י את התשובה הנכונה ביותר:</div>', unsafe_allow_html=True)

        selected = st.radio("", q["options"], key=f"question_{q['id']}",
                            label_visibility="collapsed")

        if st.button("שלח/י תשובה ✅", use_container_width=True):
            rt = time.time() - st.session_state.question_start_time
            is_correct = selected == q["correct_answer"]
            st.session_state.answers.append({
                "question_id": q["id"],
                "question_text": q["text"],
                "selected_answer": selected,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct,
                "response_time_seconds": round(rt, 2),
            })
            if is_correct:
                st.session_state.correct_count += 1
            st.session_state.current_question += 1
            st.session_state.question_start_time = time.time()
            st.rerun()

    else:
        # All questions done → lock the timer
        if st.session_state.session_start_time and st.session_state.total_duration is None:
            st.session_state.total_duration = time.time() - st.session_state.session_start_time

        # Test mode → full summary; everyone else → thank-you
        st.session_state.screen = "summary" if is_test() else "thankyou"
        st.rerun()


# ══════════════════════════════════════════
# SCREEN 5 — SUMMARY  (test / ID=999 only)
# ══════════════════════════════════════════
elif st.session_state.screen == "summary":
    total_duration = st.session_state.total_duration or 0.0
    export_df = build_export_df(total_duration)
    interactions_df = build_interactions_df()

    if not st.session_state.db_saved:
        s_ok, _ = save_session_to_db(total_duration)
        r_ok, _ = save_responses_to_db()
        if s_ok and r_ok:
            st.session_state.db_saved = True
        else:
            st.warning("השמירה למסד לא הושלמה — אפשר להוריד CSV.")

    st.balloons()
    st.markdown('<div class="page-title">📋 סיכום ביצועים</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">הניסוי הסתיים — להלן תוצאות הסשן</div>', unsafe_allow_html=True)

    x, y, z = st.columns(3)
    with x:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">זמן כולל (שניות)</div>'
            f'<div class="metric-value">{round(total_duration,1)}</div></div>',
            unsafe_allow_html=True)
    with y:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">סה״כ אינטראקציות</div>'
            f'<div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>',
            unsafe_allow_html=True)
    with z:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">תשובות נכונות</div>'
            f'<div class="metric-value">{st.session_state.correct_count} / {len(questions)}</div></div>',
            unsafe_allow_html=True)

    st.subheader("סיכום תשובות")
    st.dataframe(export_df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 הורדת תוצאות CSV",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"results_{st.session_state.participant_id}.csv",
            mime="text/csv", use_container_width=True)
    with c2:
        st.download_button("📥 הורדת לוג אינטראקציות",
            data=interactions_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"interactions_{st.session_state.participant_id}.csv",
            mime="text/csv", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, bc, _ = st.columns([1,2,1])
    with bc:
        if st.button("✅ לחץ לסיום", use_container_width=True):
            st.session_state.screen = "thankyou"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("התחל מחדש 🔄", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ══════════════════════════════════════════
# SCREEN 6 — THANK YOU
# ══════════════════════════════════════════
elif st.session_state.screen == "thankyou":
    total_duration = st.session_state.total_duration or 0.0
    if not st.session_state.db_saved:
        save_session_to_db(total_duration)
        save_responses_to_db()
        st.session_state.db_saved = True

    st.markdown("""
        <div class="thankyou-card">
            <div class="thankyou-emoji">🎉</div>
            <div class="thankyou-title">תודה רבה על השתתפותך!</div>
            <div class="thankyou-sub">
                השתתפותך תורמת למחקר אקדמי חשוב בתחום מערכות מידע עסקיות.<br>
                התוצאות ישמשו לבחינת ההשפעה של נרטיבים מבוססי AI על קבלת החלטות.<br><br>
                ניתן לסגור את הדפדפן.
            </div>
        </div>
    """, unsafe_allow_html=True)

    _, cb, _ = st.columns([2,2,2])
    with cb:
        if st.button("התחל מחדש 🔄", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()