"""Unit tests for src/kpis.py — compute_kpis and get_alarm_level functions."""

import pandas as pd
from src.kpis import compute_kpis, get_alarm_level


def test_avg_watch_hours(data):
    """Average watch hours is a positive float on full dataset."""
    result = compute_kpis(
        {"users": data["users"], "watch": data["watch"], "recs": data["recs"]}
    )
    assert result["avg_watch_hours"] > 0


def test_completion_rate(data):
    """Completion rate is in [0, 100] on full dataset."""
    result = compute_kpis(
        {"users": data["users"], "watch": data["watch"], "recs": data["recs"]}
    )
    assert 0 <= result["completion_rate"] <= 100


def test_rec_ctr(data):
    """Rec CTR is in [0, 100] on full dataset, uses was_clicked column."""
    result = compute_kpis(
        {"users": data["users"], "watch": data["watch"], "recs": data["recs"]}
    )
    assert 0 <= result["rec_ctr"] <= 100


def test_churn_rate(data):
    """Churn rate is in [0, 100] on full dataset, based on is_active==False."""
    result = compute_kpis(
        {"users": data["users"], "watch": data["watch"], "recs": data["recs"]}
    )
    assert 0 <= result["churn_rate"] <= 100


def test_empty_dataframe_guard(data):
    """Returns 0.0 for all KPIs when DataFrames are empty (no ZeroDivisionError)."""
    empty = {
        "users": data["users"].head(0),
        "watch": data["watch"].head(0),
        "recs": data["recs"].head(0),
    }
    result = compute_kpis(empty)
    assert result["avg_watch_hours"] == 0.0
    assert result["completion_rate"] == 0.0
    assert result["rec_ctr"] == 0.0
    assert result["churn_rate"] == 0.0


def test_alarm_color_thresholds():
    """Verify each KPI alarm returns correct color at boundary values."""
    # Churn Rate: green < 15, yellow 15-25, red > 25
    assert get_alarm_level("churn_rate", 10) == "green"
    assert get_alarm_level("churn_rate", 20) == "yellow"
    assert get_alarm_level("churn_rate", 30) == "red"

    # Completion Rate: green > 60, yellow 40-60, red < 40
    assert get_alarm_level("completion_rate", 70) == "green"
    assert get_alarm_level("completion_rate", 50) == "yellow"
    assert get_alarm_level("completion_rate", 30) == "red"

    # Rec CTR: green > 20, yellow 10-20, red < 10
    assert get_alarm_level("rec_ctr", 25) == "green"
    assert get_alarm_level("rec_ctr", 15) == "yellow"
    assert get_alarm_level("rec_ctr", 5) == "red"

    # Avg Watch Hours: green > 2, yellow 1-2, red < 1
    assert get_alarm_level("avg_watch_hours", 3) == "green"
    assert get_alarm_level("avg_watch_hours", 1.5) == "yellow"
    assert get_alarm_level("avg_watch_hours", 0.5) == "red"
