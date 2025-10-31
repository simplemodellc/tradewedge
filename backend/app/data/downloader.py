"""Historical market data downloader."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

from app.config import get_settings
from app.data.validator import DataValidator
from app.data.schemas import MarketDataSummary

logger = logging.getLogger(__name__)
settings = get_settings()


class VTSAXDownloader:
    """Downloads and caches VTSAX historical data."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize downloader.

        Args:
            cache_dir: Directory for cached data files
        """
        self.cache_dir = cache_dir or settings.data_cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ticker = settings.vtsax_ticker
        self.validator = DataValidator()

    def _get_cache_path(self) -> Path:
        """Get path to cached data file."""
        return self.cache_dir / f"{self.ticker.lower()}_historical.parquet"

    def _load_from_cache(self) -> Optional[pd.DataFrame]:
        """
        Load data from cache file.

        Returns:
            DataFrame if cache exists and is valid, None otherwise
        """
        cache_path = self._get_cache_path()

        if not cache_path.exists():
            logger.info(f"No cache file found at {cache_path}")
            return None

        try:
            df = pd.read_parquet(cache_path)
            df.index = pd.to_datetime(df.index)
            logger.info(f"Loaded {len(df)} records from cache")
            return df
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None

    def _save_to_cache(self, df: pd.DataFrame) -> None:
        """
        Save data to cache file.

        Args:
            df: DataFrame to cache
        """
        cache_path = self._get_cache_path()
        try:
            df.to_parquet(cache_path)
            logger.info(f"Saved {len(df)} records to cache at {cache_path}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def download(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Download VTSAX historical data.

        Args:
            start_date: Start date for data (None = from inception)
            end_date: End date for data (None = today)
            force_refresh: Force download even if cache exists

        Returns:
            DataFrame with OHLCV data

        Raises:
            ValueError: If data download or validation fails
        """
        # Try to load from cache first
        if not force_refresh:
            cached_df = self._load_from_cache()
            if cached_df is not None:
                # Filter by date range if specified
                if start_date or end_date:
                    mask = pd.Series(True, index=cached_df.index)
                    if start_date:
                        mask &= cached_df.index >= start_date
                    if end_date:
                        mask &= cached_df.index <= end_date
                    return cached_df[mask]
                return cached_df

        # Download from yfinance
        logger.info(f"Downloading {self.ticker} data from yfinance...")

        try:
            ticker_obj = yf.Ticker(self.ticker)

            # Download all available historical data if no dates specified
            if start_date is None:
                start_date = datetime(2000, 1, 1)  # VTSAX inception
            if end_date is None:
                end_date = datetime.now()

            df = ticker_obj.history(
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=True,  # Use adjusted prices
            )

            if df.empty:
                raise ValueError(f"No data returned for {self.ticker}")

            # Ensure index is datetime
            df.index = pd.to_datetime(df.index)

            # Remove timezone info for consistency
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)

            logger.info(f"Downloaded {len(df)} records for {self.ticker}")

            # Validate data
            is_valid, errors = self.validator.validate_ohlcv_dataframe(df, self.ticker)
            if not is_valid:
                logger.warning(f"Data validation found issues: {errors}")
                # Don't raise error, just log warnings for now
                # This allows us to work with slightly imperfect data

            # Save to cache
            self._save_to_cache(df)

            return df

        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            raise ValueError(f"Failed to download {self.ticker} data: {e}")

    def get_summary(self, df: Optional[pd.DataFrame] = None) -> MarketDataSummary:
        """
        Get summary statistics for the data.

        Args:
            df: DataFrame to summarize (None = load from cache)

        Returns:
            MarketDataSummary object
        """
        if df is None:
            df = self._load_from_cache()
            if df is None:
                df = self.download()

        return self.validator.create_summary(df, self.ticker)

    def refresh_data(self) -> pd.DataFrame:
        """
        Refresh cached data with latest available data.

        Returns:
            Updated DataFrame
        """
        logger.info("Refreshing VTSAX data...")
        return self.download(force_refresh=True)
