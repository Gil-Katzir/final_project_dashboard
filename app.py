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
    page_title="Final Project Dashboard",
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
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

.main {
    background: linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%);
}

.block-container {
    max-width: 1450px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

.big-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #18212f;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}

.sub-title {
    font-size: 1rem;
    color: #667085;
    margin-bottom: 1.4rem;
}

.metric-card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid #e6ebf2;
    border-radius: 20px;
    padding: 16px 18px;
    box-shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
    backdrop-filter: blur(4px);
}

.metric-label {
    color: #667085;
    font-size: 0.85rem;
    margin-bottom: 0.3rem;
}

.metric-value {
    color: #111827;
    font-size: 1.35rem;
    font-weight: 800;
}

.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #18212f;
    margin-top: 1.3rem;
    margin-bottom: 0.8rem;
}

.chart-card {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid #e6ebf2;
    border-radius: 22px;
    padding: 14px 14px 8px 14px;
    box-shadow: 0 10px 28px rgba(16, 24, 40, 0.06);
    min-height: 100%;
}

.chart-title {
    font-size: 1.02rem;
    font-weight: 800;
    color: #18212f;
    margin-bottom: 0.35rem;
}

.story-box {
    background: #eef4ff;
    border: 1px solid #d8e4ff;
    border-radius: 14px;
    padding: 10px 12px;
    color: #2c4a7a;
    font-size: 0.95rem;
    margin-bottom: 0.9rem;
}

.empty-panel {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border: 1px dashed #d7deea;
    border-radius: 20px;
    min-height: 430px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #98a2b3;
    text-align: center;
    padding: 20px;
}

.dashboard-note {
    color: #667085;
    font-size: 0.9rem;
    margin-top: 0.6rem;
}

div[data-testid="stPlotlyChart"] {
    border-radius: 18px;
    overflow: hidden;
}

div[data-testid="stRadio"] label {
    background: white;
    border: 1px solid #e7ecf3;
    border-radius: 12px;
    padding: 8px 10px;
    margin-bottom: 8px;
}

div.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    min-height: 42px;
}

div[data-baseweb="select"] > div {
    border-radius: 12px;
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
    .agg(
        **{
            "Revenue Total": ("Revenue", "sum"),
            "Profit Total": ("Profit", "sum")
        }
    )
)
monthly_total["Month"] = pd.Categorical(
    monthly_total["Month"],
    categories=months_order,
    ordered=True
)
monthly_total = monthly_total.sort_values("Month")

monthly_category = (
    df.groupby(["Month", "Category"], as_index=False)
    .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
)
monthly_category["Month"] = pd.Categorical(
    monthly_category["Month"],
    categories=months_order,
    ordered=True
)
monthly_category = monthly_category.sort_values(["Month", "Category"])

monthly_dress = (
    df[df["Category"] == "Dress"]
    .groupby("Month", as_index=False)
    .agg(
        **{
            "Discount Dress": ("Discount", "mean"),
            "Profit Dress": ("Profit", "sum")
        }
    )
)
monthly_dress["Month"] = pd.Categorical(
    monthly_dress["Month"],
    categories=months_order,
    ordered=True
)
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
    "chart1": "בגרף להלן ניתן לראות את ההכנסות הכוללות של החברה לאורך חודשי התקופה.",
    "chart2": "בגרף להלן ניתן לראות את הרווח הכולל של החברה לאורך חודשי התקופה.",
    "chart3": "בגרף להלן ניתן לראות את ההכנסות של החברה לפי קטגוריות מוצרים לאורך חודשי התקופה.",
    "chart4": "בגרף להלן ניתן לראות את שיעור ההנחה בקטגוריית Dress ואת הרווח בקטגוריה זו לאורך חודשי התקופה."
}

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "experiment_started": False,
    "participant_id": "",
    "experiment_group": "",
    "session_id": str(uuid.uuid4()),
    "session_start_time": None,
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
    "chart3_month": months_order[0],
    "chart3_category": "Dress",

    "chart4_drilled": False,
    "chart4_month": months_order[0],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# widget defaults
widget_defaults = {
    "chart1_month_select": months_order[0],
    "chart2_month_select": months_order[0],
    "chart3_month_select": months_order[0],
    "chart3_category_select": "Dress",
    "chart4_month_select": months_order[0],
}
for key, value in widget_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# previous values for change tracking
prev_defaults = {
    "__prev_chart1_month_select": months_order[0],
    "__prev_chart2_month_select": months_order[0],
    "__prev_chart3_month_select": months_order[0],
    "__prev_chart3_category_select": "Dress",
    "__prev_chart4_month_select": months_order[0],
}
for key, value in prev_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_experiment():
    for key, value in defaults.items():
        st.session_state[key] = value if key != "session_id" else str(uuid.uuid4())

    for key, value in widget_defaults.items():
        st.session_state[key] = value

    for key, value in prev_defaults.items():
        st.session_state[key] = value

    st.session_state.experiment_started = False
    st.session_state.participant_id = ""
    st.session_state.experiment_group = ""
    st.session_state.session_start_time = None
    st.session_state.question_start_time = None
    st.session_state.answers = []
    st.session_state.db_saved = False


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
        "session_id": st.session_state.session_id,
        "participant_id": st.session_state.participant_id,
        "experiment_group": st.session_state.experiment_group,
        "total_duration_seconds": round(total_duration, 2),
        "dashboard_interaction_clicks": st.session_state.dashboard_interaction_clicks,
        "correct_answers_count": st.session_state.correct_count,
        "total_questions": len(questions),
    }
    supabase.table("sessions").insert(data).execute()


def save_responses_to_db():
    rows = []
    for answer in st.session_state.answers:
        rows.append({
            "session_id": st.session_state.session_id,
            "participant_id": st.session_state.participant_id,
            "experiment_group": st.session_state.experiment_group,
            "question_id": answer["question_id"],
            "question_text": answer["question_text"],
            "selected_answer": answer["selected_answer"],
            "correct_answer": answer["correct_answer"],
            "is_correct": answer["is_correct"],
            "response_time_seconds": answer["response_time_seconds"],
        })

    if rows:
        supabase.table("responses").insert(rows).execute()


def empty_panel():
    st.markdown("""
        <div class="empty-panel">
            <div>
                <div style="font-size:1.05rem;font-weight:700;margin-bottom:6px;">הגרף עדיין לא נחשף</div>
                <div>המשך/י לענות על השאלות כדי לחשוף את השלב הבא בדשבורד</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def panel_header(title: str, narrative: str):
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)

    if st.session_state.experiment_group == "storytelling":
        st.markdown(f'<div class="story-box">{narrative}</div>', unsafe_allow_html=True)


def month_daily_totals(month_name: str):
    d = df[df["Month"] == month_name].groupby(["Day"], as_index=False).agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    )
    return d.sort_values("Day")


def category_month_daily(month_name: str, category_name: str):
    d = df[
        (df["Month"] == month_name) &
        (df["Category"] == category_name)
    ].sort_values("Day")
    return d[["Day", "Revenue", "Profit", "Discount"]].copy()


def dress_month_daily(month_name: str):
    d = df[
        (df["Month"] == month_name) &
        (df["Category"] == "Dress")
    ].sort_values("Day")
    return d[["Day", "Profit", "Discount"]].copy()


def apply_common_layout(fig, title_text):
    fig.update_layout(
        title=title_text,
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="",
        title_x=0.02
    )
    return fig


def show_chart1():
    panel_header("גרף 1: מגמת הכנסות", chart_narratives["chart1"])

    if not st.session_state.chart1_drilled:
        fig = px.line(
            monthly_total,
            x="Month",
            y="Revenue Total",
            markers=True
        )
        fig = apply_common_layout(fig, "Revenue Total by Month")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2.2, 1])
        with c1:
            st.selectbox(
                "בחר/י חודש ל-drill down",
                months_order,
                key="chart1_month_select",
                on_change=track_filter_change,
                args=("chart1_month_select", "chart1_filter_month_change")
            )
        with c2:
            st.write("")
            if st.button("Drill Down", key="chart1_drill_btn", use_container_width=True):
                st.session_state.chart1_month = st.session_state.chart1_month_select
                st.session_state.chart1_drilled = True
                track_dashboard_click("chart1_drill_down", st.session_state.chart1_month)
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart1_month)
        fig = px.bar(
            drill_df,
            x="Day",
            y="Revenue"
        )
        fig = apply_common_layout(fig, f"Daily Revenue - {st.session_state.chart1_month}")
        st.plotly_chart(fig, use_container_width=True)

        if st.button("חזרה", key="chart1_back_btn", use_container_width=True):
            st.session_state.chart1_drilled = False
            track_dashboard_click("chart1_back", st.session_state.chart1_month)
            st.rerun()


def show_chart2():
    panel_header("גרף 2: מגמת רווח", chart_narratives["chart2"])

    if not st.session_state.chart2_drilled:
        fig = px.line(
            monthly_total,
            x="Month",
            y="Profit Total",
            markers=True
        )
        fig = apply_common_layout(fig, "Profit Total by Month")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2.2, 1])
        with c1:
            st.selectbox(
                "בחר/י חודש ל-drill down",
                months_order,
                key="chart2_month_select",
                on_change=track_filter_change,
                args=("chart2_month_select", "chart2_filter_month_change")
            )
        with c2:
            st.write("")
            if st.button("Drill Down", key="chart2_drill_btn", use_container_width=True):
                st.session_state.chart2_month = st.session_state.chart2_month_select
                st.session_state.chart2_drilled = True
                track_dashboard_click("chart2_drill_down", st.session_state.chart2_month)
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart2_month)
        fig = px.bar(
            drill_df,
            x="Day",
            y="Profit"
        )
        fig = apply_common_layout(fig, f"Daily Profit - {st.session_state.chart2_month}")
        st.plotly_chart(fig, use_container_width=True)

        if st.button("חזרה", key="chart2_back_btn", use_container_width=True):
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
            markers=True
        )
        fig = apply_common_layout(fig, "Revenue by Category and Month")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns([1.2, 1.2, 1])
        with c1:
            st.selectbox(
                "בחר/י קטגוריה",
                ["T-shirt", "Dress", "Jeans"],
                key="chart3_category_select",
                on_change=track_filter_change,
                args=("chart3_category_select", "chart3_filter_category_change")
            )
        with c2:
            st.selectbox(
                "בחר/י חודש",
                months_order,
                key="chart3_month_select",
                on_change=track_filter_change,
                args=("chart3_month_select", "chart3_filter_month_change")
            )
        with c3:
            st.write("")
            if st.button("Drill Down", key="chart3_drill_btn", use_container_width=True):
                st.session_state.chart3_category = st.session_state.chart3_category_select
                st.session_state.chart3_month = st.session_state.chart3_month_select
                st.session_state.chart3_drilled = True
                track_dashboard_click(
                    "chart3_drill_down",
                    f"{st.session_state.chart3_category}|{st.session_state.chart3_month}"
                )
                st.rerun()
    else:
        drill_df = category_month_daily(
            st.session_state.chart3_month,
            st.session_state.chart3_category
        )

        long_df = drill_df.melt(
            id_vars="Day",
            value_vars=["Revenue", "Profit"],
            var_name="Metric",
            value_name="Value"
        )

        fig = px.bar(
            long_df,
            x="Day",
            y="Value",
            color="Metric",
            barmode="group"
        )
        fig = apply_common_layout(
            fig,
            f"{st.session_state.chart3_category} - Daily Revenue and Profit ({st.session_state.chart3_month})"
        )
        st.plotly_chart(fig, use_container_width=True)

        if st.button("חזרה", key="chart3_back_btn", use_container_width=True):
            st.session_state.chart3_drilled = False
            track_dashboard_click(
                "chart3_back",
                f"{st.session_state.chart3_category}|{st.session_state.chart3_month}"
            )
            st.rerun()


def show_chart4():
    panel_header("גרף 4: הנחה ורווח ב-Dress", chart_narratives["chart4"])

    if not st.session_state.chart4_drilled:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(
                x=monthly_dress["Month"],
                y=monthly_dress["Profit Dress"],
                mode="lines+markers",
                name="Profit Dress"
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=monthly_dress["Month"],
                y=monthly_dress["Discount Dress"],
                mode="lines+markers",
                name="Discount Dress"
            ),
            secondary_y=True
        )

        fig.update_yaxes(title_text="Profit Dress", secondary_y=False)
        fig.update_yaxes(title_text="Discount Dress (%)", secondary_y=True)
        fig = apply_common_layout(fig, "Dress Discount and Profit by Month")

        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2.2, 1])
        with c1:
            st.selectbox(
                "בחר/י חודש ל-drill down",
                months_order,
                key="chart4_month_select",
                on_change=track_filter_change,
                args=("chart4_month_select", "chart4_filter_month_change")
            )
        with c2:
            st.write("")
            if st.button("Drill Down", key="chart4_drill_btn", use_container_width=True):
                st.session_state.chart4_month = st.session_state.chart4_month_select
                st.session_state.chart4_drilled = True
                track_dashboard_click("chart4_drill_down", st.session_state.chart4_month)
                st.rerun()
    else:
        drill_df = dress_month_daily(st.session_state.chart4_month)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=drill_df["Day"],
                y=drill_df["Profit"],
                mode="lines+markers",
                name="Profit Dress"
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=drill_df["Day"],
                y=drill_df["Discount"],
                mode="lines+markers",
                name="Discount Dress"
            ),
            secondary_y=True
        )

        fig.update_yaxes(title_text="Profit Dress", secondary_y=False)
        fig.update_yaxes(title_text="Discount Dress (%)", secondary_y=True)
        fig = apply_common_layout(
            fig,
            f"Dress Discount and Profit by Day ({st.session_state.chart4_month})"
        )

        st.plotly_chart(fig, use_container_width=True)

        if st.button("חזרה", key="chart4_back_btn", use_container_width=True):
            st.session_state.chart4_drilled = False
            track_dashboard_click("chart4_back", st.session_state.chart4_month)
            st.rerun()


def show_or_empty(show_flag, func):
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    if show_flag:
        func()
    else:
        empty_panel()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Start screen
# -----------------------------
if not st.session_state.experiment_started:
    st.markdown('<div class="big-title">ניסוי דשבורד</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">הזנת פרטי התחלה</div>', unsafe_allow_html=True)

    participant_id_input = st.text_input("מספר משתתף")
    experiment_group_input = st.selectbox("קבוצת ניסוי", ["", "control", "storytelling"])

    if st.button("התחל ניסוי", use_container_width=True):
        if participant_id_input.strip() == "":
            st.warning("יש להזין מספר משתתף")
        elif experiment_group_input == "":
            st.warning("יש לבחור קבוצת ניסוי")
        else:
            st.session_state.participant_id = participant_id_input.strip()
            st.session_state.experiment_group = experiment_group_input
            st.session_state.experiment_started = True
            st.session_state.session_start_time = time.time()
            st.session_state.question_start_time = time.time()
            st.session_state.db_saved = False
            st.rerun()

# -----------------------------
# Experiment screen
# -----------------------------
else:
    st.markdown('<div class="big-title">📊 Business Performance Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Dashboard-based decision experiment</div>', unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    with a:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">מספר משתתף</div><div class="metric-value">{st.session_state.participant_id}</div></div>',
            unsafe_allow_html=True
        )
    with b:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">קבוצת ניסוי</div><div class="metric-value">{st.session_state.experiment_group}</div></div>',
            unsafe_allow_html=True
        )
    with c:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">שאלה נוכחית</div><div class="metric-value">{min(st.session_state.current_question + 1, len(questions))} / {len(questions)}</div></div>',
            unsafe_allow_html=True
        )
    with d:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">אינטראקציות בדשבורד</div><div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>',
            unsafe_allow_html=True
        )

    # reveal logic
    show_fig1 = True
    show_fig2 = False
    show_fig3 = False
    show_fig4 = False

    if st.session_state.experiment_group == "control":
        show_fig2 = True
        show_fig3 = True
        show_fig4 = True
    else:
        if st.session_state.current_question >= 2:
            show_fig2 = True
        if st.session_state.current_question >= 4:
            show_fig3 = True
        if st.session_state.current_question >= 7:
            show_fig4 = True

    st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)

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
        '<div class="dashboard-note">נספרות רק אינטראקציות עם הדשבורד עצמו, כמו שינויי פילטרים, drill down וחזרה. בחירת תשובות לשאלות אינה נספרת.</div>',
        unsafe_allow_html=True
    )

    st.divider()

    if st.session_state.current_question < len(questions):
        q = questions[st.session_state.current_question]
        st.subheader(f"שאלה {q['id']} מתוך {len(questions)}")
        st.write(q["text"])

        selected = st.radio(
            "בחר/י תשובה:",
            q["options"],
            key=f"question_{q['id']}"
        )

        if st.button("שלח/י תשובה", use_container_width=True):
            response_time = time.time() - st.session_state.question_start_time
            is_correct = selected == q["correct_answer"]

            st.session_state.answers.append({
                "question_id": q["id"],
                "question_text": q["text"],
                "selected_answer": selected,
                "correct_answer": q["correct_answer"],
                "is_correct": is_correct,
                "response_time_seconds": round(response_time, 2)
            })

            if is_correct:
                st.session_state.correct_count += 1

            st.session_state.current_question += 1
            st.session_state.question_start_time = time.time()
            st.rerun()

    else:
        total_duration = time.time() - st.session_state.session_start_time
        export_df = build_export_df(total_duration)
        interactions_df = build_interactions_df()

        if not st.session_state.db_saved:
            save_session_to_db(total_duration)
            save_responses_to_db()
            st.session_state.db_saved = True

        st.success("הניסוי הסתיים")

        x, y, z = st.columns(3)
        with x:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">זמן כולל</div><div class="metric-value">{round(total_duration, 2)}</div></div>',
                unsafe_allow_html=True
            )
        with y:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">אינטראקציות בדשבורד</div><div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>',
                unsafe_allow_html=True
            )
        with z:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">תשובות נכונות</div><div class="metric-value">{st.session_state.correct_count}</div></div>',
                unsafe_allow_html=True
            )

        st.subheader("תוצאות שאלון")
        st.dataframe(export_df, use_container_width=True)

        csv_results = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "הורדת תוצאות CSV",
            data=csv_results,
            file_name=f"results_{st.session_state.participant_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.subheader("לוג אינטראקציות בדשבורד")
        st.dataframe(interactions_df, use_container_width=True)

        csv_interactions = interactions_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "הורדת לוג אינטראקציות CSV",
            data=csv_interactions,
            file_name=f"interactions_{st.session_state.participant_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

        if st.button("התחל מחדש", use_container_width=True):
            reset_experiment()
            st.rerun()