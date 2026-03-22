"""Tests for src/data_loader.py — covers DATA-01, DATA-02, DATA-03 requirements."""

import pandas as pd


EXPECTED_KEYS = {"users", "movies", "watch", "recs", "searches", "reviews"}


def test_load_data_returns_all_tables(data):
    """DATA-01: load_data() returns dict with all 6 expected keys."""
    assert isinstance(data, dict)
    assert set(data.keys()) == EXPECTED_KEYS


def test_all_tables_nonempty(data):
    """DATA-01: Each DataFrame in the dict has len > 0."""
    for name, df in data.items():
        assert len(df) > 0, f"{name} DataFrame is empty"


def test_users_no_duplicate_ids(data):
    """DATA-02: users DataFrame has no duplicate user_id values."""
    users = data["users"]
    assert users["user_id"].is_unique, "Duplicate user_id values found in users"


def test_no_nulls_in_key_columns(data):
    """DATA-02: user_id and movie_id columns have zero nulls in their respective tables."""
    # user_id should have no nulls in users, watch, recs, searches, reviews
    for name in ["users", "watch", "recs", "searches", "reviews"]:
        df = data[name]
        assert df["user_id"].isna().sum() == 0, f"{name} has null user_id values"

    # movie_id should have no nulls in movies, watch, recs, reviews
    for name in ["movies", "watch", "recs", "reviews"]:
        df = data[name]
        assert df["movie_id"].isna().sum() == 0, f"{name} has null movie_id values"


def test_category_dtypes(data):
    """DATA-02: subscription_plan, country, primary_device columns have category dtype."""
    users = data["users"]
    # Actual column names from dataset: subscription_plan, country, primary_device
    for col in ["subscription_plan", "country", "primary_device"]:
        assert users[col].dtype.name == "category", (
            f"users['{col}'] has dtype {users[col].dtype.name}, expected category"
        )


def test_age_outliers_capped(data):
    """DATA-02: All values in users['age'] are between 13 and 100 inclusive."""
    users = data["users"]
    assert users["age"].min() >= 13, f"Min age {users['age'].min()} < 13"
    assert users["age"].max() <= 100, f"Max age {users['age'].max()} > 100"


def test_watch_user_join_quality(data):
    """DATA-03: At least 80% of watch_history user_ids exist in users user_ids."""
    watch = data["watch"]
    users = data["users"]
    match_rate = watch["user_id"].isin(users["user_id"]).mean()
    assert match_rate >= 0.80, (
        f"watch_history user_id match rate {match_rate:.1%} < 80%"
    )


def test_watch_movie_join_quality(data):
    """DATA-03: At least 80% of watch_history movie_ids exist in movies movie_ids."""
    watch = data["watch"]
    movies = data["movies"]
    match_rate = watch["movie_id"].isin(movies["movie_id"]).mean()
    assert match_rate >= 0.80, (
        f"watch_history movie_id match rate {match_rate:.1%} < 80%"
    )


def test_memory_under_limit(data):
    """DATA-03: Sum of memory for all 6 DataFrames < 400MB."""
    total_bytes = sum(df.memory_usage(deep=True).sum() for df in data.values())
    total_mb = total_bytes / 1e6
    assert total_mb < 400, f"Total memory {total_mb:.1f} MB exceeds 400MB limit"
