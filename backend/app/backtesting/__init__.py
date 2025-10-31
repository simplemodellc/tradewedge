"""Backtesting engine and strategy framework."""

from .engine import BacktestEngine
from .factory import StrategyFactory
from .schemas import (
    BacktestConfig,
    BacktestRequest,
    BacktestResponse,
    BacktestResult,
    PerformanceMetrics,
    Position,
    PositionSide,
    PositionStatus,
    Signal,
    SignalType,
)
from .strategy import BaseStrategy, BuyAndHoldStrategy, SMACrossoverStrategy

__all__ = [
    # Engine
    "BacktestEngine",
    "StrategyFactory",
    # Schemas
    "BacktestConfig",
    "BacktestRequest",
    "BacktestResponse",
    "BacktestResult",
    "PerformanceMetrics",
    "Position",
    "PositionSide",
    "PositionStatus",
    "Signal",
    "SignalType",
    # Strategies
    "BaseStrategy",
    "BuyAndHoldStrategy",
    "SMACrossoverStrategy",
]
