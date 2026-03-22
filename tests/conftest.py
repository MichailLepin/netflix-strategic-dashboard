import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.data_loader import load_data


@pytest.fixture(scope="session")
def data():
    return load_data()
