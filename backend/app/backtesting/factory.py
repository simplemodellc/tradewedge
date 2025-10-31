"""Strategy factory for creating strategies by name."""

from typing import Any, Dict, Type

from .strategy import BaseStrategy, BuyAndHoldStrategy, SMACrossoverStrategy


class StrategyFactory:
    """Factory for creating strategy instances by name."""

    _strategies: Dict[str, Type[BaseStrategy]] = {
        "buy_hold": BuyAndHoldStrategy,
        "buy_and_hold": BuyAndHoldStrategy,
        "sma_crossover": SMACrossoverStrategy,
        "sma_cross": SMACrossoverStrategy,
    }

    @classmethod
    def create(cls, name: str, params: Dict[str, Any] = None) -> BaseStrategy:
        """
        Create a strategy instance by name.

        Args:
            name: Strategy name (case-insensitive)
            params: Optional parameters for the strategy

        Returns:
            Strategy instance

        Raises:
            ValueError: If strategy name is not recognized
        """
        name_lower = name.lower()
        if name_lower not in cls._strategies:
            available = ", ".join(sorted(set(cls._strategies.keys())))
            raise ValueError(
                f"Unknown strategy: {name}. Available strategies: {available}"
            )

        strategy_class = cls._strategies[name_lower]
        params = params or {}

        try:
            return strategy_class(**params)
        except TypeError as e:
            raise ValueError(
                f"Invalid parameters for {name}: {params}. Error: {str(e)}"
            ) from e

    @classmethod
    def list_strategies(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get a list of all available strategies with their metadata.

        Returns:
            Dictionary mapping strategy names to their metadata
        """
        strategies = {}
        seen_classes = set()

        for name, strategy_class in cls._strategies.items():
            # Skip aliases (only include primary names)
            if strategy_class in seen_classes:
                continue

            seen_classes.add(strategy_class)

            # Get default parameters by inspecting __init__
            import inspect

            sig = inspect.signature(strategy_class.__init__)
            params = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                params[param_name] = {
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                    "required": param.default == inspect.Parameter.empty,
                }

            strategies[name] = {
                "class": strategy_class.__name__,
                "params": params,
                "description": strategy_class.__doc__.strip() if strategy_class.__doc__ else "",
            }

        return strategies
