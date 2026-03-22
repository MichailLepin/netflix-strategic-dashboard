"""Data loader for Netflix 2025 User Behavior Dataset.

Loads, cleans, type-casts, join-validates, and caches all 6 CSV tables.
"""

import streamlit as st
import pandas as pd


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    """Load, clean, and return all 6 Netflix dataset tables.

    Returns a dict with keys: users, movies, watch, recs, searches, reviews
    """
    raise NotImplementedError("Task 2 implements this")
