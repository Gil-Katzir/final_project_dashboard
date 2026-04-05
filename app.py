
import streamlit as st
import pandas as pd
import plotly.express as px
import time
import uuid
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Final Project Dashboard", layout="wide")

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #f6f8fb;
}
.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.big-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #18212f;
    margin-bottom: 0.1rem;
}
.sub-title {
    font-size: 1rem;
    color: #667085;
    margin-bottom: 1.2rem;
}
.metric-card {
    background: white;
    border: 1px solid #e7ecf3;
    border-radius: 18px;
    padding: 14px 18px;
    box-shadow: 0 4px 14px rgba(16,24,40,0.06);
}
.metric-label {
    color: #667085;
    font-size: 0.85rem;
}
.metric-value {
    color: #111827;
    font-size: 1.2rem;
    font-weight: 800;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #18212f;
    margin-top: 1.2rem;
    margin-bottom: 0.7rem;
}
.empty-panel {
    background: white;
    border: 1px solid #e7ecf3;
    border-radius: 18px;
    min-height: 420px;
    box-shadow: 0 4px 14px rgba(16,24,40,0.04);
}
div[data-testid="stVerticalBlock"] div:has(> div[data-testid="stPlotlyChart"]) {
    border-radius: 18px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
df = pd.read_csv("data.csv")
df["Date"] = pd.to_datetime(df["Date"])
months_order = list(df["Month"].drop_duplicates())

# monthly aggregates
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
    "chart1_drilled": False,
    "chart1_month": months_order[0],
    "chart2_drilled": False,
    "chart2_month": months_order[0],
    "chart3_drilled": False,
    "chart3_month": months_order[0],
    "chart3_category": "Dress",
    "chart4_drilled": False,
    "chart4_month": months_order[0]
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_experiment():
    for key, value in defaults.items():
        st.session_state[key] = value if key != "session_id" else str(uuid.uuid4())
    st.session_state.experiment_started = False
    st.session_state.participant_id = ""
    st.session_state.experiment_group = ""
    st.session_state.session_start_time = None
    st.session_state.question_start_time = None
    st.session_state.answers = []


def track_dashboard_click():
    st.session_state.dashboard_interaction_clicks += 1


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


def empty_panel():
    st.markdown('<div class="empty-panel"></div>', unsafe_allow_html=True)


def panel_header(title: str, narrative: str):
    st.markdown(f"**{title}**")
    st.write(narrative)


def month_daily_totals(month_name: str):
    d = df[df["Month"] == month_name].groupby(["Day"], as_index=False).agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum")
    )
    return d.sort_values("Day")


def category_month_daily(month_name: str, category_name: str):
    d = df[(df["Month"] == month_name) & (df["Category"] == category_name)].sort_values("Day")
    return d[["Day", "Revenue", "Profit", "Discount"]].copy()


def dress_month_daily(month_name: str):
    d = df[(df["Month"] == month_name) & (df["Category"] == "Dress")].sort_values("Day")
    return d[["Day", "Profit", "Discount"]].copy()


def show_chart1():
    panel_header("גרף 1: מגמת הכנסות", chart_narratives["chart1"])
    if not st.session_state.chart1_drilled:
        fig = px.line(
            monthly_total,
            x="Month",
            y="Revenue Total",
            markers=True,
            title="Revenue Total by Month"
        )
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            selected_month = st.selectbox("בחר/י חודש ל-drill down", months_order, key="chart1_month_select")
        with c2:
            st.write("")
            if st.button("Drill Down", key="chart1_drill_btn", use_container_width=True):
                st.session_state.chart1_month = selected_month
                st.session_state.chart1_drilled = True
                track_dashboard_click()
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart1_month)
        fig = px.bar(
            drill_df,
            x="Day",
            y="Revenue",
            title=f"Daily Revenue - {st.session_state.chart1_month}"
        )
        st.plotly_chart(fig, use_container_width=True)
        if st.button("חזרה", key="chart1_back_btn", use_container_width=True):
            st.session_state.chart1_drilled = False
            track_dashboard_click()
            st.rerun()


def show_chart2():
    panel_header("גרף 2: מגמת רווח", chart_narratives["chart2"])
    if not st.session_state.chart2_drilled:
        fig = px.line(
            monthly_total,
            x="Month",
            y="Profit Total",
            markers=True,
            title="Profit Total by Month"
        )
        st.plotly_chart(fig, use_container_width=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            selected_month = st.selectbox("בחר/י חודש ל-drill down", months_order, key="chart2_month_select")
        with c2:
            st.write("")
            if st.button("Drill Down", key="chart2_drill_btn", use_container_width=True):
                st.session_state.chart2_month = selected_month
                st.session_state.chart2_drilled = True
                track_dashboard_click()
                st.rerun()
    else:
        drill_df = month_daily_totals(st.session_state.chart2_month)
        fig = px.bar(
            drill_df,
            x="Day",
            y="Profit",
            title=f"Daily Profit - {st.session_state.chart2_month}"
        )
        st.plotly_chart(fig, use_container_width=True)
        if st.button("חזרה", key="chart2_back_btn", use_container_width=True):
            st.session_state.chart2_drilled = False
            track_dashboard_click()
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
            title="Revenue by Category and Month"
        )
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns([1.2, 1.2, 1])
        with c1:
            selected_category = st.selectbox("בחר/י קטגוריה", ["T-shirt", "Dress", "Jeans"], key="chart3_category_select")
        with c2:
            selected_month = st.selectbox("בחר/י חודש", months_order, key="chart3_month_select")
        with c3:
            st.write("")
            if st.button("Drill Down", key="chart3_drill_btn", use_container_width=True):
                st.session_state.chart3_category = selected_category
                st.session_state.chart3_month = selected_month
                st.session_state.chart3_drilled = True
                track_dashboard_click()
                st.rerun()
    else:
        drill_df = category_month_daily(st.session_state.chart3_month, st.session_state.chart3_category)
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
            barmode="group",
            title=f"{st.session_state.chart3_category} - Daily Revenue and Profit ({st.session_state.chart3_month})"
        )
        st.plotly_chart(fig, use_container_width=True)
        if st.button("חזרה", key="chart3_back_btn", use_container_width=True):
            st.session_state.chart3_drilled = False
            track_dashboard_click()
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

        fig.update_layout(
            title="Dress Discount and Profit by Month",
            margin=dict(l=20, r=20, t=50, b=20)
        )

        fig.update_yaxes(title_text="Profit Dress", secondary_y=False)
        fig.update_yaxes(title_text="Discount Dress (%)", secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            selected_month = st.selectbox(
                "בחר/י חודש ל-drill down",
                months_order,
                key="chart4_month_select"
            )
        with c2:
            st.write("")
            if st.button("Drill Down", key="chart4_drill_btn", use_container_width=True):
                st.session_state.chart4_month = selected_month
                st.session_state.chart4_drilled = True
                track_dashboard_click()
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

        fig.update_layout(
            title=f"Dress Discount and Profit by Day ({st.session_state.chart4_month})",
            margin=dict(l=20, r=20, t=50, b=20)
        )

        fig.update_yaxes(title_text="Profit Dress", secondary_y=False)
        fig.update_yaxes(title_text="Discount Dress (%)", secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)

        if st.button("חזרה", key="chart4_back_btn", use_container_width=True):
            st.session_state.chart4_drilled = False
            track_dashboard_click()
            st.rerun()


def show_or_empty(show_flag, func):
    with st.container(border=True):
        if show_flag:
            func()
        else:
            empty_panel()


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
            st.rerun()

# -----------------------------
# Experiment screen
# -----------------------------
else:
    st.markdown('<div class="big-title">Final Project Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Dashboard-based decision experiment</div>', unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        st.markdown(f'<div class="metric-card"><div class="metric-label">מספר משתתף</div><div class="metric-value">{st.session_state.participant_id}</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown(f'<div class="metric-card"><div class="metric-label">קבוצת ניסוי</div><div class="metric-value">{st.session_state.experiment_group}</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="metric-card"><div class="metric-label">שאלה נוכחית</div><div class="metric-value">{min(st.session_state.current_question + 1, len(questions))} / {len(questions)}</div></div>', unsafe_allow_html=True)

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

    st.caption("שים/י לב: לאחר שליחת תשובה לא ניתן לשנות אותה.")

    st.divider()

    if st.session_state.current_question < len(questions):
        q = questions[st.session_state.current_question]
        st.subheader(f"שאלה {q['id']} מתוך {len(questions)}")
        st.write(q["text"])

        selected = st.radio("בחר/י תשובה:", q["options"], key=f"question_{q['id']}")

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

        st.success("הניסוי הסתיים")
        x, y, z = st.columns(3)
        with x:
            st.markdown(f'<div class="metric-card"><div class="metric-label">זמן כולל</div><div class="metric-value">{round(total_duration, 2)}</div></div>', unsafe_allow_html=True)
        with y:
            st.markdown(f'<div class="metric-card"><div class="metric-label">אינטראקציות בדשבורד</div><div class="metric-value">{st.session_state.dashboard_interaction_clicks}</div></div>', unsafe_allow_html=True)
        with z:
            st.markdown(f'<div class="metric-card"><div class="metric-label">תשובות נכונות</div><div class="metric-value">{st.session_state.correct_count}</div></div>', unsafe_allow_html=True)

        st.dataframe(export_df, use_container_width=True)
        csv = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "הורדת תוצאות CSV",
            data=csv,
            file_name=f"results_{st.session_state.participant_id}.csv",
            mime="text/csv",
            use_container_width=True
        )
        if st.button("התחל מחדש", use_container_width=True):
            reset_experiment()
            st.rerun()
