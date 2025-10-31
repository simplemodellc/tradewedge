"""Momentum indicators implementation."""

from typing import Optional

import pandas as pd
import pandas_ta as ta

from .base import BaseIndicator


class RSI(BaseIndicator):
    """Relative Strength Index (RSI)."""

    def __init__(self, length: int = 14):
        """
        Initialize RSI indicator.

        Args:
            length: Period length for RSI calculation (default: 14)
        """
        super().__init__("RSI", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with RSI column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"RSI_{self.length}"] = ta.rsi(df["Close"], length=self.length)
        return result


class MACD(BaseIndicator):
    """Moving Average Convergence Divergence (MACD)."""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """
        Initialize MACD indicator.

        Args:
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)
        """
        super().__init__("MACD", {"fast": fast, "slow": slow, "signal": signal})
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with MACD, MACD_signal, and MACD_histogram columns added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        macd = ta.macd(df["Close"], fast=self.fast, slow=self.slow, signal=self.signal)

        if macd is not None:
            # pandas_ta returns a DataFrame with columns like MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
            result[f"MACD_{self.fast}_{self.slow}_{self.signal}"] = macd.iloc[:, 0]
            result[f"MACDh_{self.fast}_{self.slow}_{self.signal}"] = macd.iloc[:, 1]
            result[f"MACDs_{self.fast}_{self.slow}_{self.signal}"] = macd.iloc[:, 2]

        return result


class Stochastic(BaseIndicator):
    """Stochastic Oscillator."""

    def __init__(self, k: int = 14, d: int = 3, smooth_k: int = 3):
        """
        Initialize Stochastic indicator.

        Args:
            k: Period for %K (default: 14)
            d: Period for %D (default: 3)
            smooth_k: Smoothing period for %K (default: 3)
        """
        super().__init__("Stochastic", {"k": k, "d": d, "smooth_k": smooth_k})
        self.k = k
        self.d = d
        self.smooth_k = smooth_k

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Stochastic on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with Stochastic %K and %D columns added
        """
        self.validate_dataframe(df, ["High", "Low", "Close"])
        result = df.copy()
        stoch = ta.stoch(
            df["High"], df["Low"], df["Close"], k=self.k, d=self.d, smooth_k=self.smooth_k
        )

        if stoch is not None:
            result[f"STOCHk_{self.k}_{self.d}_{self.smooth_k}"] = stoch.iloc[:, 0]
            result[f"STOCHd_{self.k}_{self.d}_{self.smooth_k}"] = stoch.iloc[:, 1]

        return result


class CCI(BaseIndicator):
    """Commodity Channel Index (CCI)."""

    def __init__(self, length: int = 20):
        """
        Initialize CCI indicator.

        Args:
            length: Period length for CCI calculation (default: 20)
        """
        super().__init__("CCI", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate CCI on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with CCI column added
        """
        self.validate_dataframe(df, ["High", "Low", "Close"])
        result = df.copy()
        result[f"CCI_{self.length}"] = ta.cci(
            df["High"], df["Low"], df["Close"], length=self.length
        )
        return result


class ROC(BaseIndicator):
    """Rate of Change (ROC)."""

    def __init__(self, length: int = 10):
        """
        Initialize ROC indicator.

        Args:
            length: Period length for ROC calculation (default: 10)
        """
        super().__init__("ROC", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ROC on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with ROC column added
        """
        self.validate_dataframe(df, ["Close"])
        result = df.copy()
        result[f"ROC_{self.length}"] = ta.roc(df["Close"], length=self.length)
        return result


class WilliamsR(BaseIndicator):
    """Williams %R."""

    def __init__(self, length: int = 14):
        """
        Initialize Williams %R indicator.

        Args:
            length: Period length for Williams %R calculation (default: 14)
        """
        super().__init__("WilliamsR", {"length": length})
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Williams %R on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with Williams %R column added
        """
        self.validate_dataframe(df, ["High", "Low", "Close"])
        result = df.copy()
        result[f"WILLR_{self.length}"] = ta.willr(
            df["High"], df["Low"], df["Close"], length=self.length
        )
        return result
