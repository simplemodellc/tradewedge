"""Data validation utilities."""

import logging
from datetime import datetime, timedelta
from typing import List, Tuple

import pandas as pd

from app.data.schemas import OHLCVData, MarketDataSummary

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates historical market data quality."""

    @staticmethod
    def validate_ohlcv_dataframe(df: pd.DataFrame, ticker: str) -> Tuple[bool, List[str]]:
        """
        Validate OHLCV dataframe structure and data quality.

        Args:
            df: DataFrame with OHLCV data
            ticker: Ticker symbol

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: List[str] = []

        # Check for empty dataframe first
        if df.empty:
            errors.append("DataFrame is empty - no data available")
            return False, errors

        # Check required columns
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
            return False, errors

        # Check for NaN values
        nan_counts = df[required_columns].isna().sum()
        if nan_counts.any():
            for col, count in nan_counts.items():
                if count > 0:
                    errors.append(f"Column '{col}' has {count} NaN values")

        # Validate OHLC relationships
        invalid_high = df["High"] < df["Low"]
        if invalid_high.any():
            count = invalid_high.sum()
            errors.append(f"Found {count} records where High < Low")

        invalid_close_high = df["Close"] > df["High"]
        if invalid_close_high.any():
            count = invalid_close_high.sum()
            errors.append(f"Found {count} records where Close > High")

        invalid_close_low = df["Close"] < df["Low"]
        if invalid_close_low.any():
            count = invalid_close_low.sum()
            errors.append(f"Found {count} records where Close < Low")

        # Check for negative or zero prices
        price_columns = ["Open", "High", "Low", "Close"]
        for col in price_columns:
            invalid_prices = df[col] <= 0
            if invalid_prices.any():
                count = invalid_prices.sum()
                errors.append(f"Column '{col}' has {count} non-positive values")

        # Check for negative volume
        if (df["Volume"] < 0).any():
            count = (df["Volume"] < 0).sum()
            errors.append(f"Found {count} records with negative volume")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def check_missing_dates(df: pd.DataFrame, expected_frequency: str = "B") -> List[datetime]:
        """
        Check for missing dates in the time series.

        Args:
            df: DataFrame with DatetimeIndex
            expected_frequency: Expected frequency ('B' for business days, 'D' for daily)

        Returns:
            List of missing dates
        """
        if df.empty or not isinstance(df.index, pd.DatetimeIndex):
            return []

        start_date = df.index.min()
        end_date = df.index.max()

        # Generate expected date range
        expected_dates = pd.date_range(start=start_date, end=end_date, freq=expected_frequency)

        # Find missing dates
        missing_dates = expected_dates.difference(df.index)

        return missing_dates.to_pydatetime().tolist()

    @staticmethod
    def calculate_data_quality_score(
        df: pd.DataFrame, missing_dates: List[datetime]
    ) -> float:
        """
        Calculate a data quality score (0-100).

        Args:
            df: DataFrame with OHLCV data
            missing_dates: List of missing dates

        Returns:
            Quality score between 0 and 100
        """
        if df.empty:
            return 0.0

        score = 100.0

        # Penalize for NaN values
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        total_cells = len(df) * len(required_columns)
        nan_count = df[required_columns].isna().sum().sum()
        nan_penalty = (nan_count / total_cells) * 20 if total_cells > 0 else 0
        score -= nan_penalty

        # Penalize for missing dates
        if len(df) > 0:
            expected_days = (df.index.max() - df.index.min()).days
            missing_penalty = (len(missing_dates) / max(expected_days, 1)) * 30
            score -= missing_penalty

        # Penalize for invalid OHLC relationships
        invalid_count = 0
        invalid_count += (df["High"] < df["Low"]).sum()
        invalid_count += (df["Close"] > df["High"]).sum()
        invalid_count += (df["Close"] < df["Low"]).sum()
        invalid_penalty = (invalid_count / len(df)) * 50 if len(df) > 0 else 0
        score -= invalid_penalty

        return max(0.0, min(100.0, score))

    @staticmethod
    def create_summary(df: pd.DataFrame, ticker: str) -> MarketDataSummary:
        """
        Create a summary of the market data.

        Args:
            df: DataFrame with OHLCV data
            ticker: Ticker symbol

        Returns:
            MarketDataSummary object
        """
        if df.empty:
            return MarketDataSummary(
                ticker=ticker,
                start_date=datetime.now(),
                end_date=datetime.now(),
                total_records=0,
                missing_dates=0,
                data_quality_score=0.0,
            )

        missing_dates = DataValidator.check_missing_dates(df)
        quality_score = DataValidator.calculate_data_quality_score(df, missing_dates)

        return MarketDataSummary(
            ticker=ticker,
            start_date=df.index.min().to_pydatetime(),
            end_date=df.index.max().to_pydatetime(),
            total_records=len(df),
            missing_dates=len(missing_dates),
            data_quality_score=quality_score,
        )
