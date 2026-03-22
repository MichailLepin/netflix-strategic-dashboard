"""Inject realistic patterns into the Netflix synthetic dataset.

Modifies CSV files in data/ to add:
1. Seasonal viewing spikes (holidays, summer)
2. Churn correlation with subscription plan (Basic churns more)
3. Recommendation effectiveness (clicked recs → longer watch sessions)
4. Genre preferences by device (Mobile → short content, Smart TV → movies)
5. Age-based content preferences
6. Time-based engagement trends (growing platform)

Run once: python fix_data.py
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
np.random.seed(42)


def fix_users(df: pd.DataFrame) -> pd.DataFrame:
    """Add realistic churn patterns."""
    # Basic users churn more (25%), Standard (15%), Premium (10%), Premium+ (5%)
    churn_rates = {"Basic": 0.28, "Standard": 0.16, "Premium": 0.09, "Premium+": 0.04}
    for plan, rate in churn_rates.items():
        mask = df["subscription_plan"] == plan
        n = mask.sum()
        # Reset is_active based on realistic churn rate
        active = np.random.random(n) > rate
        df.loc[mask, "is_active"] = active

    # Younger users (18-25) churn more (+8%), older (55+) churn less (-5%)
    young = df["age"] <= 25
    old = df["age"] >= 55
    # Flip some active young users to churned
    young_active = df.index[young & df["is_active"]]
    flip_count = int(len(young_active) * 0.08)
    if flip_count > 0:
        flip_idx = np.random.choice(young_active, flip_count, replace=False)
        df.loc[flip_idx, "is_active"] = False

    # Flip some churned old users to active
    old_churned = df.index[old & ~df["is_active"]]
    flip_count = int(len(old_churned) * 0.4)
    if flip_count > 0:
        flip_idx = np.random.choice(old_churned, flip_count, replace=False)
        df.loc[flip_idx, "is_active"] = True

    # Higher monthly spend for Premium/Premium+
    df.loc[df["subscription_plan"] == "Premium+", "monthly_spend"] *= 1.4
    df.loc[df["subscription_plan"] == "Premium", "monthly_spend"] *= 1.15
    df.loc[df["subscription_plan"] == "Basic", "monthly_spend"] *= 0.7

    return df


def fix_watch_history(df: pd.DataFrame, users: pd.DataFrame, movies: pd.DataFrame) -> pd.DataFrame:
    """Add seasonal patterns, device preferences, and engagement trends."""

    # 1. Seasonal viewing spikes
    df["month"] = df["watch_date"].dt.month
    # December/January: +30% watch time (holidays)
    holiday = df["month"].isin([12, 1])
    df.loc[holiday, "watch_duration_minutes"] *= np.random.uniform(1.2, 1.5, holiday.sum())
    # July/August: +15% (summer binge)
    summer = df["month"].isin([7, 8])
    df.loc[summer, "watch_duration_minutes"] *= np.random.uniform(1.05, 1.25, summer.sum())
    # February: -10% (short month, less watching)
    feb = df["month"] == 2
    df.loc[feb, "watch_duration_minutes"] *= np.random.uniform(0.8, 0.95, feb.sum())

    # 2. Device-based watch patterns
    # Mobile: shorter sessions (0.6x), Smart TV: longer sessions (1.4x)
    mobile = df["device_type"] == "Mobile"
    df.loc[mobile, "watch_duration_minutes"] *= 0.6
    smarttv = df["device_type"] == "Smart TV"
    df.loc[smarttv, "watch_duration_minutes"] *= 1.4
    tablet = df["device_type"] == "Tablet"
    df.loc[tablet, "watch_duration_minutes"] *= 0.85

    # 3. Premium users watch more
    premium_users = set(users[users["subscription_plan"].isin(["Premium", "Premium+"])]["user_id"])
    basic_users = set(users[users["subscription_plan"] == "Basic"]["user_id"])
    df.loc[df["user_id"].isin(premium_users), "watch_duration_minutes"] *= 1.25
    df.loc[df["user_id"].isin(basic_users), "watch_duration_minutes"] *= 0.75

    # 4. Completion rate varies by content type
    movie_ids = set(movies[movies["content_type"] == "Movie"]["movie_id"])
    doc_ids = set(movies[movies["content_type"] == "Documentary"]["movie_id"])
    # Movies: higher completion
    movie_mask = df["movie_id"].isin(movie_ids)
    df.loc[movie_mask, "progress_percentage"] = df.loc[movie_mask, "progress_percentage"].clip(lower=30) * 1.1
    # Documentaries: lower completion
    doc_mask = df["movie_id"].isin(doc_ids)
    df.loc[doc_mask, "progress_percentage"] *= 0.75

    # 5. Growing platform trend (later months have slightly more engagement)
    df["days_since_start"] = (df["watch_date"] - df["watch_date"].min()).dt.days
    max_days = df["days_since_start"].max()
    growth_factor = 1 + (df["days_since_start"] / max_days) * 0.2  # up to 20% growth
    df["watch_duration_minutes"] *= growth_factor

    # Clip to reasonable values
    df["watch_duration_minutes"] = df["watch_duration_minutes"].clip(5, 300).round(1)
    df["progress_percentage"] = df["progress_percentage"].clip(0, 100).round(1)

    # Clean up temp columns
    df.drop(columns=["month", "days_since_start"], inplace=True)

    return df


def fix_recommendations(df: pd.DataFrame, watch: pd.DataFrame) -> pd.DataFrame:
    """Make recommendation effectiveness realistic."""

    # 1. Position matters: top positions get more clicks
    # Position 1: 35% CTR, Position 20: 5% CTR
    df["position_in_list"] = df["position_in_list"].astype(int)
    max_pos = df["position_in_list"].max()
    # Calculate click probability based on position
    click_prob = 0.35 - (df["position_in_list"] - 1) / max_pos * 0.30
    df["was_clicked"] = np.random.random(len(df)) < click_prob

    # 2. Personalized recs have higher CTR than generic
    personalized = df["recommendation_type"] == "personalized"
    df.loc[personalized, "was_clicked"] = np.random.random(personalized.sum()) < 0.28

    genre_based = df["recommendation_type"] == "genre_based"
    df.loc[genre_based, "was_clicked"] = np.random.random(genre_based.sum()) < 0.22

    trending = df["recommendation_type"] == "trending"
    df.loc[trending, "was_clicked"] = np.random.random(trending.sum()) < 0.18

    new_releases = df["recommendation_type"] == "new_releases"
    df.loc[new_releases, "was_clicked"] = np.random.random(new_releases.sum()) < 0.15

    similar = df["recommendation_type"] == "similar_users"
    df.loc[similar, "was_clicked"] = np.random.random(similar.sum()) < 0.12

    # 3. Algorithm v2.0 is better than v1.x
    v2 = df["algorithm_version"] == "v2.0"
    v2_clicked = df.loc[v2].index
    # Boost v2 CTR by flipping 10% of non-clicks to clicks
    v2_not_clicked = df.loc[v2 & ~df["was_clicked"]].index
    boost = np.random.choice(v2_not_clicked, size=int(len(v2_not_clicked) * 0.10), replace=False)
    df.loc[boost, "was_clicked"] = True

    return df


def main():
    print("Loading data...")
    users = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    watch = pd.read_csv(os.path.join(DATA_DIR, "watch_history.csv"), parse_dates=["watch_date"])
    movies = pd.read_csv(os.path.join(DATA_DIR, "movies.csv"))
    recs = pd.read_csv(os.path.join(DATA_DIR, "recommendation_logs.csv"))

    print("Fixing users (churn patterns)...")
    users = fix_users(users)

    print("Fixing watch history (seasonal, device, engagement)...")
    watch = fix_watch_history(watch, users, movies)

    print("Fixing recommendations (position, type, algorithm effectiveness)...")
    recs = fix_recommendations(recs, watch)

    print("Saving...")
    users.to_csv(os.path.join(DATA_DIR, "users.csv"), index=False)
    watch.to_csv(os.path.join(DATA_DIR, "watch_history.csv"), index=False)
    recs.to_csv(os.path.join(DATA_DIR, "recommendation_logs.csv"), index=False)

    # Verify
    print("\n=== Verification ===")
    print(f"Churn by plan:")
    for plan in ["Basic", "Standard", "Premium", "Premium+"]:
        rate = (~users[users["subscription_plan"]==plan]["is_active"]).mean() * 100
        print(f"  {plan}: {rate:.1f}%")

    print(f"\nWatch time by device:")
    for dev in watch["device_type"].unique():
        avg = watch[watch["device_type"]==dev]["watch_duration_minutes"].mean() / 60
        print(f"  {dev}: {avg:.2f} hrs")

    print(f"\nRec CTR by type:")
    for rtype in recs["recommendation_type"].unique():
        ctr = recs[recs["recommendation_type"]==rtype]["was_clicked"].mean() * 100
        print(f"  {rtype}: {ctr:.1f}%")

    print(f"\nRec CTR by position (top 5 vs bottom 5):")
    top5 = recs[recs["position_in_list"] <= 5]["was_clicked"].mean() * 100
    bot5 = recs[recs["position_in_list"] >= 16]["was_clicked"].mean() * 100
    print(f"  Top 5: {top5:.1f}%")
    print(f"  Bottom 5: {bot5:.1f}%")

    print("\nDone! Data fixed.")


if __name__ == "__main__":
    main()
