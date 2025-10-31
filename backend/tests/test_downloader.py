"""Tests for VTSAX data downloader."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from app.data.downloader import VTSAXDownloader


class TestVTSAXDownloader:
    """Test suite for VTSAXDownloader."""

    @pytest.fixture
    def downloader(self, test_settings, tmp_path):
        """Create downloader instance with test settings."""
        return VTSAXDownloader(cache_dir=tmp_path / "cache")

    def test_init(self, downloader, tmp_path):
        """Test downloader initialization."""
        assert downloader.ticker == "VTSAX"
        assert downloader.cache_dir.exists()
        assert downloader.validator is not None

    def test_get_cache_path(self, downloader):
        """Test cache path generation."""
        cache_path = downloader._get_cache_path()

        assert cache_path.name == "vtsax_historical.parquet"
        assert cache_path.parent == downloader.cache_dir

    def test_save_and_load_cache(self, downloader, sample_ohlcv_data):
        """Test saving and loading data from cache."""
        # Save to cache
        downloader._save_to_cache(sample_ohlcv_data)

        # Load from cache
        loaded_df = downloader._load_from_cache()

        assert loaded_df is not None
        assert len(loaded_df) == len(sample_ohlcv_data)
        # Check without frequency attribute as parquet doesn't preserve it
        pd.testing.assert_frame_equal(loaded_df, sample_ohlcv_data, check_freq=False)

    def test_load_from_cache_no_file(self, downloader):
        """Test loading from cache when file doesn't exist."""
        loaded_df = downloader._load_from_cache()

        assert loaded_df is None

    @patch("app.data.downloader.yf.Ticker")
    def test_download_success(self, mock_ticker, downloader, sample_ohlcv_data):
        """Test successful data download."""
        # Mock yfinance response
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance

        # Download data
        df = downloader.download(force_refresh=True)

        assert df is not None
        assert len(df) > 0
        assert all(col in df.columns for col in ["Open", "High", "Low", "Close", "Volume"])

    @patch("app.data.downloader.yf.Ticker")
    def test_download_empty_response(self, mock_ticker, downloader):
        """Test download with empty response."""
        # Mock empty response
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance

        # Should raise ValueError
        with pytest.raises(ValueError, match="No data returned"):
            downloader.download(force_refresh=True)

    @patch("app.data.downloader.yf.Ticker")
    def test_download_with_date_range(self, mock_ticker, downloader, sample_ohlcv_data):
        """Test download with specific date range."""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)

        df = downloader.download(start_date=start_date, end_date=end_date, force_refresh=True)

        assert df is not None
        # Verify yfinance was called with correct dates
        mock_ticker_instance.history.assert_called_once()
        call_kwargs = mock_ticker_instance.history.call_args.kwargs
        assert call_kwargs["start"] == start_date
        assert call_kwargs["end"] == end_date

    def test_download_uses_cache(self, downloader, sample_ohlcv_data):
        """Test that download uses cache when available."""
        # Save to cache first
        downloader._save_to_cache(sample_ohlcv_data)

        # Download without force_refresh should use cache
        with patch("app.data.downloader.yf.Ticker") as mock_ticker:
            df = downloader.download()

            # yfinance should not be called
            mock_ticker.assert_not_called()
            assert df is not None
            assert len(df) == len(sample_ohlcv_data)

    @patch("app.data.downloader.yf.Ticker")
    def test_get_summary(self, mock_ticker, downloader, sample_ohlcv_data):
        """Test getting data summary."""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance

        summary = downloader.get_summary(df=sample_ohlcv_data)

        assert summary.ticker == "VTSAX"
        assert summary.total_records == len(sample_ohlcv_data)
        assert summary.data_quality_score >= 0

    @patch("app.data.downloader.yf.Ticker")
    def test_refresh_data(self, mock_ticker, downloader, sample_ohlcv_data):
        """Test data refresh."""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = sample_ohlcv_data
        mock_ticker.return_value = mock_ticker_instance

        df = downloader.refresh_data()

        assert df is not None
        # Should have saved to cache
        assert downloader._get_cache_path().exists()

    @patch("app.data.downloader.yf.Ticker")
    def test_download_handles_timezone(self, mock_ticker, downloader):
        """Test that download removes timezone info."""
        # Create data with timezone
        dates = pd.date_range(start="2023-01-01", end="2023-01-10", freq="B", tz="UTC")
        tz_data = pd.DataFrame(
            {
                "Open": [100 + i for i in range(len(dates))],
                "High": [105 + i for i in range(len(dates))],
                "Low": [95 + i for i in range(len(dates))],
                "Close": [102 + i for i in range(len(dates))],
                "Volume": [1000000 + i * 10000 for i in range(len(dates))],
            },
            index=dates,
        )

        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = tz_data
        mock_ticker.return_value = mock_ticker_instance

        df = downloader.download(force_refresh=True)

        # Index should not have timezone
        assert df.index.tz is None
