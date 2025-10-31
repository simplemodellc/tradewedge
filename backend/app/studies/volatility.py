"""Volatility indicators implementation."""

from typing import Optional

import pandas as pd
import pandas_ta as ta

from .base import BaseIndicator


class BollingerBands(BaseIndicator):
    """Bollinger Bands."""

    def __init__(self, length: int = 20, std: float = 2.0):
        """
        Initialize Bollinger Bands indicator.

        Args:
            length: Period length for moving average (default: 20)
            std: Number of standard deviations (default: 2.0)
        """
        super().__init__("BollingerBands", {"length": length, "std": std})
        self.length = length
        self.std = std

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with BB upper, middle, and lower bands added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        bbands = ta.bbands(df["Close"], length=self.length, std=self.std)

        if bbands is not None:
            # pandas_ta returns BBL_length_std, BBM_length_std, BBU_length_std, BBB_length_std, BBP_length_std
            result[f"BBL_{self.length}_{self.std}"] = bbands.iloc[:, 0]  # Lower band
            result[f"BBM_{self.length}_{self.std}"] = bbands.iloc[:, 1]  # Middle band
            result[f"BBU_{self.length}_{self.std}"] = bbands.iloc[:, 2]  # Upper band
            result[f"BBB_{self.length}_{self.std}"] = bbands.iloc[:, 3]  # Bandwidth
            result[f"BBP_{self.length}_{self.std}"] = bbands.iloc[:, 4]  # Percent B

        return result


class ATR(BaseIndicator):
    """Average True Range (ATR)."""

    def __init__(self, length: int = 14):
        """
        Initialize ATR indicator.

        Args:
            length: Period length for ATR calculation (default: 14)
        """
        super().__init__("ATR", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ATR on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with ATR column added
        """
        self.validate_dataframe(df, ["High", "Low", "Close"])
        result = df.copy()
        result[f"ATR_{self.length}"] = ta.atr(
            df["High"], df["Low"], df["Close"], length=self.length
        )
        return result


class KeltnerChannels(BaseIndicator):
    """Keltner Channels."""

    def __init__(self, length: int = 20, scalar: float = 2.0):
        """
        Initialize Keltner Channels indicator.

        Args:
            length: Period length for EMA (default: 20)
            scalar: ATR multiplier (default: 2.0)
        """
        super().__init__("KeltnerChannels", {"length": length, "scalar": scalar})
        self.length = length
        self.scalar = scalar

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Keltner Channels on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with KC upper, basis, and lower bands added
        """
        self.validate_dataframe(df, ["High", "Low", "Close"])
        result = df.copy()
        kc = ta.kc(
            df["High"], df["Low"], df["Close"], length=self.length, scalar=self.scalar
        )

        if kc is not None:
            # pandas_ta returns KCL_length_scalar, KCB_length_scalar, KCU_length_scalar
            result[f"KCL_{self.length}_{self.scalar}"] = kc.iloc[:, 0]  # Lower band
            result[f"KCB_{self.length}_{self.scalar}"] = kc.iloc[:, 1]  # Basis (middle)
            result[f"KCU_{self.length}_{self.scalar}"] = kc.iloc[:, 2]  # Upper band

        return result


class StandardDeviation(BaseIndicator):
    """Standard Deviation."""

    def __init__(self, length: int = 20):
        """
        Initialize Standard Deviation indicator.

        Args:
            length: Period length for standard deviation (default: 20)
        """
        super().__init__("StandardDeviation", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Standard Deviation on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with Standard Deviation column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"STDEV_{self.length}"] = ta.stdev(df["Close"], length=self.length)
        return result
