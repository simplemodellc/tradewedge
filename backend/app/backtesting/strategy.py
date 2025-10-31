"""Trading strategy implementations."""

from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd

from .schemas import Signal, SignalType


class BaseStrategy(ABC):
    """Base class for all trading strategies."""

    def __init__(self, name: str, params: Dict = None):
        """
        Initialize strategy.

        Args:
            name: Strategy name
            params: Strategy parameters
        """
        self.name = name
        self.params = params or {}

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals from OHLCV data.

        Args:
            df: DataFrame with OHLCV data and any indicators

        Returns:
            List of Signal objects
        """
        pass

    def get_description(self) -> str:
        """Get strategy description."""
        return f"{self.name} with params: {self.params}"


class BuyAndHoldStrategy(BaseStrategy):
    """
    Buy and hold strategy.

    Buys on the first day and holds until the end.
    """

    def __init__(self):
        """Initialize buy and hold strategy."""
        super().__init__("BuyAndHold", {})

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate buy signal on first day, sell on last day.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List with buy signal at start and sell signal at end
        """
        if df.empty:
            return []

        signals = []

        # Buy on first day
        first_date = df.index[0]
        first_price = df.iloc[0]["Close"]
        signals.append(
            Signal(
                date=first_date,
                signal=SignalType.BUY,
                price=first_price,
                reason="Buy and hold - initial purchase",
            )
        )

        # Sell on last day
        last_date = df.index[-1]
        last_price = df.iloc[-1]["Close"]
        signals.append(
            Signal(
                date=last_date,
                signal=SignalType.SELL,
                price=last_price,
                reason="Buy and hold - final exit",
            )
        )

        return signals


class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average (SMA) Crossover Strategy.

    Generates buy signal when fast SMA crosses above slow SMA.
    Generates sell signal when fast SMA crosses below slow SMA.
    """

    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        """
        Initialize SMA crossover strategy.

        Args:
            fast_period: Fast SMA period (default: 20)
            slow_period: Slow SMA period (default: 50)
        """
        super().__init__(
            "SMACrossover", {"fast_period": fast_period, "slow_period": slow_period}
        )
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate signals based on SMA crossover.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of Signal objects
        """
        if df.empty or len(df) < self.slow_period:
            return []

        # Calculate SMAs
        df_copy = df.copy()
        df_copy[f"SMA_{self.fast_period}"] = df_copy["Close"].rolling(self.fast_period).mean()
        df_copy[f"SMA_{self.slow_period}"] = df_copy["Close"].rolling(self.slow_period).mean()

        # Drop NaN values
        df_copy = df_copy.dropna()

        if df_copy.empty:
            return []

        signals = []
        position = None  # Track current position

        for i in range(1, len(df_copy)):
            prev_fast = df_copy.iloc[i - 1][f"SMA_{self.fast_period}"]
            prev_slow = df_copy.iloc[i - 1][f"SMA_{self.slow_period}"]
            curr_fast = df_copy.iloc[i][f"SMA_{self.fast_period}"]
            curr_slow = df_copy.iloc[i][f"SMA_{self.slow_period}"]
            curr_date = df_copy.index[i]
            curr_price = df_copy.iloc[i]["Close"]

            # Golden cross - fast crosses above slow (BUY)
            if prev_fast <= prev_slow and curr_fast > curr_slow and position is None:
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.BUY,
                        price=curr_price,
                        reason=f"Golden cross: SMA{self.fast_period} crossed above SMA{self.slow_period}",
                    )
                )
                position = "long"

            # Death cross - fast crosses below slow (SELL)
            elif prev_fast >= prev_slow and curr_fast < curr_slow and position == "long":
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.SELL,
                        price=curr_price,
                        reason=f"Death cross: SMA{self.fast_period} crossed below SMA{self.slow_period}",
                    )
                )
                position = None

        # Close any open position at the end
        if position == "long":
            last_date = df_copy.index[-1]
            last_price = df_copy.iloc[-1]["Close"]
            signals.append(
                Signal(
                    date=last_date,
                    signal=SignalType.SELL,
                    price=last_price,
                    reason="End of backtest - close position",
                )
            )

        return signals
