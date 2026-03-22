"""KPI computation and alarm coloring for the Netflix Strategic Dashboard.

Pure functions that take filtered DataFrames and return KPI scalars
and alarm levels for dashboard tile coloring.
"""

import pandas as pd


def compute_kpis(filtered: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Compute 4 KPI scalars from filtered DataFrames.

    Parameters
    ----------
    filtered : dict with keys users, watch, recs

    Returns
    -------
    dict with keys: avg_watch_hours, completion_rate, rec_ctr, churn_rate
    All values rounded to 1 decimal place. Returns 0.0 for empty DataFrames.
    """
    users = filtered["users"]
    watch = filtered["watch"]
    recs = filtered["recs"]

    # KPI-01: Average Daily Watch Time (hours)
    if len(watch) > 0:
        avg_watch_hours = round(watch["watch_duration_minutes"].mean() / 60.0, 1)
    else:
        avg_watch_hours = 0.0

    # KPI-02: Content Completion Rate (%)
    if len(watch) > 0:
        completion_rate = round(
            (watch["progress_percentage"] >= 90).sum() / len(watch) * 100, 1
        )
    else:
        completion_rate = 0.0

    # KPI-03: Recommendation Click-Through Rate (%)
    # CRITICAL: column is was_clicked, NOT clicked
    if len(recs) > 0:
        rec_ctr = round(recs["was_clicked"].sum() / len(recs) * 100, 1)
    else:
        rec_ctr = 0.0

    # KPI-04: Churn Rate (%) — is_active=False means churned
    if len(users) > 0:
        churn_rate = round((~users["is_active"]).sum() / len(users) * 100, 1)
    else:
        churn_rate = 0.0

    return {
        "avg_watch_hours": avg_watch_hours,
        "completion_rate": completion_rate,
        "rec_ctr": rec_ctr,
        "churn_rate": churn_rate,
    }


def get_alarm_level(kpi_name: str, value: float) -> str:
    """Return 'green', 'yellow', or 'red' based on alarm thresholds.

    Thresholds:
    - churn_rate: green < 15, yellow 15-25, red > 25
    - completion_rate: green > 60, yellow 40-60, red < 40
    - rec_ctr: green > 20, yellow 10-20, red < 10
    - avg_watch_hours: green > 2, yellow 1-2, red < 1
    """
    if kpi_name == "churn_rate":
        if value < 15:
            return "green"
        elif value <= 25:
            return "yellow"
        else:
            return "red"
    elif kpi_name == "completion_rate":
        if value > 60:
            return "green"
        elif value >= 40:
            return "yellow"
        else:
            return "red"
    elif kpi_name == "rec_ctr":
        if value > 20:
            return "green"
        elif value >= 10:
            return "yellow"
        else:
            return "red"
    elif kpi_name == "avg_watch_hours":
        if value > 2:
            return "green"
        elif value >= 1:
            return "yellow"
        else:
            return "red"
    else:
        return "yellow"  # Unknown KPI defaults to warning
