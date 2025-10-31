"""Pytest configuration and shared fixtures."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator
import tempfile

import pandas as pd
import pytest

from app.config import Settings


@pytest.fixture
def test_settings() -> Generator[Settings, None, None]:
    """Create test settings with temporary directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        settings = Settings(
            environment="test",
            debug=True,
            database_url=f"sqlite:///{tmpdir}/test.db",
            data_cache_dir=Path(tmpdir) / "cache",
            log_level="DEBUG",
        )
        yield settings


@pytest.fixture
def sample_ohlcv_data() -> pd.DataFrame:
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start="2023-01-01", end="2023-01-31", freq="B")
    data = {
        "Open": [100 + i for i in range(len(dates))],
        "High": [105 + i for i in range(len(dates))],
        "Low": [95 + i for i in range(len(dates))],
        "Close": [102 + i for i in range(len(dates))],
        "Volume": [1000000 + i * 10000 for i in range(len(dates))],
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"
    return df


@pytest.fixture
def invalid_ohlcv_data() -> pd.DataFrame:
    """Create invalid OHLCV data for testing validation."""
    dates = pd.date_range(start="2023-01-02", end="2023-01-11", freq="B")  # 8 business days
    data = {
        "Open": [100, 101, 102, 103, -5, 105, 106, 107],  # Negative value at index 4
        "High": [105, 106, 107, 98, 109, 110, 111, 112],  # High < Low at index 3 (98 < 99)
        "Low": [95, 96, 97, 99, 99, 100, 101, 102],
        "Close": [102, 103, 104, 105, 106, 107, 108, 109],
        "Volume": [1000000, 1010000, 1020000, 1030000, -1000, 1050000, 1060000, 1070000],  # Negative at index 4
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"
    return df


@pytest.fixture
def data_with_gaps() -> pd.DataFrame:
    """Create OHLCV data with missing dates."""
    # Create dates with gaps
    dates = []
    current = datetime(2023, 1, 2)  # Start on Monday
    for i in range(20):
        dates.append(current)
        # Skip some random days to create gaps
        if i in [3, 7, 12]:
            current += timedelta(days=5)  # Skip a week
        else:
            current += timedelta(days=1)

    data = {
        "Open": [100 + i for i in range(len(dates))],
        "High": [105 + i for i in range(len(dates))],
        "Low": [95 + i for i in range(len(dates))],
        "Close": [102 + i for i in range(len(dates))],
        "Volume": [1000000 + i * 10000 for i in range(len(dates))],
    }
    df = pd.DataFrame(data, index=pd.DatetimeIndex(dates))
    df.index.name = "Date"
    return df
