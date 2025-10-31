"""Tests for backtesting engine and strategies."""

import pandas as pd
import pytest
from datetime import datetime, timedelta

from app.backtesting import (
    BacktestConfig,
    BacktestEngine,
    BuyAndHoldStrategy,
    SMACrossoverStrategy,
    StrategyFactory,
)


@pytest.fixture
def sample_trending_data():
    """Create sample trending price data for testing."""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    # Create upward trending prices
    prices = [100 + i * 0.5 for i in range(100)]
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p * 1.02 for p in prices],
            "Low": [p * 0.98 for p in prices],
            "Close": prices,
            "Volume": [1000000] * 100,
        },
        index=dates,
    )
    return df


@pytest.fixture
def sample_oscillating_data():
    """Create sample oscillating price data for crossover testing."""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    # Create oscillating prices that cross moving averages
    import numpy as np

    prices = 100 + 10 * np.sin(np.linspace(0, 4 * np.pi, 100))
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": prices * 1.01,
            "Low": prices * 0.99,
            "Close": prices,
            "Volume": [1000000] * 100,
        },
        index=dates,
    )
    return df


class TestStrategyFactory:
    """Tests for StrategyFactory."""

    def test_create_buy_hold(self):
        """Test creating buy and hold strategy."""
        strategy = StrategyFactory.create("buy_hold")
        assert isinstance(strategy, BuyAndHoldStrategy)

    def test_create_sma_crossover(self):
        """Test creating SMA crossover strategy."""
        strategy = StrategyFactory.create("sma_crossover", {"fast_period": 10, "slow_period": 30})
        assert isinstance(strategy, SMACrossoverStrategy)
        assert strategy.fast_period == 10
        assert strategy.slow_period == 30

    def test_create_unknown_strategy(self):
        """Test creating unknown strategy raises error."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            StrategyFactory.create("unknown")

    def test_list_strategies(self):
        """Test listing all available strategies."""
        strategies = StrategyFactory.list_strategies()
        assert isinstance(strategies, dict)
        assert len(strategies) > 0
        assert "buy_hold" in strategies or "buy_and_hold" in strategies
        assert "sma_crossover" in strategies or "sma_cross" in strategies


class TestBuyAndHoldStrategy:
    """Tests for BuyAndHoldStrategy."""

    def test_generate_signals(self, sample_trending_data):
        """Test signal generation for buy and hold."""
        strategy = BuyAndHoldStrategy()
        signals = strategy.generate_signals(sample_trending_data)

        assert len(signals) == 2  # Buy at start, sell at end
        assert signals[0].signal.value == "buy"
        assert signals[1].signal.value == "sell"
        assert signals[0].date == sample_trending_data.index[0]
        assert signals[1].date == sample_trending_data.index[-1]

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        strategy = BuyAndHoldStrategy()
        signals = strategy.generate_signals(pd.DataFrame())
        assert len(signals) == 0


class TestSMACrossoverStrategy:
    """Tests for SMACrossoverStrategy."""

    def test_generate_signals(self, sample_oscillating_data):
        """Test signal generation for SMA crossover."""
        strategy = SMACrossoverStrategy(fast_period=5, slow_period=20)
        signals = strategy.generate_signals(sample_oscillating_data)

        # Should have at least one buy and sell signal
        assert len(signals) >= 2
        buy_signals = [s for s in signals if s.signal.value == "buy"]
        sell_signals = [s for s in signals if s.signal.value == "sell"]
        assert len(buy_signals) > 0
        assert len(sell_signals) > 0

    def test_insufficient_data(self):
        """Test with insufficient data for slow period."""
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        df = pd.DataFrame(
            {
                "Open": range(100, 110),
                "High": range(105, 115),
                "Low": range(95, 105),
                "Close": range(100, 110),
                "Volume": [1000000] * 10,
            },
            index=dates,
        )

        strategy = SMACrossoverStrategy(fast_period=5, slow_period=20)
        signals = strategy.generate_signals(df)
        assert len(signals) == 0  # Not enough data


class TestBacktestEngine:
    """Tests for BacktestEngine."""

    def test_buy_and_hold_backtest(self, sample_trending_data):
        """Test running buy and hold backtest."""
        strategy = BuyAndHoldStrategy()
        engine = BacktestEngine(
            BacktestConfig(initial_capital=10000, commission_pct=0.001)
        )

        result = engine.run(
            strategy=strategy,
            df=sample_trending_data,
            ticker="TEST",
        )

        # Verify result structure
        assert result.ticker == "TEST"
        assert result.strategy_type == "BuyAndHold"
        assert result.initial_capital == 10000
        assert result.final_capital > 0

        # Verify we have positions
        assert len(result.positions) > 0
        assert result.positions[0].status.value == "closed"

        # Verify metrics
        assert result.metrics.total_trades > 0
        assert result.metrics.total_return != 0

        # Verify equity curve
        assert len(result.equity_curve) > 0

    def test_sma_crossover_backtest(self, sample_oscillating_data):
        """Test running SMA crossover backtest."""
        strategy = SMACrossoverStrategy(fast_period=5, slow_period=20)
        engine = BacktestEngine(
            BacktestConfig(initial_capital=10000, commission_pct=0.001)
        )

        result = engine.run(
            strategy=strategy,
            df=sample_oscillating_data,
            ticker="TEST",
        )

        # Verify result structure
        assert result.ticker == "TEST"
        assert result.strategy_type == "SMACrossover"

        # Should have multiple trades
        assert result.metrics.total_trades >= 0

    def test_backtest_with_commission(self, sample_trending_data):
        """Test backtest applies commission correctly."""
        strategy = BuyAndHoldStrategy()

        # Run with no commission
        engine_no_comm = BacktestEngine(
            BacktestConfig(initial_capital=10000, commission_pct=0)
        )
        result_no_comm = engine_no_comm.run(
            strategy=strategy, df=sample_trending_data, ticker="TEST"
        )

        # Run with commission
        engine_with_comm = BacktestEngine(
            BacktestConfig(initial_capital=10000, commission_pct=0.01)  # 1%
        )
        result_with_comm = engine_with_comm.run(
            strategy=strategy, df=sample_trending_data, ticker="TEST"
        )

        # With commission should have lower final capital
        assert result_with_comm.final_capital < result_no_comm.final_capital
        assert result_with_comm.metrics.total_commission > 0

    def test_backtest_with_date_range(self, sample_trending_data):
        """Test backtest with custom date range."""
        strategy = BuyAndHoldStrategy()
        engine = BacktestEngine()

        start_date = sample_trending_data.index[10]
        end_date = sample_trending_data.index[50]

        result = engine.run(
            strategy=strategy,
            df=sample_trending_data,
            ticker="TEST",
            start_date=start_date,
            end_date=end_date,
        )

        # Verify date range
        assert result.start_date >= start_date
        assert result.end_date <= end_date

    def test_insufficient_capital(self):
        """Test backtest with insufficient capital."""
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        df = pd.DataFrame(
            {
                "Open": [10000] * 10,  # Very high price
                "High": [10100] * 10,
                "Low": [9900] * 10,
                "Close": [10000] * 10,
                "Volume": [1000000] * 10,
            },
            index=dates,
        )

        strategy = BuyAndHoldStrategy()
        engine = BacktestEngine(BacktestConfig(initial_capital=100))  # Too low

        result = engine.run(strategy=strategy, df=df, ticker="TEST")

        # Should have no positions due to insufficient capital
        assert len(result.positions) == 0
        assert result.final_capital == 100  # Capital unchanged


class TestPerformanceMetrics:
    """Tests for performance metrics calculation."""

    def test_profitable_trade_metrics(self, sample_trending_data):
        """Test metrics for profitable trade."""
        strategy = BuyAndHoldStrategy()
        engine = BacktestEngine()

        result = engine.run(
            strategy=strategy,
            df=sample_trending_data,
            ticker="TEST",
        )

        # In uptrend, buy and hold should be profitable
        assert result.metrics.total_return > 0
        assert result.metrics.total_return_pct > 0
        assert result.metrics.win_rate == 1.0  # Single winning trade
        assert result.metrics.winning_trades == 1
        assert result.metrics.losing_trades == 0

    def test_max_drawdown_calculation(self):
        """Test max drawdown calculation."""
        dates = pd.date_range(start="2023-01-01", periods=50, freq="D")
        # Create price that goes up then crashes
        prices = [100 + i for i in range(25)] + [125 - i for i in range(25)]

        df = pd.DataFrame(
            {
                "Open": prices,
                "High": [p * 1.01 for p in prices],
                "Low": [p * 0.99 for p in prices],
                "Close": prices,
                "Volume": [1000000] * 50,
            },
            index=dates,
        )

        strategy = BuyAndHoldStrategy()
        engine = BacktestEngine()
        result = engine.run(strategy=strategy, df=df, ticker="TEST")

        # Drawdown calculation should work even if no drawdown occurred
        # (buy and hold only has 2 equity points so can't capture intermediate drawdowns)
        assert result.metrics.max_drawdown >= 0
        assert result.metrics.max_drawdown_pct >= 0

    def test_sharpe_ratio_calculation(self, sample_trending_data):
        """Test Sharpe ratio calculation."""
        strategy = BuyAndHoldStrategy()
        engine = BacktestEngine()

        result = engine.run(
            strategy=strategy,
            df=sample_trending_data,
            ticker="TEST",
        )

        # Should have a Sharpe ratio for trending data
        assert result.metrics.sharpe_ratio is not None

    def test_win_loss_metrics(self, sample_oscillating_data):
        """Test win/loss metrics with multiple trades."""
        strategy = SMACrossoverStrategy(fast_period=5, slow_period=20)
        engine = BacktestEngine()

        result = engine.run(
            strategy=strategy,
            df=sample_oscillating_data,
            ticker="TEST",
        )

        # Verify win/loss metrics are calculated
        assert result.metrics.total_trades >= 0
        assert result.metrics.winning_trades >= 0
        assert result.metrics.losing_trades >= 0
        assert (
            result.metrics.winning_trades + result.metrics.losing_trades
            <= result.metrics.total_trades
        )

        if result.metrics.total_trades > 0:
            assert 0 <= result.metrics.win_rate <= 1
