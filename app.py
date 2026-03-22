import streamlit as st

st.set_page_config(
    page_title="Netflix Strategic Dashboard",
    page_icon=":clapper:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data_loader import load_data

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

# --- Custom CSS for metric tiles ---
st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: #1F1F1F;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #E50914;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar placeholder ---
with st.sidebar:
    st.header("Filters")
    st.info("Filters will be added in the next step")

# --- KPI Row placeholder ---
st.markdown("---")
kpi_cols = st.columns(4)
for i, col in enumerate(kpi_cols):
    with col:
        st.metric(f"KPI {i + 1}", "\u2014")

# --- Chart Grid placeholder ---
st.markdown("---")
st.subheader("Content & Engagement Analytics")

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.info("Chart: Engagement Trends Over Time (Phase 3)")
with chart_col2:
    st.info("Chart: Top Genres by Watch Time (Phase 3)")

chart_col3, chart_col4 = st.columns(2)
with chart_col3:
    st.info("Chart: Device Type Distribution (Phase 3)")
with chart_col4:
    st.info("Chart: Watch Time vs Content Rating (Phase 3)")
