"""Data loader for Netflix 2025 User Behavior Dataset.

Loads, cleans, type-casts, join-validates, and caches all 6 CSV tables.
"""

import os
import streamlit as st
import pandas as pd

# Resolve data directory relative to this file so it works from any cwd
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    """Load, clean, and return all 6 Netflix dataset tables.

    Returns a dict with keys: users, movies, watch, recs, searches, reviews
    """
    users = _load_users()
    movies = _load_movies()
    watch = _load_watch_history()
    recs = _load_recommendation_logs()
    searches = _load_search_logs()
    reviews = _load_reviews()

    # Validate join keys before downstream code trusts these DataFrames
    _validate_join_keys(users, movies, watch, recs, searches, reviews)

    result = {
        "users": users,
        "movies": movies,
        "watch": watch,
        "recs": recs,
        "searches": searches,
        "reviews": reviews,
    }

    # Memory check
    total_mb = sum(df.memory_usage(deep=True).sum() for df in result.values()) / 1e6
    print(f"Total DataFrame memory: {total_mb:.1f} MB")

    return result


def _load_users() -> pd.DataFrame:
    """Load and clean users.csv.

    Churn definition: The 'is_active' column is a boolean flag.
    Users with is_active=False are considered churned.
    This will be used directly in Phase 2 for the Churn Rate KPI (KPI-04).
    """
    df = pd.read_csv(os.path.join(_DATA_DIR, "users.csv"))

    # Drop duplicate users
    df = df.drop_duplicates(subset=["user_id"])

    # Drop rows with null user_id (critical key)
    df = df.dropna(subset=["user_id"])

    # Fill missing categorical fields with mode
    for col in ["subscription_plan", "country", "primary_device", "gender"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numeric fields with median
    for col in ["age", "monthly_spend", "household_size"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].median())

    # Cap age outliers: Netflix minimum age 13, max 100
    if "age" in df.columns:
        df.loc[:, "age"] = df["age"].clip(13, 100)

    # Cast low-cardinality string columns to category dtype
    # Use df[col] assignment (not df.loc) to ensure dtype actually changes
    for col in ["subscription_plan", "country", "primary_device", "gender"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Cast narrow integers
    if "age" in df.columns:
        df["age"] = df["age"].astype("int16")
    if "household_size" in df.columns and not df["household_size"].isna().any():
        df["household_size"] = df["household_size"].astype("int16")

    # Parse dates
    for col in ["subscription_start_date", "created_at"]:
        if col in df.columns:
            df.loc[:, col] = pd.to_datetime(df[col], errors="coerce")

    return df


def _load_movies() -> pd.DataFrame:
    """Load and clean movies.csv."""
    df = pd.read_csv(os.path.join(_DATA_DIR, "movies.csv"))

    # Drop duplicate movies
    df = df.drop_duplicates(subset=["movie_id"])

    # Drop rows with null movie_id
    df = df.dropna(subset=["movie_id"])

    # Fill missing categorical fields with mode
    for col in ["content_type", "genre_primary", "genre_secondary", "rating",
                "language", "country_of_origin"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numeric fields with median
    for col in ["duration_minutes", "imdb_rating", "production_budget",
                "box_office_revenue", "number_of_seasons", "number_of_episodes"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].median())

    # Cast low-cardinality columns to category
    for col in ["content_type", "genre_primary", "genre_secondary", "rating",
                "language", "country_of_origin"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Parse dates
    if "added_to_platform" in df.columns:
        df.loc[:, "added_to_platform"] = pd.to_datetime(
            df["added_to_platform"], errors="coerce"
        )

    return df


def _load_watch_history() -> pd.DataFrame:
    """Load and clean watch_history.csv."""
    df = pd.read_csv(os.path.join(_DATA_DIR, "watch_history.csv"))

    # Drop duplicates on session_id (primary key)
    df = df.drop_duplicates(subset=["session_id"])

    # Drop rows with null join keys
    df = df.dropna(subset=["user_id", "movie_id"])

    # Fill missing categorical fields
    for col in ["device_type", "action", "quality", "location_country"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numeric fields with median
    for col in ["watch_duration_minutes", "progress_percentage", "user_rating"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].median())

    # Cap watch_duration_minutes: 0-1440 (max 24 hours)
    if "watch_duration_minutes" in df.columns:
        df.loc[:, "watch_duration_minutes"] = df["watch_duration_minutes"].clip(0, 1440)

    # Cast low-cardinality columns to category
    for col in ["device_type", "action", "quality", "location_country"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Parse dates
    if "watch_date" in df.columns:
        df.loc[:, "watch_date"] = pd.to_datetime(df["watch_date"], errors="coerce")

    return df


def _load_recommendation_logs() -> pd.DataFrame:
    """Load and clean recommendation_logs.csv."""
    df = pd.read_csv(os.path.join(_DATA_DIR, "recommendation_logs.csv"))

    # Drop duplicates on recommendation_id (primary key)
    df = df.drop_duplicates(subset=["recommendation_id"])

    # Drop rows with null join keys
    df = df.dropna(subset=["user_id", "movie_id"])

    # Fill missing categorical fields
    for col in ["recommendation_type", "device_type", "time_of_day",
                "algorithm_version"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numeric fields
    for col in ["recommendation_score", "position_in_list"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].median())

    # Cast low-cardinality columns to category
    for col in ["recommendation_type", "device_type", "time_of_day",
                "algorithm_version"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Parse dates
    if "recommendation_date" in df.columns:
        df.loc[:, "recommendation_date"] = pd.to_datetime(
            df["recommendation_date"], errors="coerce"
        )

    return df


def _load_search_logs() -> pd.DataFrame:
    """Load and clean search_logs.csv."""
    df = pd.read_csv(os.path.join(_DATA_DIR, "search_logs.csv"))

    # Drop duplicates on search_id (primary key)
    df = df.drop_duplicates(subset=["search_id"])

    # Drop rows with null user_id
    df = df.dropna(subset=["user_id"])

    # Fill missing categorical fields
    for col in ["device_type", "location_country"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numeric fields
    for col in ["results_returned", "clicked_result_position",
                "search_duration_seconds"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].median())

    # Cast low-cardinality columns to category
    for col in ["device_type", "location_country"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Parse dates
    if "search_date" in df.columns:
        df.loc[:, "search_date"] = pd.to_datetime(
            df["search_date"], errors="coerce"
        )

    return df


def _load_reviews() -> pd.DataFrame:
    """Load and clean reviews.csv."""
    df = pd.read_csv(os.path.join(_DATA_DIR, "reviews.csv"))

    # Drop duplicates on review_id (primary key)
    df = df.drop_duplicates(subset=["review_id"])

    # Drop rows with null join keys
    df = df.dropna(subset=["user_id", "movie_id"])

    # Fill missing categorical fields
    for col in ["device_type", "sentiment"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numeric fields
    for col in ["helpful_votes", "total_votes", "sentiment_score"]:
        if col in df.columns and df[col].isna().any():
            df.loc[:, col] = df[col].fillna(df[col].median())

    # Cast low-cardinality columns to category
    for col in ["device_type", "sentiment"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Parse dates
    if "review_date" in df.columns:
        df.loc[:, "review_date"] = pd.to_datetime(
            df["review_date"], errors="coerce"
        )

    return df


def _validate_join_keys(
    users: pd.DataFrame,
    movies: pd.DataFrame,
    watch: pd.DataFrame,
    recs: pd.DataFrame,
    searches: pd.DataFrame,
    reviews: pd.DataFrame,
) -> None:
    """Validate referential integrity between tables.

    Raises ValueError if any match rate falls below 80%.
    """
    user_ids = set(users["user_id"])
    movie_ids = set(movies["movie_id"])

    # watch_history -> users
    n_watch = len(watch)
    watch_user_match = watch["user_id"].isin(user_ids).sum()
    watch_user_rate = watch_user_match / n_watch
    print(f"watch_history user_id match rate: {watch_user_rate:.1%} "
          f"({n_watch - watch_user_match} orphans out of {n_watch})")

    # watch_history -> movies
    watch_movie_match = watch["movie_id"].isin(movie_ids).sum()
    watch_movie_rate = watch_movie_match / n_watch
    print(f"watch_history movie_id match rate: {watch_movie_rate:.1%} "
          f"({n_watch - watch_movie_match} orphans out of {n_watch})")

    # recommendation_logs -> users
    n_recs = len(recs)
    recs_user_match = recs["user_id"].isin(user_ids).sum()
    recs_user_rate = recs_user_match / n_recs
    print(f"recommendation_logs user_id match rate: {recs_user_rate:.1%} "
          f"({n_recs - recs_user_match} orphans out of {n_recs})")

    # recommendation_logs -> movies
    recs_movie_match = recs["movie_id"].isin(movie_ids).sum()
    recs_movie_rate = recs_movie_match / n_recs
    print(f"recommendation_logs movie_id match rate: {recs_movie_rate:.1%} "
          f"({n_recs - recs_movie_match} orphans out of {n_recs})")

    # Validate thresholds
    for name, rate in [
        ("watch_history user_id", watch_user_rate),
        ("watch_history movie_id", watch_movie_rate),
        ("recommendation_logs user_id", recs_user_rate),
        ("recommendation_logs movie_id", recs_movie_rate),
    ]:
        if rate < 0.80:
            raise ValueError(
                f"{name} join quality too low ({rate:.1%}) — "
                "KPI calculations may be invalid. Inspect dataset."
            )


if __name__ == "__main__":
    # Bypass st.cache_data when running standalone
    data = load_data.__wrapped__() if hasattr(load_data, "__wrapped__") else load_data()
    for name, df in data.items():
        print(f"{name}: {len(df)} rows, {df.shape[1]} cols")
        print(f"  Memory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
        print(f"  Columns: {df.columns.tolist()}")
    total_mb = sum(df.memory_usage(deep=True).sum() for df in data.values()) / 1e6
    print(f"\nTotal memory: {total_mb:.1f} MB")
    print(f"Memory target (<400MB): {'PASS' if total_mb < 400 else 'FAIL'}")
