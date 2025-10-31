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


class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Strategy.

    Generates buy signal when RSI crosses below oversold threshold.
    Generates sell signal when RSI crosses above overbought threshold.
    """

    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        """
        Initialize RSI strategy.

        Args:
            period: RSI calculation period (default: 14)
            oversold: Oversold threshold (default: 30)
            overbought: Overbought threshold (default: 70)
        """
        super().__init__(
            "RSI",
            {"period": period, "oversold": oversold, "overbought": overbought}
        )
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate signals based on RSI oversold/overbought levels.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of Signal objects
        """
        if df.empty or len(df) < self.period + 1:
            return []

        # Calculate RSI
        df_copy = df.copy()
        delta = df_copy["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        df_copy["RSI"] = 100 - (100 / (1 + rs))

        # Drop NaN values
        df_copy = df_copy.dropna()

        if df_copy.empty:
            return []

        signals = []
        position = None  # Track current position

        for i in range(1, len(df_copy)):
            prev_rsi = df_copy.iloc[i - 1]["RSI"]
            curr_rsi = df_copy.iloc[i]["RSI"]
            curr_date = df_copy.index[i]
            curr_price = df_copy.iloc[i]["Close"]

            # Buy when RSI crosses below oversold (entering oversold)
            if prev_rsi >= self.oversold and curr_rsi < self.oversold and position is None:
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.BUY,
                        price=curr_price,
                        reason=f"RSI oversold: {curr_rsi:.2f} < {self.oversold}",
                    )
                )
                position = "long"

            # Sell when RSI crosses above overbought (entering overbought)
            elif prev_rsi <= self.overbought and curr_rsi > self.overbought and position == "long":
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.SELL,
                        price=curr_price,
                        reason=f"RSI overbought: {curr_rsi:.2f} > {self.overbought}",
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


class MACDStrategy(BaseStrategy):
    """
    MACD (Moving Average Convergence Divergence) Strategy.

    Generates buy signal when MACD line crosses above signal line.
    Generates sell signal when MACD line crosses below signal line.
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        Initialize MACD strategy.

        Args:
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line period (default: 9)
        """
        super().__init__(
            "MACD",
            {"fast_period": fast_period, "slow_period": slow_period, "signal_period": signal_period}
        )
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate signals based on MACD crossover.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of Signal objects
        """
        if df.empty or len(df) < self.slow_period + self.signal_period:
            return []

        # Calculate MACD
        df_copy = df.copy()
        ema_fast = df_copy["Close"].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df_copy["Close"].ewm(span=self.slow_period, adjust=False).mean()
        df_copy["MACD"] = ema_fast - ema_slow
        df_copy["Signal"] = df_copy["MACD"].ewm(span=self.signal_period, adjust=False).mean()

        # Drop NaN values
        df_copy = df_copy.dropna()

        if df_copy.empty:
            return []

        signals = []
        position = None  # Track current position

        for i in range(1, len(df_copy)):
            prev_macd = df_copy.iloc[i - 1]["MACD"]
            prev_signal = df_copy.iloc[i - 1]["Signal"]
            curr_macd = df_copy.iloc[i]["MACD"]
            curr_signal = df_copy.iloc[i]["Signal"]
            curr_date = df_copy.index[i]
            curr_price = df_copy.iloc[i]["Close"]

            # Buy when MACD crosses above signal line
            if prev_macd <= prev_signal and curr_macd > curr_signal and position is None:
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.BUY,
                        price=curr_price,
                        reason=f"MACD bullish crossover: {curr_macd:.4f} > {curr_signal:.4f}",
                    )
                )
                position = "long"

            # Sell when MACD crosses below signal line
            elif prev_macd >= prev_signal and curr_macd < curr_signal and position == "long":
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.SELL,
                        price=curr_price,
                        reason=f"MACD bearish crossover: {curr_macd:.4f} < {curr_signal:.4f}",
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


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands Mean Reversion Strategy.

    Generates buy signal when price touches lower band.
    Generates sell signal when price touches upper band.
    """

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        """
        Initialize Bollinger Bands strategy.

        Args:
            period: Moving average period (default: 20)
            std_dev: Number of standard deviations (default: 2.0)
        """
        super().__init__(
            "BollingerBands",
            {"period": period, "std_dev": std_dev}
        )
        self.period = period
        self.std_dev = std_dev

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate signals based on Bollinger Bands bounce.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of Signal objects
        """
        if df.empty or len(df) < self.period:
            return []

        # Calculate Bollinger Bands
        df_copy = df.copy()
        df_copy["SMA"] = df_copy["Close"].rolling(self.period).mean()
        df_copy["STD"] = df_copy["Close"].rolling(self.period).std()
        df_copy["Upper"] = df_copy["SMA"] + (df_copy["STD"] * self.std_dev)
        df_copy["Lower"] = df_copy["SMA"] - (df_copy["STD"] * self.std_dev)

        # Drop NaN values
        df_copy = df_copy.dropna()

        if df_copy.empty:
            return []

        signals = []
        position = None  # Track current position

        for i in range(len(df_copy)):
            curr_close = df_copy.iloc[i]["Close"]
            curr_lower = df_copy.iloc[i]["Lower"]
            curr_upper = df_copy.iloc[i]["Upper"]
            curr_date = df_copy.index[i]

            # Buy when price touches or crosses below lower band
            if curr_close <= curr_lower and position is None:
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.BUY,
                        price=curr_close,
                        reason=f"Price at lower band: {curr_close:.2f} <= {curr_lower:.2f}",
                    )
                )
                position = "long"

            # Sell when price touches or crosses above upper band
            elif curr_close >= curr_upper and position == "long":
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.SELL,
                        price=curr_close,
                        reason=f"Price at upper band: {curr_close:.2f} >= {curr_upper:.2f}",
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


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy using Z-Score.

    Generates buy signal when price is more than threshold standard deviations below mean.
    Generates sell signal when price returns to mean or above.
    """

    def __init__(self, period: int = 20, entry_threshold: float = -2.0, exit_threshold: float = 0.0):
        """
        Initialize mean reversion strategy.

        Args:
            period: Lookback period for mean and std dev (default: 20)
            entry_threshold: Z-score threshold for entry (default: -2.0)
            exit_threshold: Z-score threshold for exit (default: 0.0)
        """
        super().__init__(
            "MeanReversion",
            {"period": period, "entry_threshold": entry_threshold, "exit_threshold": exit_threshold}
        )
        self.period = period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generate signals based on mean reversion (Z-score).

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of Signal objects
        """
        if df.empty or len(df) < self.period:
            return []

        # Calculate Z-score
        df_copy = df.copy()
        df_copy["SMA"] = df_copy["Close"].rolling(self.period).mean()
        df_copy["STD"] = df_copy["Close"].rolling(self.period).std()
        df_copy["ZScore"] = (df_copy["Close"] - df_copy["SMA"]) / df_copy["STD"]

        # Drop NaN values
        df_copy = df_copy.dropna()

        if df_copy.empty:
            return []

        signals = []
        position = None  # Track current position

        for i in range(len(df_copy)):
            curr_zscore = df_copy.iloc[i]["ZScore"]
            curr_date = df_copy.index[i]
            curr_price = df_copy.iloc[i]["Close"]

            # Buy when Z-score is below entry threshold (oversold)
            if curr_zscore <= self.entry_threshold and position is None:
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.BUY,
                        price=curr_price,
                        reason=f"Mean reversion entry: Z-score {curr_zscore:.2f}",
                    )
                )
                position = "long"

            # Sell when Z-score returns to exit threshold (mean)
            elif curr_zscore >= self.exit_threshold and position == "long":
                signals.append(
                    Signal(
                        date=curr_date,
                        signal=SignalType.SELL,
                        price=curr_price,
                        reason=f"Mean reversion exit: Z-score {curr_zscore:.2f}",
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
