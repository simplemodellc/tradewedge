"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# Strategy Schemas
class StrategyBase(BaseModel):
    """Base strategy schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Strategy name")
    description: Optional[str] = Field(None, description="Strategy description")
    config: Dict[str, Any] = Field(..., description="Strategy configuration")


class StrategyCreate(StrategyBase):
    """Schema for creating a strategy."""

    pass


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class Strategy(StrategyBase):
    """Strategy response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Backtest Schemas
class BacktestBase(BaseModel):
    """Base backtest schema."""

    ticker: str = Field(default="VTSAX", description="Ticker symbol")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: float = Field(default=10000.0, gt=0, description="Initial capital")


class BacktestCreate(BacktestBase):
    """Schema for creating a backtest."""

    strategy_id: int = Field(..., description="Strategy ID to backtest")


class BacktestRun(BaseModel):
    """Schema for running a backtest with inline strategy config."""

    strategy_name: str = Field(..., description="Strategy name")
    strategy_config: Dict[str, Any] = Field(..., description="Strategy configuration")
    ticker: str = Field(default="VTSAX", description="Ticker symbol")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: float = Field(default=10000.0, gt=0, description="Initial capital")


class BacktestResults(BaseModel):
    """Backtest performance results."""

    total_return: Optional[float] = Field(None, description="Total return percentage")
    cagr: Optional[float] = Field(None, description="Compound annual growth rate")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown percentage")
    win_rate: Optional[float] = Field(None, description="Win rate percentage")
    total_trades: Optional[int] = Field(None, description="Total number of trades")


class Backtest(BacktestBase):
    """Backtest response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    strategy_id: int
    total_return: Optional[float] = None
    cagr: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None
    results: Optional[Dict[str, Any]] = None
    created_at: datetime


class BacktestDetail(Backtest):
    """Detailed backtest response with strategy info."""

    strategy: Strategy


# List responses
class StrategyList(BaseModel):
    """List of strategies."""

    strategies: List[Strategy]
    total: int


class BacktestList(BaseModel):
    """List of backtests."""

    backtests: List[Backtest]
    total: int
