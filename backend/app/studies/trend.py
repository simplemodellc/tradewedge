"""Trend indicators implementation."""

from typing import Optional

import pandas as pd
import pandas_ta as ta

from .base import BaseIndicator


class SMA(BaseIndicator):
    """Simple Moving Average (SMA)."""

    def __init__(self, length: int = 20):
        """
        Initialize SMA indicator.

        Args:
            length: Period length for the moving average (default: 20)
        """
        super().__init__("SMA", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMA on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with SMA column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"SMA_{self.length}"] = ta.sma(df["Close"], length=self.length)
        return result


class EMA(BaseIndicator):
    """Exponential Moving Average (EMA)."""

    def __init__(self, length: int = 20):
        """
        Initialize EMA indicator.

        Args:
            length: Period length for the moving average (default: 20)
        """
        super().__init__("EMA", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate EMA on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with EMA column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"EMA_{self.length}"] = ta.ema(df["Close"], length=self.length)
        return result


class WMA(BaseIndicator):
    """Weighted Moving Average (WMA)."""

    def __init__(self, length: int = 20):
        """
        Initialize WMA indicator.

        Args:
            length: Period length for the moving average (default: 20)
        """
        super().__init__("WMA", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate WMA on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with WMA column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"WMA_{self.length}"] = ta.wma(df["Close"], length=self.length)
        return result


class DEMA(BaseIndicator):
    """Double Exponential Moving Average (DEMA)."""

    def __init__(self, length: int = 20):
        """
        Initialize DEMA indicator.

        Args:
            length: Period length for the moving average (default: 20)
        """
        super().__init__("DEMA", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate DEMA on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with DEMA column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"DEMA_{self.length}"] = ta.dema(df["Close"], length=self.length)
        return result


class TEMA(BaseIndicator):
    """Triple Exponential Moving Average (TEMA)."""

    def __init__(self, length: int = 20):
        """
        Initialize TEMA indicator.

        Args:
            length: Period length for the moving average (default: 20)
        """
        super().__init__("TEMA", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate TEMA on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with TEMA column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"TEMA_{self.length}"] = ta.tema(df["Close"], length=self.length)
        return result


class HMA(BaseIndicator):
    """Hull Moving Average (HMA)."""

    def __init__(self, length: int = 20):
        """
        Initialize HMA indicator.

        Args:
            length: Period length for the moving average (default: 20)
        """
        super().__init__("HMA", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate HMA on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with HMA column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"HMA_{self.length}"] = ta.hma(df["Close"], length=self.length)
        return result
