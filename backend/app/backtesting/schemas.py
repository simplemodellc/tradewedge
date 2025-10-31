"""Pydantic schemas for backtesting."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SignalType(str, Enum):
    """Signal types for backtesting."""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class PositionSide(str, Enum):
    """Position side."""

    LONG = "long"
    SHORT = "short"


class PositionStatus(str, Enum):
    """Position status."""

    OPEN = "open"
    CLOSED = "closed"


class BacktestConfig(BaseModel):
    """Configuration for backtesting."""

    model_config = ConfigDict(str_strip_whitespace=True)

    initial_capital: float = Field(default=10000.0, gt=0, description="Initial capital")
    commission: float = Field(default=0.0, ge=0, description="Commission per trade (flat fee)")
    commission_pct: float = Field(
        default=0.001, ge=0, le=1, description="Commission as percentage (0.001 = 0.1%)"
    )
    slippage: float = Field(default=0.0, ge=0, description="Slippage per trade (flat)")
    slippage_pct: float = Field(
        default=0.0, ge=0, le=1, description="Slippage as percentage"
    )
    position_size_pct: float = Field(
        default=1.0, gt=0, le=1, description="Position size as % of capital (1.0 = 100%)"
    )


class Position(BaseModel):
    """Represents a trading position."""

    model_config = ConfigDict(str_strip_whitespace=True)

    entry_date: datetime = Field(..., description="Entry date")
    entry_price: float = Field(..., gt=0, description="Entry price")
    exit_date: Optional[datetime] = Field(default=None, description="Exit date")
    exit_price: Optional[float] = Field(default=None, description="Exit price")
    quantity: float = Field(..., gt=0, description="Position quantity (shares)")
    side: PositionSide = Field(default=PositionSide.LONG, description="Position side")
    status: PositionStatus = Field(default=PositionStatus.OPEN, description="Position status")
    entry_value: float = Field(..., description="Total entry value")
    exit_value: Optional[float] = Field(default=None, description="Total exit value")
    pnl: Optional[float] = Field(default=None, description="Profit/Loss")
    pnl_pct: Optional[float] = Field(default=None, description="Profit/Loss percentage")
    commission_paid: float = Field(default=0.0, description="Total commission paid")


class Signal(BaseModel):
    """Trading signal."""

    model_config = ConfigDict(str_strip_whitespace=True)

    date: datetime = Field(..., description="Signal date")
    signal: SignalType = Field(..., description="Signal type")
    price: float = Field(..., gt=0, description="Price at signal")
    reason: Optional[str] = Field(default=None, description="Reason for signal")


class PerformanceMetrics(BaseModel):
    """Performance metrics for a backtest."""

    model_config = ConfigDict(str_strip_whitespace=True)

    total_return: float = Field(..., description="Total return")
    total_return_pct: float = Field(..., description="Total return percentage")
    annual_return_pct: float = Field(..., description="Annualized return percentage")
    sharpe_ratio: Optional[float] = Field(default=None, description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    max_drawdown_pct: float = Field(..., description="Maximum drawdown percentage")
    win_rate: float = Field(..., ge=0, le=1, description="Win rate (0-1)")
    total_trades: int = Field(..., ge=0, description="Total number of trades")
    winning_trades: int = Field(..., ge=0, description="Number of winning trades")
    losing_trades: int = Field(..., ge=0, description="Number of losing trades")
    avg_win: float = Field(..., description="Average winning trade")
    avg_loss: float = Field(..., description="Average losing trade")
    profit_factor: Optional[float] = Field(default=None, description="Profit factor")
    total_commission: float = Field(default=0.0, description="Total commission paid")


class BacktestRequest(BaseModel):
    """Request to run a backtest."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticker: str = Field(default="SPY", description="Ticker symbol")
    strategy_type: str = Field(..., description="Strategy type (e.g., 'sma_crossover', 'buy_hold')")
    strategy_params: Dict[str, Any] = Field(
        default_factory=dict, description="Strategy parameters"
    )
    start_date: Optional[datetime] = Field(default=None, description="Backtest start date")
    end_date: Optional[datetime] = Field(default=None, description="Backtest end date")
    config: BacktestConfig = Field(
        default_factory=BacktestConfig, description="Backtest configuration"
    )


class BacktestResult(BaseModel):
    """Result of a backtest."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticker: str = Field(..., description="Ticker symbol")
    strategy_type: str = Field(..., description="Strategy type")
    strategy_params: Dict[str, Any] = Field(..., description="Strategy parameters")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: float = Field(..., description="Initial capital")
    final_capital: float = Field(..., description="Final capital")
    metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    positions: List[Position] = Field(..., description="All positions taken")
    signals: List[Signal] = Field(..., description="All signals generated")
    equity_curve: List[Dict[str, Any]] = Field(..., description="Equity curve data")


class BacktestResponse(BaseModel):
    """Response with backtest results."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(default="success", description="Response status")
    result: BacktestResult = Field(..., description="Backtest result")
