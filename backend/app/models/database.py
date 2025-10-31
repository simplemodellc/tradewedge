"""Database models for strategies and backtests."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Strategy(Base):
    """Trading strategy model."""

    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Strategy configuration stored as JSON
    config = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    backtests = relationship("Backtest", back_populates="strategy", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Strategy(id={self.id}, name='{self.name}')>"


class Backtest(Base):
    """Backtest result model."""

    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, index=True)

    # Backtest parameters
    ticker = Column(String(20), nullable=False, default="VTSAX")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False, default=10000.0)

    # Performance metrics
    total_return = Column(Float, nullable=True)
    cagr = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    total_trades = Column(Integer, nullable=True)

    # Full results stored as JSON (trade log, equity curve, etc.)
    results = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Backtest(id={self.id}, strategy_id={self.strategy_id}, total_return={self.total_return})>"
