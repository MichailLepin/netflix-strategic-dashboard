"""Chart-building functions for the Netflix Strategic Dashboard.

Pure functions that accept filtered DataFrames and return Plotly figures.
No Streamlit calls — only plotly.express for chart construction.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Netflix-themed color palettes
_GENRE_COLORS = [
    "#E50914", "#B20710", "#831010", "#5C0A0A", "#FF6B6B",
    "#FF9999", "#CC3333", "#993333", "#660000", "#330000",
]
_DEVICE_COLORS = ["#E50914", "#B20710", "#564D4D", "#831010", "#999999"]

# Shared layout defaults
_LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    height=300,
    margin=dict(t=30, b=20, l=20, r=20),
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


def create_engagement_line(
    watch_df: pd.DataFrame, users_df: pd.DataFrame
) -> go.Figure:
    """Weekly watch hours over time, segmented by subscription plan.

    Parameters
    ----------
    watch_df : filtered watch_history DataFrame
    users_df : filtered users DataFrame (needed for subscription_plan)

    Returns
    -------
    Plotly Figure (line chart)
    """
    if len(watch_df) == 0:
        return _empty_figure()

    # Merge to get subscription_plan onto watch rows
    merged = watch_df.merge(
        users_df[["user_id", "subscription_plan"]], on="user_id", how="left"
    )

    # Resample weekly: mean watch duration in hours per plan
    merged["watch_hours"] = merged["watch_duration_minutes"] / 60.0
    weekly = (
        merged
        .groupby([pd.Grouper(key="watch_date", freq="W"), "subscription_plan"])["watch_hours"]
        .mean()
        .reset_index()
    )
    weekly.columns = ["week", "subscription_plan", "avg_watch_hours"]

    fig = px.line(
        weekly, x="week", y="avg_watch_hours",
        color="subscription_plan",
        title="Weekly Watch Hours by Subscription Plan",
    )
    fig.update_layout(**_LAYOUT_DEFAULTS)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3))
    fig.update_xaxes(showgrid=False)
    # Keep y-grid for readability on line chart
    return fig


def create_genre_bar(
    watch_df: pd.DataFrame, movies_df: pd.DataFrame
) -> go.Figure:
    """Top 10 genres by total watch time (horizontal bar chart).

    Parameters
    ----------
    watch_df : filtered watch_history DataFrame
    movies_df : movies DataFrame (unfiltered, for genre lookup)

    Returns
    -------
    Plotly Figure (horizontal bar chart)
    """
    if len(watch_df) == 0:
        return _empty_figure()

    merged = watch_df.merge(
        movies_df[["movie_id", "genre_primary"]], on="movie_id", how="left"
    )
    merged["watch_hours"] = merged["watch_duration_minutes"] / 60.0

    genre_totals = (
        merged
        .groupby("genre_primary", observed=True)["watch_hours"]
        .sum()
        .nlargest(10)
        .sort_values(ascending=True)  # ascending for horizontal bar (highest at top)
        .reset_index()
    )
    genre_totals.columns = ["genre", "total_hours"]

    fig = px.bar(
        genre_totals, x="total_hours", y="genre",
        orientation="h", color="genre",
        color_discrete_sequence=_GENRE_COLORS,
        title="Top 10 Genres by Watch Time (Hours)",
    )
    fig.update_layout(**_LAYOUT_DEFAULTS)
    fig.update_layout(showlegend=False)  # bar labels are self-explanatory
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig


def create_device_donut(watch_df: pd.DataFrame) -> go.Figure:
    """Device type distribution by session count (donut chart).

    Parameters
    ----------
    watch_df : filtered watch_history DataFrame

    Returns
    -------
    Plotly Figure (donut/pie chart)
    """
    if len(watch_df) == 0:
        return _empty_figure()

    device_counts = (
        watch_df["device_type"]
        .value_counts()
        .reset_index()
    )
    device_counts.columns = ["device_type", "count"]

    fig = px.pie(
        device_counts, names="device_type", values="count",
        hole=0.4,
        color_discrete_sequence=_DEVICE_COLORS,
        title="Watch Sessions by Device",
    )
    fig.update_layout(**_LAYOUT_DEFAULTS)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3))
    return fig


def create_rec_effectiveness_bar(recs_df: pd.DataFrame) -> go.Figure:
    """Recommendation CTR by algorithm type (horizontal bar chart).

    Answers: "Which recommendation strategy works best?"
    Directly tied to the Netflix recommendation engine case study.

    Parameters
    ----------
    recs_df : filtered recommendation_logs DataFrame

    Returns
    -------
    Plotly Figure (horizontal bar chart)
    """
    if len(recs_df) == 0:
        return _empty_figure()

    ctr_by_type = (
        recs_df
        .groupby("recommendation_type", observed=True)["was_clicked"]
        .mean()
        .mul(100)
        .round(1)
        .sort_values(ascending=True)
        .reset_index()
    )
    ctr_by_type.columns = ["recommendation_type", "ctr_percent"]

    # Rename for readability
    name_map = {
        "personalized": "Personalized",
        "genre_based": "Genre-Based",
        "trending": "Trending",
        "new_releases": "New Releases",
        "similar_users": "Similar Users",
    }
    ctr_by_type["recommendation_type"] = ctr_by_type["recommendation_type"].map(
        lambda x: name_map.get(x, x)
    )

    _REC_COLORS = {
        "Personalized": "#2ECC40",
        "Genre-Based": "#E50914",
        "Trending": "#FF6B6B",
        "New Releases": "#B20710",
        "Similar Users": "#564D4D",
    }

    fig = px.bar(
        ctr_by_type, x="ctr_percent", y="recommendation_type",
        orientation="h",
        color="recommendation_type",
        color_discrete_map=_REC_COLORS,
        title="Recommendation CTR by Algorithm Type (%)",
    )
    fig.update_layout(**_LAYOUT_DEFAULTS)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(showgrid=False, title_text="Click-Through Rate (%)")
    fig.update_yaxes(showgrid=False, title_text="")
    return fig
