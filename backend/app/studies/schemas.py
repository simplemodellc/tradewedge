"""Pydantic schemas for indicator requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class IndicatorRequest(BaseModel):
    """Request to calculate an indicator."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticker: str = Field(default="SPY", description="Ticker symbol")
    indicator: str = Field(..., description="Indicator name (e.g., 'sma', 'rsi', 'macd')")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Indicator parameters (e.g., {'length': 20})"
    )
    start_date: Optional[datetime] = Field(
        default=None, description="Start date for data range"
    )
    end_date: Optional[datetime] = Field(default=None, description="End date for data range")


class IndicatorResponse(BaseModel):
    """Response with calculated indicator data."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(default="success", description="Response status")
    ticker: str = Field(..., description="Ticker symbol")
    indicator: str = Field(..., description="Indicator name")
    params: Dict[str, Any] = Field(..., description="Parameters used")
    data: List[Dict[str, Any]] = Field(..., description="OHLCV data with indicator values")
    count: int = Field(..., description="Number of data points")
    columns: List[str] = Field(..., description="Column names in the data")


class IndicatorListResponse(BaseModel):
    """Response with list of available indicators."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(default="success", description="Response status")
    indicators: List[Dict[str, Any]] = Field(..., description="List of available indicators")
    count: int = Field(..., description="Number of available indicators")
