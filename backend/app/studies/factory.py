"""Indicator factory for creating indicators by name."""

from typing import Any, Dict, Type

from .base import BaseIndicator
from .momentum import CCI, MACD, ROC, RSI, Stochastic, WilliamsR
from .trend import DEMA, EMA, HMA, SMA, TEMA, WMA
from .volatility import ATR, BollingerBands, KeltnerChannels, StandardDeviation
from .volume import AD, MFI, OBV, VWAP, VolumeSMA


class IndicatorFactory:
    """Factory for creating indicator instances by name."""

    _indicators: Dict[str, Type[BaseIndicator]] = {
        # Trend indicators
        "sma": SMA,
        "ema": EMA,
        "wma": WMA,
        "dema": DEMA,
        "tema": TEMA,
        "hma": HMA,
        # Momentum indicators
        "rsi": RSI,
        "macd": MACD,
        "stochastic": Stochastic,
        "stoch": Stochastic,  # Alias
        "cci": CCI,
        "roc": ROC,
        "willr": WilliamsR,
        "williamsr": WilliamsR,  # Alias
        # Volatility indicators
        "bbands": BollingerBands,
        "bb": BollingerBands,  # Alias
        "bollingerbands": BollingerBands,  # Alias
        "atr": ATR,
        "kc": KeltnerChannels,
        "keltner": KeltnerChannels,  # Alias
        "stdev": StandardDeviation,
        # Volume indicators
        "obv": OBV,
        "volumesma": VolumeSMA,
        "vwap": VWAP,
        "mfi": MFI,
        "ad": AD,
    }

    @classmethod
    def create(cls, name: str, params: Dict[str, Any] = None) -> BaseIndicator:
        """
        Create an indicator instance by name.

        Args:
            name: Indicator name (case-insensitive)
            params: Optional parameters for the indicator

        Returns:
            Indicator instance

        Raises:
            ValueError: If indicator name is not recognized
        """
        name_lower = name.lower()
        if name_lower not in cls._indicators:
            available = ", ".join(sorted(set(cls._indicators.keys())))
            raise ValueError(
                f"Unknown indicator: {name}. Available indicators: {available}"
            )

        indicator_class = cls._indicators[name_lower]
        params = params or {}

        try:
            return indicator_class(**params)
        except TypeError as e:
            raise ValueError(
                f"Invalid parameters for {name}: {params}. Error: {str(e)}"
            ) from e

    @classmethod
    def list_indicators(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get a list of all available indicators with their metadata.

        Returns:
            Dictionary mapping indicator names to their metadata
        """
        indicators = {}
        seen_classes = set()

        for name, indicator_class in cls._indicators.items():
            # Skip aliases (only include primary names)
            if indicator_class in seen_classes:
                continue

            seen_classes.add(indicator_class)

            # Get default parameters by inspecting __init__
            import inspect

            sig = inspect.signature(indicator_class.__init__)
            params = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                params[param_name] = {
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                    "required": param.default == inspect.Parameter.empty,
                }

            indicators[name] = {
                "class": indicator_class.__name__,
                "category": cls._get_category(indicator_class),
                "params": params,
                "description": indicator_class.__doc__.strip() if indicator_class.__doc__ else "",
            }

        return indicators

    @classmethod
    def _get_category(cls, indicator_class: Type[BaseIndicator]) -> str:
        """Get the category of an indicator class."""
        module = indicator_class.__module__
        if "trend" in module:
            return "trend"
        elif "momentum" in module:
            return "momentum"
        elif "volatility" in module:
            return "volatility"
        elif "volume" in module:
            return "volume"
        else:
            return "other"
