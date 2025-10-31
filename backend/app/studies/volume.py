"""Volume indicators implementation."""

from typing import Optional

import pandas as pd
import pandas_ta as ta

from .base import BaseIndicator


class OBV(BaseIndicator):
    """On-Balance Volume (OBV)."""

    def __init__(self):
        """Initialize OBV indicator."""
        super().__init__("OBV", {})

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate OBV on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with OBV column added
        """
        self.validate_dataframe(df, ["Close", "Volume"])
        result = df.copy()
        result["OBV"] = ta.obv(df["Close"], df["Volume"])
        return result


class VolumeSMA(BaseIndicator):
    """Volume Simple Moving Average."""

    def __init__(self, length: int = 20):
        """
        Initialize Volume SMA indicator.

        Args:
            length: Period length for volume moving average (default: 20)
        """
        super().__init__("VolumeSMA", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Volume SMA on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with Volume SMA column added
        """
        self.validate_dataframe(df, ["Volume"])
        result = df.copy()
        result[f"Volume_SMA_{self.length}"] = ta.sma(df["Volume"], length=self.length)
        return result


class VWAP(BaseIndicator):
    """Volume Weighted Average Price (VWAP)."""

    def __init__(self):
        """Initialize VWAP indicator."""
        super().__init__("VWAP", {})

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate VWAP on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with VWAP column added
        """
        self.validate_dataframe(df, ["High", "Low", "Close", "Volume"])
        result = df.copy()
        result["VWAP"] = ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"])
        return result


class MFI(BaseIndicator):
    """Money Flow Index (MFI)."""

    def __init__(self, length: int = 14):
        """
        Initialize MFI indicator.

        Args:
            length: Period length for MFI calculation (default: 14)
        """
        super().__init__("MFI", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MFI on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with MFI column added
        """
        self.validate_dataframe(df, ["High", "Low", "Close", "Volume"])
        result = df.copy()
        result[f"MFI_{self.length}"] = ta.mfi(
            df["High"], df["Low"], df["Close"], df["Volume"], length=self.length
        )
        return result


class AD(BaseIndicator):
    """Accumulation/Distribution (A/D) Line."""

    def __init__(self):
        """Initialize A/D indicator."""
        super().__init__("AD", {})

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate A/D on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with A/D column added
        """
        self.validate_dataframe(df, ["High", "Low", "Close", "Volume"])
        result = df.copy()
        result["AD"] = ta.ad(df["High"], df["Low"], df["Close"], df["Volume"])
        return result
