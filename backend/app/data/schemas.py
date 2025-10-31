"""Data schemas and validation models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OHLCVData(BaseModel):
    """OHLCV (Open, High, Low, Close, Volume) data point."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )

    date: datetime
    open: float = Field(gt=0, description="Opening price")
    high: float = Field(gt=0, description="Highest price")
    low: float = Field(gt=0, description="Lowest price")
    close: float = Field(gt=0, description="Closing price")
    volume: int = Field(ge=0, description="Trading volume")

    @field_validator("high")
    @classmethod
    def validate_high(cls, v: float, info) -> float:  # type: ignore
        """Validate that high is the highest price."""
        if "low" in info.data and v < info.data["low"]:
            raise ValueError("High price must be >= low price")
        return v

    @field_validator("close")
    @classmethod
    def validate_close(cls, v: float, info) -> float:  # type: ignore
        """Validate that close is within high-low range."""
        if "high" in info.data and "low" in info.data:
            if not (info.data["low"] <= v <= info.data["high"]):
                raise ValueError("Close price must be between low and high")
        return v


class MarketDataSummary(BaseModel):
    """Summary statistics for market data."""

    ticker: str
    start_date: datetime
    end_date: datetime
    total_records: int
    missing_dates: int
    data_quality_score: float = Field(ge=0, le=100)


class DataDownloadRequest(BaseModel):
    """Request to download historical data."""

    ticker: str = "VTSAX"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    force_refresh: bool = False
