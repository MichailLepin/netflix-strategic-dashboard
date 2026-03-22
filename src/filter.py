"""Pure filter functions for the Netflix Strategic Dashboard.

Applies sidebar filter selections to the data dictionaries, returning
filtered copies of users, watch, and recs DataFrames.
"""

import pandas as pd


def apply_filters(
    data: dict[str, pd.DataFrame],
    genres: list[str],
    plans: list[str],
    devices: list[str],
    date_range: tuple,
) -> dict[str, pd.DataFrame]:
    """Return filtered copies of users, watch, recs DataFrames.

    Parameters
    ----------
    data : dict with keys users, movies, watch, recs (at minimum)
    genres : list of genre_primary values to keep (empty = all)
    plans : list of subscription_plan values to keep (empty = all)
    devices : list of device_type values to keep (empty = all)
    date_range : tuple of (start_date, end_date) or empty tuple for no filter

    Returns
    -------
    dict with keys: users, watch, recs — filtered copies
    """
    users = data["users"].copy()
    watch = data["watch"].copy()
    recs = data["recs"].copy()
    movies = data["movies"]

    # Genre filter: find matching movie_ids, then filter watch by those
    if genres:
        genre_movie_ids = set(
            movies.loc[movies["genre_primary"].isin(genres), "movie_id"]
        )
        watch = watch[watch["movie_id"].isin(genre_movie_ids)]
        recs = recs[recs["movie_id"].isin(genre_movie_ids)]

    # Subscription plan filter: filter users, then cascade to watch/recs
    if plans:
        users = users[users["subscription_plan"].isin(plans)]
        user_ids = set(users["user_id"])
        watch = watch[watch["user_id"].isin(user_ids)]
        recs = recs[recs["user_id"].isin(user_ids)]

    # Device type filter: filter watch rows
    if devices:
        watch = watch[watch["device_type"].isin(devices)]

    # Date range filter: filter watch rows by watch_date
    if len(date_range) == 2:
        start = pd.Timestamp(date_range[0])
        end = pd.Timestamp(date_range[1])
        watch = watch[(watch["watch_date"] >= start) & (watch["watch_date"] <= end)]

    return {"users": users, "watch": watch, "recs": recs}
