"""Backtesting engine for executing trading strategies."""

import logging
from datetime import datetime
from typing import List, Tuple

import numpy as np
import pandas as pd

from .schemas import (
    BacktestConfig,
    BacktestResult,
    PerformanceMetrics,
    Position,
    PositionSide,
    PositionStatus,
    Signal,
    SignalType,
)
from .strategy import BaseStrategy

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Engine for executing backtests on historical data.

    Handles position tracking, capital management, and performance calculation.
    """

    def __init__(self, config: BacktestConfig = None):
        """
        Initialize backtest engine.

        Args:
            config: Backtest configuration
        """
        self.config = config or BacktestConfig()
        self.capital = self.config.initial_capital
        self.positions: List[Position] = []
        self.equity_curve: List[dict] = []
        self.current_position: Position | None = None

    def run(
        self,
        strategy: BaseStrategy,
        df: pd.DataFrame,
        ticker: str,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> BacktestResult:
        """
        Run backtest on historical data.

        Args:
            strategy: Trading strategy to execute
            df: DataFrame with OHLCV data
            ticker: Ticker symbol
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            BacktestResult with performance metrics and positions
        """
        # Filter data by date range
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        if df.empty:
            raise ValueError("No data available for backtest period")

        # Reset state
        self.capital = self.config.initial_capital
        self.positions = []
        self.equity_curve = []
        self.current_position = None

        # Generate signals
        signals = strategy.generate_signals(df)
        logger.info(f"Generated {len(signals)} signals for {strategy.name}")

        # Execute signals
        for signal in signals:
            self._execute_signal(signal, df)

        # Calculate final metrics
        metrics = self._calculate_metrics(df)

        return BacktestResult(
            ticker=ticker,
            strategy_type=strategy.name,
            strategy_params=strategy.params,
            start_date=df.index[0],
            end_date=df.index[-1],
            initial_capital=self.config.initial_capital,
            final_capital=self.capital,
            metrics=metrics,
            positions=self.positions,
            signals=signals,
            equity_curve=self.equity_curve,
        )

    def _execute_signal(self, signal: Signal, df: pd.DataFrame) -> None:
        """
        Execute a trading signal.

        Args:
            signal: Signal to execute
            df: Historical data
        """
        if signal.signal == SignalType.BUY:
            self._open_position(signal)
        elif signal.signal == SignalType.SELL:
            self._close_position(signal)

        # Update equity curve
        self._update_equity_curve(signal.date, signal.price)

    def _open_position(self, signal: Signal) -> None:
        """
        Open a new position.

        Args:
            signal: Buy signal
        """
        if self.current_position is not None:
            logger.warning(f"Already in position, skipping buy signal at {signal.date}")
            return

        # Calculate position size
        available_capital = self.capital * self.config.position_size_pct

        # Apply slippage to entry price
        entry_price = signal.price * (1 + self.config.slippage_pct) + self.config.slippage

        # Calculate quantity accounting for commission
        # quantity * entry_price * (1 + commission_pct) + commission <= available_capital
        # Solve for quantity
        cost_per_share = entry_price * (1 + self.config.commission_pct)
        quantity = int((available_capital - self.config.commission) / cost_per_share)

        if quantity <= 0:
            logger.warning(f"Insufficient capital to buy at {signal.date}")
            return

        # Calculate costs
        entry_value = quantity * entry_price
        commission = self.config.commission + (entry_value * self.config.commission_pct)

        # Check if we have enough capital
        total_cost = entry_value + commission
        if total_cost > self.capital:
            logger.warning(f"Insufficient capital for trade at {signal.date}")
            return

        # Deduct from capital
        self.capital -= total_cost

        # Create position
        self.current_position = Position(
            entry_date=signal.date,
            entry_price=entry_price,
            quantity=quantity,
            side=PositionSide.LONG,
            status=PositionStatus.OPEN,
            entry_value=entry_value,
            commission_paid=commission,
        )

        logger.info(
            f"Opened position: {quantity} shares at ${entry_price:.2f}, "
            f"capital: ${self.capital:.2f}"
        )

    def _close_position(self, signal: Signal) -> None:
        """
        Close current position.

        Args:
            signal: Sell signal
        """
        if self.current_position is None:
            logger.warning(f"No open position to close at {signal.date}")
            return

        # Apply slippage to exit price
        exit_price = signal.price * (1 - self.config.slippage_pct) - self.config.slippage

        # Calculate exit value
        exit_value = self.current_position.quantity * exit_price
        exit_commission = self.config.commission + (exit_value * self.config.commission_pct)

        # Add to capital
        self.capital += exit_value - exit_commission

        # Calculate P&L
        total_commission = self.current_position.commission_paid + exit_commission
        pnl = exit_value - self.current_position.entry_value - total_commission
        pnl_pct = (pnl / self.current_position.entry_value) * 100

        # Update position
        self.current_position.exit_date = signal.date
        self.current_position.exit_price = exit_price
        self.current_position.exit_value = exit_value
        self.current_position.pnl = pnl
        self.current_position.pnl_pct = pnl_pct
        self.current_position.status = PositionStatus.CLOSED
        self.current_position.commission_paid = total_commission

        logger.info(
            f"Closed position: {self.current_position.quantity} shares at ${exit_price:.2f}, "
            f"P&L: ${pnl:.2f} ({pnl_pct:.2f}%), capital: ${self.capital:.2f}"
        )

        # Save position
        self.positions.append(self.current_position)
        self.current_position = None

    def _update_equity_curve(self, date: datetime, price: float) -> None:
        """
        Update equity curve with current portfolio value.

        Args:
            date: Current date
            price: Current price
        """
        # Calculate current portfolio value
        portfolio_value = self.capital

        if self.current_position is not None:
            # Add unrealized position value
            current_value = self.current_position.quantity * price
            portfolio_value += current_value

        self.equity_curve.append(
            {
                "date": date.strftime("%Y-%m-%dT%H:%M:%S"),
                "equity": portfolio_value,
                "cash": self.capital,
                "return": (portfolio_value - self.config.initial_capital),
                "return_pct": ((portfolio_value - self.config.initial_capital) / self.config.initial_capital) * 100,
            }
        )

    def _calculate_metrics(self, df: pd.DataFrame) -> PerformanceMetrics:
        """
        Calculate performance metrics.

        Args:
            df: Historical data

        Returns:
            PerformanceMetrics object
        """
        # Total return
        total_return = self.capital - self.config.initial_capital
        total_return_pct = (total_return / self.config.initial_capital) * 100

        # Annualized return
        days = (df.index[-1] - df.index[0]).days
        years = days / 365.25
        annual_return_pct = (
            ((self.capital / self.config.initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        )

        # Calculate metrics from closed positions
        closed_positions = [p for p in self.positions if p.status == PositionStatus.CLOSED]

        total_trades = len(closed_positions)
        winning_trades = len([p for p in closed_positions if p.pnl and p.pnl > 0])
        losing_trades = len([p for p in closed_positions if p.pnl and p.pnl < 0])

        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # Average win/loss
        wins = [p.pnl for p in closed_positions if p.pnl and p.pnl > 0]
        losses = [p.pnl for p in closed_positions if p.pnl and p.pnl < 0]

        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0

        # Profit factor
        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else None

        # Max drawdown
        equity_values = [e["equity"] for e in self.equity_curve]
        max_drawdown, max_drawdown_pct = self._calculate_max_drawdown(equity_values)

        # Sharpe ratio
        returns = [e["return_pct"] for e in self.equity_curve]
        sharpe_ratio = self._calculate_sharpe_ratio(returns)

        # Total commission
        total_commission = sum(p.commission_paid for p in self.positions)

        return PerformanceMetrics(
            total_return=total_return,
            total_return_pct=total_return_pct,
            annual_return_pct=annual_return_pct,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            win_rate=win_rate,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            total_commission=total_commission,
        )

    def _calculate_max_drawdown(self, equity_values: List[float]) -> Tuple[float, float]:
        """
        Calculate maximum drawdown.

        Args:
            equity_values: List of equity values over time

        Returns:
            Tuple of (max_drawdown, max_drawdown_pct)
        """
        if not equity_values:
            return 0.0, 0.0

        peak = equity_values[0]
        max_dd = 0.0
        max_dd_pct = 0.0

        for value in equity_values:
            if value > peak:
                peak = value

            dd = peak - value
            dd_pct = (dd / peak) * 100 if peak > 0 else 0

            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct

        return max_dd, max_dd_pct

    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.0) -> float | None:
        """
        Calculate Sharpe ratio.

        Args:
            returns: List of returns
            risk_free_rate: Risk-free rate (annualized %)

        Returns:
            Sharpe ratio or None if insufficient data
        """
        if len(returns) < 2:
            return None

        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate

        if excess_returns.std() == 0:
            return None

        # Annualize the Sharpe ratio (assuming daily returns)
        sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)

        return float(sharpe)
