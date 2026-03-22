"""Deep enrichment of Netflix synthetic dataset with realistic industry patterns.

Makes the data tell a real business story:
- Netflix-realistic KPI baselines (completion ~65%, churn ~6%, CTR ~22%)
- Meaningful variance across segments that drives actionable insights
- Seasonal patterns visible in time trends
- Clear recommendation algorithm effectiveness differences

Run once: python fix_data.py
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Use backup of original Kaggle data if available, otherwise use current
BACKUP_DIR = os.path.join(DATA_DIR, "original_kaggle")

np.random.seed(42)


def fix_users(df: pd.DataFrame) -> pd.DataFrame:
    """Realistic churn and spend patterns."""

    # Realistic churn by plan (monthly churn, Netflix industry norms)
    churn_rates = {"Basic": 0.12, "Standard": 0.06, "Premium": 0.03, "Premium+": 0.015}
    for plan, rate in churn_rates.items():
        mask = df["subscription_plan"] == plan
        n = mask.sum()
        df.loc[mask, "is_active"] = np.random.random(n) > rate

    # Age affects churn: young adults (18-25) churn 2x more
    young = df["age"] <= 25
    young_active = df.index[young & df["is_active"]]
    flip = int(len(young_active) * 0.06)
    if flip > 0:
        df.loc[np.random.choice(young_active, flip, replace=False), "is_active"] = False

    # Older users (55+) more loyal
    old_churned = df.index[(df["age"] >= 55) & ~df["is_active"]]
    flip = int(len(old_churned) * 0.5)
    if flip > 0:
        df.loc[np.random.choice(old_churned, flip, replace=False), "is_active"] = True

    # Realistic monthly spend by plan
    spend_map = {"Basic": (9.99, 2.0), "Standard": (15.49, 3.0),
                 "Premium": (22.99, 4.0), "Premium+": (29.99, 5.0)}
    for plan, (mean, std) in spend_map.items():
        mask = df["subscription_plan"] == plan
        df.loc[mask, "monthly_spend"] = np.random.normal(mean, std, mask.sum()).clip(5, 50).round(2)

    return df


def fix_watch_history(df: pd.DataFrame, users: pd.DataFrame, movies: pd.DataFrame) -> pd.DataFrame:
    """Realistic viewing patterns."""
    df["month"] = df["watch_date"].dt.month

    # --- Base watch duration: realistic Netflix average ~90 min per session ---
    # But with high variance (some short mobile checks, some binge sessions)
    base_duration = np.random.lognormal(mean=4.2, sigma=0.6, size=len(df))  # median ~67 min
    df["watch_duration_minutes"] = base_duration.clip(5, 300).round(1)

    # --- Seasonal patterns ---
    # Holiday surge: Dec +40%, Jan +20%
    dec = df["month"] == 12
    df.loc[dec, "watch_duration_minutes"] *= np.random.uniform(1.3, 1.5, dec.sum())
    jan = df["month"] == 1
    df.loc[jan, "watch_duration_minutes"] *= np.random.uniform(1.1, 1.3, jan.sum())
    # Summer boost: Jul-Aug +15%
    summer = df["month"].isin([7, 8])
    df.loc[summer, "watch_duration_minutes"] *= np.random.uniform(1.05, 1.25, summer.sum())
    # Post-holiday dip: Feb -15%
    feb = df["month"] == 2
    df.loc[feb, "watch_duration_minutes"] *= np.random.uniform(0.75, 0.9, feb.sum())
    # Spring dip: Apr -10%
    apr = df["month"] == 4
    df.loc[apr, "watch_duration_minutes"] *= np.random.uniform(0.85, 0.95, apr.sum())

    # --- Device patterns ---
    mobile = df["device_type"] == "Mobile"
    df.loc[mobile, "watch_duration_minutes"] *= 0.5  # Mobile = short sessions
    smarttv = df["device_type"] == "Smart TV"
    df.loc[smarttv, "watch_duration_minutes"] *= 1.6  # Smart TV = long lean-back
    tablet = df["device_type"] == "Tablet"
    df.loc[tablet, "watch_duration_minutes"] *= 0.75

    # --- Subscription tier engagement ---
    premium_users = set(users[users["subscription_plan"].isin(["Premium", "Premium+"])]["user_id"])
    basic_users = set(users[users["subscription_plan"] == "Basic"]["user_id"])
    df.loc[df["user_id"].isin(premium_users), "watch_duration_minutes"] *= 1.3
    df.loc[df["user_id"].isin(basic_users), "watch_duration_minutes"] *= 0.7

    # --- Genre engagement differences ---
    genre_map = movies.set_index("movie_id")["genre_primary"].to_dict()
    df["_genre"] = df["movie_id"].map(genre_map)

    # Some genres are more engaging
    high_engagement = ["Thriller", "Sci-Fi", "Drama", "Mystery", "Crime"]
    low_engagement = ["Documentary", "Music", "Sport", "History"]
    high_mask = df["_genre"].isin(high_engagement)
    low_mask = df["_genre"].isin(low_engagement)
    df.loc[high_mask, "watch_duration_minutes"] *= 1.25
    df.loc[low_mask, "watch_duration_minutes"] *= 0.7

    # --- Completion rate: realistic ~65% overall ---
    # Higher for movies, lower for TV series (people start and don't finish)
    content_map = movies.set_index("movie_id")["content_type"].to_dict()
    df["_content"] = df["movie_id"].map(content_map)

    # Base completion: bimodal — most people either watch most of it or drop early
    # 70% of viewers complete (>90%), 30% drop off earlier
    completers = np.random.random(len(df)) < 0.88
    progress = np.where(
        completers,
        np.random.normal(95, 5, len(df)),   # completers: avg 95%, tight spread
        np.random.normal(40, 20, len(df)),  # dropoffs: avg 40%
    )
    df["progress_percentage"] = np.clip(progress, 0, 100).round(1)

    # Movies: +10% completion (designed for single sitting)
    movie_mask = df["_content"] == "Movie"
    df.loc[movie_mask, "progress_percentage"] = (
        df.loc[movie_mask, "progress_percentage"] * 1.1
    ).clip(0, 100).round(1)

    # TV Series: slightly lower completion (serial fatigue)
    tv_mask = df["_content"] == "TV Series"
    df.loc[tv_mask, "progress_percentage"] = (
        df.loc[tv_mask, "progress_percentage"] * 0.92
    ).clip(0, 100).round(1)

    # Documentaries: lower completion (less sticky)
    doc_mask = df["_content"] == "Documentary"
    df.loc[doc_mask, "progress_percentage"] = (
        df.loc[doc_mask, "progress_percentage"] * 0.85
    ).clip(0, 100).round(1)

    # Smart TV users complete more (lean-back, committed viewing)
    df.loc[smarttv, "progress_percentage"] = (
        df.loc[smarttv, "progress_percentage"] * 1.15
    ).clip(0, 100).round(1)
    # Mobile users complete less (interrupted viewing)
    df.loc[mobile, "progress_percentage"] = (
        df.loc[mobile, "progress_percentage"] * 0.88
    ).clip(0, 100).round(1)

    # --- Platform growth trend ---
    df["_days"] = (df["watch_date"] - df["watch_date"].min()).dt.days
    max_days = df["_days"].max()
    if max_days > 0:
        growth = 1 + (df["_days"] / max_days) * 0.25
        df["watch_duration_minutes"] *= growth

    # Final clipping
    df["watch_duration_minutes"] = df["watch_duration_minutes"].clip(3, 360).round(1)
    df["progress_percentage"] = df["progress_percentage"].clip(0, 100).round(1)

    # Clean temp columns
    df.drop(columns=["month", "_genre", "_content", "_days"], inplace=True)

    return df


def fix_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """Realistic recommendation effectiveness patterns."""

    # --- Position bias: top positions get WAY more clicks ---
    pos = df["position_in_list"].astype(int)
    max_pos = pos.max()
    # Exponential decay: position 1 → ~40% CTR, position 20 → ~5%
    click_prob = 0.40 * np.exp(-0.15 * (pos - 1))
    df["was_clicked"] = np.random.random(len(df)) < click_prob

    # --- Algorithm type effectiveness ---
    type_ctr = {
        "personalized": 0.35,    # Best: tailored to user
        "genre_based": 0.25,     # Good: matches preferences
        "trending": 0.20,        # OK: social proof
        "new_releases": 0.15,    # Mediocre: not targeted
        "similar_users": 0.10,   # Worst: cold-start problem
    }
    for rtype, ctr in type_ctr.items():
        mask = df["recommendation_type"] == rtype
        df.loc[mask, "was_clicked"] = np.random.random(mask.sum()) < ctr

    # --- Algorithm v2.0 is 20% better than v1.x ---
    v2 = df["algorithm_version"] == "v2.0"
    v2_not_clicked = df.loc[v2 & ~df["was_clicked"]].index
    boost = int(len(v2_not_clicked) * 0.15)
    if boost > 0:
        df.loc[np.random.choice(v2_not_clicked, boost, replace=False), "was_clicked"] = True

    # --- Time-of-day effect ---
    if "time_of_day" in df.columns:
        # Evening recs get more clicks (prime time, user is browsing)
        evening = df["time_of_day"].isin(["Evening", "Night"])
        evening_not_clicked = df.loc[evening & ~df["was_clicked"]].index
        boost = int(len(evening_not_clicked) * 0.08)
        if boost > 0:
            df.loc[np.random.choice(evening_not_clicked, boost, replace=False), "was_clicked"] = True

    return df


def main():
    print("Loading original Kaggle data...")
    users = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    watch = pd.read_csv(os.path.join(DATA_DIR, "watch_history.csv"), parse_dates=["watch_date"])
    movies = pd.read_csv(os.path.join(DATA_DIR, "movies.csv"))
    recs = pd.read_csv(os.path.join(DATA_DIR, "recommendation_logs.csv"))

    print("Fixing users (realistic churn + spend)...")
    users = fix_users(users)

    print("Fixing watch history (seasonal, device, genre, completion)...")
    watch = fix_watch_history(watch, users, movies)

    print("Fixing recommendations (position bias, algorithm effectiveness)...")
    recs = fix_recommendations(recs)

    print("Saving...")
    users.to_csv(os.path.join(DATA_DIR, "users.csv"), index=False)
    watch.to_csv(os.path.join(DATA_DIR, "watch_history.csv"), index=False)
    recs.to_csv(os.path.join(DATA_DIR, "recommendation_logs.csv"), index=False)

    # === VERIFICATION ===
    print("\n" + "=" * 60)
    print("VERIFICATION — Realistic Netflix KPIs")
    print("=" * 60)

    avg_watch = watch["watch_duration_minutes"].mean() / 60
    print(f"\nAvg Watch Time per session: {avg_watch:.1f} hrs (target: 1.5-2.5 hrs)")

    completion = (watch["progress_percentage"] >= 90).mean() * 100
    print(f"Completion Rate (>=90%): {completion:.1f}% (target: 55-70%)")

    ctr = recs["was_clicked"].mean() * 100
    print(f"Recommendation CTR: {ctr:.1f}% (target: 20-30%)")

    churn = (~users["is_active"]).mean() * 100
    print(f"Churn Rate: {churn:.1f}% (target: 4-8%)")

    print(f"\nChurn by plan:")
    for plan in ["Basic", "Standard", "Premium", "Premium+"]:
        r = (~users[users["subscription_plan"] == plan]["is_active"]).mean() * 100
        print(f"  {plan}: {r:.1f}%")

    print(f"\nWatch time by device (avg hrs):")
    for dev in sorted(watch["device_type"].unique()):
        h = watch[watch["device_type"] == dev]["watch_duration_minutes"].mean() / 60
        print(f"  {dev}: {h:.2f} hrs")

    print(f"\nCompletion by content type:")
    content_map = movies.set_index("movie_id")["content_type"].to_dict()
    watch["_ct"] = watch["movie_id"].map(content_map)
    for ct in ["Movie", "TV Series", "Documentary", "Stand-up Comedy", "Limited Series"]:
        mask = watch["_ct"] == ct
        if mask.any():
            comp = (watch.loc[mask, "progress_percentage"] >= 90).mean() * 100
            print(f"  {ct}: {comp:.1f}%")

    print(f"\nRec CTR by type:")
    for rt in ["personalized", "genre_based", "trending", "new_releases", "similar_users"]:
        c = recs[recs["recommendation_type"] == rt]["was_clicked"].mean() * 100
        print(f"  {rt}: {c:.1f}%")

    print(f"\nRec CTR by algorithm version:")
    for v in sorted(recs["algorithm_version"].dropna().unique()):
        c = recs[recs["algorithm_version"] == v]["was_clicked"].mean() * 100
        print(f"  {v}: {c:.1f}%")

    print(f"\nTop 5 genres by total watch hours:")
    genre_map = movies.set_index("movie_id")["genre_primary"].to_dict()
    watch["_genre"] = watch["movie_id"].map(genre_map)
    gh = watch.groupby("_genre")["watch_duration_minutes"].sum() / 60
    for g, h in gh.sort_values(ascending=False).head(5).items():
        print(f"  {g}: {h:,.0f} hrs")

    print("\n✓ Data enrichment complete.")


if __name__ == "__main__":
    main()
