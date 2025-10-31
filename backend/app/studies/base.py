"""Base classes and interfaces for technical indicators."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd


class BaseIndicator(ABC):
    """
    Base class for all technical indicators.

    Provides a common interface for calculating indicators on OHLCV data.
    """

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize the indicator.

        Args:
            name: Name of the indicator
            params: Optional parameters for the indicator
        """
        self.name = name
        self.params = params or {}

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the indicator on the given DataFrame.

        Args:
            df: DataFrame with OHLCV data (columns: Open, High, Low, Close, Volume)

        Returns:
            DataFrame with original data and new indicator column(s)

        Raises:
            ValueError: If required columns are missing
        """
        pass

    def validate_dataframe(self, df: pd.DataFrame, required_columns: list[str]) -> None:
        """
        Validate that DataFrame has required columns.

        Args:
            df: DataFrame to validate
            required_columns: List of required column names

        Raises:
            ValueError: If DataFrame is empty or missing required columns
        """
        if df is None or df.empty:
            raise ValueError("DataFrame is empty")

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

    def get_description(self) -> str:
        """
        Get a description of this indicator.

        Returns:
            String description of the indicator
        """
        return f"{self.name} with params: {self.params}"
