"""Chart-building functions for the Netflix Strategic Dashboard.

Each chart answers a specific business question tied to the
Netflix recommendation engine case study value logic chain:

  Better Predictions → Higher Engagement → Lower Churn → Revenue Growth

Pure functions: accept filtered DataFrames, return Plotly figures.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Shared layout defaults — Netflix dark theme
_LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    height=300,
    margin=dict(t=40, b=20, l=20, r=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


def _empty_figure(message: str = "No data for selected filters") -> go.Figure:
    """Return an empty figure with a centered annotation."""
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color="#999999"),
    )
    fig.update_layout(**_LAYOUT_DEFAULTS)
    return fig


# ─── Chart 1: Engagement Trend ──────────────────────────────────────
# Q: "Is engagement improving over time? Are seasonal patterns visible?"
# Maps to: Higher Engagement in the value chain
# ML target from case study: P(completion)

def create_engagement_trend(watch_df: pd.DataFrame) -> go.Figure:
    """Monthly completion rate trend over time.

    Shows the % of sessions where users watched ≥90% of content.
    This is the key ML target P(completion) from the case study.
    Seasonal patterns (holiday spikes, Feb dip) become visible.
    """
    if len(watch_df) == 0:
        return _empty_figure()

    df = watch_df.copy()
    df["month"] = df["watch_date"].dt.to_period("M").dt.to_timestamp()
    df["completed"] = df["progress_percentage"] >= 90

    monthly = (
        df.groupby("month")
        .agg(
            completion_rate=("completed", "mean"),
            avg_session_hrs=("watch_duration_minutes", lambda x: x.mean() / 60),
        )
        .reset_index()
    )
    monthly["completion_rate"] = (monthly["completion_rate"] * 100).round(1)
    monthly["avg_session_hrs"] = monthly["avg_session_hrs"].round(2)

    fig = go.Figure()

    # Completion rate as main line
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["completion_rate"],
        mode="lines+markers",
        name="Completion Rate (%)",
        line=dict(color="#E50914", width=3),
        marker=dict(size=6),
        hovertemplate="%{x|%b %Y}<br>Completion: %{y:.1f}%<extra></extra>",
    ))

    # Avg session time as secondary line
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["avg_session_hrs"],
        mode="lines",
        name="Avg Session (hrs)",
        line=dict(color="#FF6B6B", width=2, dash="dot"),
        yaxis="y2",
        hovertemplate="%{x|%b %Y}<br>Session: %{y:.1f} hrs<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title="Monthly Engagement: Completion Rate & Session Time",
        yaxis=dict(title="Completion Rate (%)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis2=dict(title="Avg Session (hrs)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False)

    return fig


# ─── Chart 2: Churn by Segment ─────────────────────────────────────
# Q: "Which subscription segments are at highest churn risk?"
# Maps to: Lower Churn in the value chain
# Case study Q2: "Under what conditions does the engine reduce churn?"

def create_churn_by_plan(users_df: pd.DataFrame) -> go.Figure:
    """Churn rate by subscription plan (vertical bar).

    Shows that Basic subscribers churn ~14% while Premium+ churn ~3%.
    Actionable: target retention campaigns at Basic tier.
    """
    if len(users_df) == 0:
        return _empty_figure()

    churn_data = (
        users_df.groupby("subscription_plan", observed=True)["is_active"]
        .apply(lambda x: round((~x).mean() * 100, 1))
        .reset_index()
    )
    churn_data.columns = ["plan", "churn_rate"]

    # Sort by churn rate descending for visual impact
    churn_data = churn_data.sort_values("churn_rate", ascending=False)

    # Color: red for high churn, green for low
    colors = []
    for rate in churn_data["churn_rate"]:
        if rate > 10:
            colors.append("#FF4136")  # red — critical
        elif rate > 5:
            colors.append("#FFDC00")  # yellow — warning
        else:
            colors.append("#2ECC40")  # green — healthy

    fig = go.Figure(go.Bar(
        x=churn_data["plan"],
        y=churn_data["churn_rate"],
        marker_color=colors,
        text=churn_data["churn_rate"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="%{x}<br>Churn: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title="Churn Rate by Subscription Plan",
        yaxis=dict(title="Churn Rate (%)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        xaxis=dict(title=""),
    )
    fig.update_xaxes(showgrid=False)

    return fig


# ─── Chart 3: Session Duration by Device ────────────────────────────
# Q: "How do engagement patterns differ across devices?"
# Maps to: Higher Engagement — identifies UX investment priorities
# Case study variable: Device type → Avg. session duration

def create_session_by_device(watch_df: pd.DataFrame) -> go.Figure:
    """Average session duration by device type (horizontal bar).

    Smart TV 2.57 hrs vs Mobile 0.85 hrs — big screen = longer engagement.
    Actionable: optimize mobile UX for shorter, more satisfying sessions.
    """
    if len(watch_df) == 0:
        return _empty_figure()

    device_data = (
        watch_df.groupby("device_type", observed=True)["watch_duration_minutes"]
        .mean()
        .div(60)
        .round(2)
        .sort_values(ascending=True)
        .reset_index()
    )
    device_data.columns = ["device", "avg_hours"]

    # Color gradient: longer = more green (good engagement)
    colors = []
    for hrs in device_data["avg_hours"]:
        if hrs >= 2.0:
            colors.append("#2ECC40")
        elif hrs >= 1.5:
            colors.append("#E50914")
        elif hrs >= 1.0:
            colors.append("#FFDC00")
        else:
            colors.append("#FF4136")

    fig = go.Figure(go.Bar(
        y=device_data["device"],
        x=device_data["avg_hours"],
        orientation="h",
        marker_color=colors,
        text=device_data["avg_hours"].apply(lambda v: f"{v:.1f} hrs"),
        textposition="outside",
        hovertemplate="%{y}<br>Avg: %{x:.2f} hrs<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title="Avg Session Duration by Device",
        xaxis=dict(title="Average Hours per Session", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title=""),
    )
    fig.update_yaxes(showgrid=False)

    return fig


# ─── Chart 4: Recommendation Effectiveness ─────────────────────────
# Q: "Which recommendation algorithm type drives the most clicks?"
# Maps to: Better Predictions in the value chain
# Case study Q1: "Do personalized recs increase viewing hours?"

def create_rec_effectiveness(recs_df: pd.DataFrame) -> go.Figure:
    """Recommendation CTR by algorithm type (horizontal bar).

    Personalized 37% >> Similar Users 13%.
    Directly supports the Netflix recommendation engine case study:
    invest in personalization, reduce reliance on cold-start approaches.
    """
    if len(recs_df) == 0:
        return _empty_figure()

    ctr_by_type = (
        recs_df.groupby("recommendation_type", observed=True)["was_clicked"]
        .mean()
        .mul(100)
        .round(1)
        .sort_values(ascending=True)
        .reset_index()
    )
    ctr_by_type.columns = ["type", "ctr"]

    # Readable names
    name_map = {
        "personalized": "Personalized",
        "genre_based": "Genre-Based",
        "trending": "Trending",
        "new_releases": "New Releases",
        "similar_users": "Similar Users",
    }
    ctr_by_type["type"] = ctr_by_type["type"].map(lambda x: name_map.get(x, x))

    # Color: best algorithm green, worst red
    max_ctr = ctr_by_type["ctr"].max()
    min_ctr = ctr_by_type["ctr"].min()
    colors = []
    for ctr in ctr_by_type["ctr"]:
        ratio = (ctr - min_ctr) / (max_ctr - min_ctr) if max_ctr > min_ctr else 0.5
        if ratio > 0.7:
            colors.append("#2ECC40")
        elif ratio > 0.3:
            colors.append("#E50914")
        else:
            colors.append("#564D4D")

    fig = go.Figure(go.Bar(
        y=ctr_by_type["type"],
        x=ctr_by_type["ctr"],
        orientation="h",
        marker_color=colors,
        text=ctr_by_type["ctr"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="%{y}<br>CTR: %{x:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title="Recommendation CTR by Algorithm Type",
        xaxis=dict(title="Click-Through Rate (%)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title=""),
    )
    fig.update_yaxes(showgrid=False)

    return fig
