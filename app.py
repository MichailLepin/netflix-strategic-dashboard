import streamlit as st

st.set_page_config(
    page_title="Netflix Strategic Dashboard",
    page_icon=":clapper:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data_loader import load_data
from src.filter import apply_filters
from src.kpis import compute_kpis, get_alarm_level
from src.charts import create_engagement_line, create_genre_bar, create_device_donut, create_subscription_bar

# Load data (cached)
data = load_data()

# --- Header Row ---
logo_col, title_col = st.columns([1, 6])

with logo_col:
    st.markdown(
        '<h1 style="color:#E50914;font-weight:900;margin:0;">NETFLIX</h1>',
        unsafe_allow_html=True,
    )

with title_col:
    st.markdown("## Netflix Strategic Dashboard")
    st.caption("Content Strategy & User Engagement Analytics")

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filters")

    # Genre filter — from movies table, dynamically populated
    all_genres = sorted(data["movies"]["genre_primary"].cat.categories.tolist())
    selected_genres = st.multiselect(
        "Genre", options=all_genres, default=[], placeholder="All genres"
    )

    # Subscription type filter — from users table
    all_plans = sorted(data["users"]["subscription_plan"].cat.categories.tolist())
    selected_plans = st.multiselect(
        "Subscription Type", options=all_plans, default=[], placeholder="All plans"
    )

    # Device type filter — from watch_history
    all_devices = sorted(data["watch"]["device_type"].cat.categories.tolist())
    selected_devices = st.multiselect(
        "Device Type", options=all_devices, default=[], placeholder="All devices"
    )

    # Date range filter — from watch_history watch_date column
    date_min = data["watch"]["watch_date"].min().date()
    date_max = data["watch"]["watch_date"].max().date()
    date_range = st.date_input(
        "Time Period",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    st.markdown("---")
    st.subheader("Alarm Thresholds")
    st.markdown("""
    **Total Watch Hours**
    - :green[Green] > 50K hrs | :orange[Yellow] 20-50K hrs | :red[Red] < 20K hrs
    - *Action: Evaluate content engagement strategies*

    **Completion Rate**
    - :green[Green] > 60% | :orange[Yellow] 40-60% | :red[Red] < 40%
    - *Action: Review content quality and pacing*

    **Rec Click-Through**
    - :green[Green] > 20% | :orange[Yellow] 10-20% | :red[Red] < 10%
    - *Action: Tune recommendation algorithm*

    **Churn Rate**
    - :green[Green] < 15% | :orange[Yellow] 15-25% | :red[Red] > 25%
    - *Action: Investigate retention strategies*
    """)

# --- Apply Filters ---
if len(date_range) != 2:
    st.sidebar.warning("Select both start and end dates")
    filtered = apply_filters(data, [], [], [], ())
    filters_active = False
else:
    filtered = apply_filters(
        data, selected_genres, selected_plans, selected_devices, date_range
    )
    # Check if any filter is actually active
    filters_active = bool(
        selected_genres
        or selected_plans
        or selected_devices
        or date_range != (date_min, date_max)
    )

# --- Compute KPIs ---
kpi_filtered = compute_kpis(filtered)
kpi_overall = compute_kpis(
    {"users": data["users"], "watch": data["watch"], "recs": data["recs"]}
)

# --- KPI Tile Row ---
st.markdown("---")

# Alarm color mapping
ALARM_COLORS = {"green": "#2ECC40", "yellow": "#FFDC00", "red": "#FF4136"}

# KPI display configuration
kpi_config = [
    {
        "key": "avg_watch_hours",
        "label": "Total Watch Hours",
        "format": lambda v: f"{v:,.0f} hrs",
        "delta_color": "normal",
    },
    {
        "key": "completion_rate",
        "label": "Completion Rate",
        "format": lambda v: f"{v:.1f}%",
        "delta_color": "normal",
    },
    {
        "key": "rec_ctr",
        "label": "Rec Click-Through",
        "format": lambda v: f"{v:.1f}%",
        "delta_color": "normal",
    },
    {
        "key": "churn_rate",
        "label": "Churn Rate",
        "format": lambda v: f"{v:.1f}%",
        "delta_color": "inverse",
    },
]

kpi_cols = st.columns(4)
alarm_css_parts = []

for i, (col, cfg) in enumerate(zip(kpi_cols, kpi_config)):
    key = cfg["key"]
    value = kpi_filtered[key]
    overall = kpi_overall[key]
    alarm = get_alarm_level(key, value)
    border_color = ALARM_COLORS[alarm]

    with col:
        if filters_active:
            delta = round(value - overall, 1)
            if "hrs" in cfg["format"](0) and abs(delta) > 100:
                delta_str = f"{delta:+,.0f} hrs"
            elif "%" in cfg["format"](0):
                delta_str = f"{delta:+.1f}%"
            else:
                delta_str = f"{delta:+.1f}"
            st.metric(
                label=cfg["label"],
                value=cfg["format"](value),
                delta=delta_str,
                delta_color=cfg["delta_color"],
            )
        else:
            st.metric(label=cfg["label"], value=cfg["format"](value))

    # Build per-tile alarm CSS (nth-of-type is 1-indexed)
    alarm_css_parts.append(
        f'[data-testid="stMetric"]:nth-of-type({i + 1}) {{ border-left: 4px solid {border_color} !important; }}'
    )

# --- Custom CSS: base metric styling + per-tile alarm coloring ---
st.markdown(
    f"""
    <style>
    [data-testid="stMetric"] {{
        background-color: #1F1F1F;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #E50914;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
    }}
    {chr(10).join(alarm_css_parts)}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Chart Grid placeholder ---
st.markdown("---")
st.subheader("Content & Engagement Analytics")

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    fig_line = create_engagement_line(filtered["watch"], filtered["users"])
    st.plotly_chart(fig_line, use_container_width=True)
with chart_col2:
    fig_bar = create_genre_bar(filtered["watch"], data["movies"])
    st.plotly_chart(fig_bar, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)
with chart_col3:
    fig_donut = create_device_donut(filtered["watch"])
    st.plotly_chart(fig_donut, use_container_width=True)
with chart_col4:
    fig_subs = create_subscription_bar(filtered["users"])
    st.plotly_chart(fig_subs, use_container_width=True)
