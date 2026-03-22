"""Unit tests for src/filter.py — apply_filters function."""

import pandas as pd
from src.filter import apply_filters


def test_genre_filter(data):
    """Selecting 1 genre reduces watch rows to only movies of that genre."""
    genre = data["movies"]["genre_primary"].cat.categories[0]
    filtered = apply_filters(data, genres=[genre], plans=[], devices=[], date_range=())
    # All remaining watch rows should map to movies with the selected genre
    genre_movie_ids = set(
        data["movies"].loc[data["movies"]["genre_primary"] == genre, "movie_id"]
    )
    assert len(filtered["watch"]) > 0
    assert filtered["watch"]["movie_id"].isin(genre_movie_ids).all()
    assert len(filtered["watch"]) <= len(data["watch"])


def test_subscription_filter(data):
    """Selecting 'Premium' reduces users to Premium-only, and cascades to watch/recs."""
    filtered = apply_filters(data, genres=[], plans=["Premium"], devices=[], date_range=())
    assert (filtered["users"]["subscription_plan"] == "Premium").all()
    premium_user_ids = set(filtered["users"]["user_id"])
    assert filtered["watch"]["user_id"].isin(premium_user_ids).all()
    assert filtered["recs"]["user_id"].isin(premium_user_ids).all()


def test_device_filter(data):
    """Selecting 1 device reduces watch rows to that device only."""
    device = data["watch"]["device_type"].cat.categories[0]
    filtered = apply_filters(data, genres=[], plans=[], devices=[device], date_range=())
    assert (filtered["watch"]["device_type"] == device).all()
    assert len(filtered["watch"]) <= len(data["watch"])


def test_date_filter(data):
    """Selecting a 1-month range reduces watch rows to that month only."""
    date_min = data["watch"]["watch_date"].min()
    date_end = date_min + pd.Timedelta(days=30)
    date_range = (date_min.date(), date_end.date())
    filtered = apply_filters(data, genres=[], plans=[], devices=[], date_range=date_range)
    assert (filtered["watch"]["watch_date"] >= pd.Timestamp(date_range[0])).all()
    assert (filtered["watch"]["watch_date"] <= pd.Timestamp(date_range[1])).all()


def test_no_filter(data):
    """Empty lists and full date range returns all rows unchanged."""
    date_min = data["watch"]["watch_date"].min().date()
    date_max = data["watch"]["watch_date"].max().date()
    filtered = apply_filters(
        data, genres=[], plans=[], devices=[], date_range=(date_min, date_max)
    )
    assert len(filtered["watch"]) == len(data["watch"])
    assert len(filtered["users"]) == len(data["users"])
    assert len(filtered["recs"]) == len(data["recs"])


def test_combined_filters(data):
    """Genre + subscription applied together narrows correctly."""
    genre = data["movies"]["genre_primary"].cat.categories[0]
    filtered = apply_filters(
        data, genres=[genre], plans=["Premium"], devices=[], date_range=()
    )
    # Genre constraint
    genre_movie_ids = set(
        data["movies"].loc[data["movies"]["genre_primary"] == genre, "movie_id"]
    )
    assert filtered["watch"]["movie_id"].isin(genre_movie_ids).all()
    # Subscription constraint
    assert (filtered["users"]["subscription_plan"] == "Premium").all()
    premium_user_ids = set(filtered["users"]["user_id"])
    assert filtered["watch"]["user_id"].isin(premium_user_ids).all()
