"""Multi-strategy comparison and analysis engine."""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
from datetime import datetime

from app.backtesting.engine import BacktestEngine
from app.backtesting.schemas import BacktestResult, PerformanceMetrics
from app.data.downloader import MarketDataDownloader


class ComparisonResult:
    """Results from comparing multiple strategies."""

    def __init__(
        self,
        results: List[BacktestResult],
        strategy_names: List[str],
        rankings: Dict[str, List[int]],
        correlations: Dict[str, float],
    ):
        """
        Initialize comparison result.

        Args:
            results: List of backtest results
            strategy_names: List of strategy names
            rankings: Rankings by various metrics
            correlations: Correlation metrics between strategies
        """
        self.results = results
        self.strategy_names = strategy_names
        self.rankings = rankings
        self.correlations = correlations

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "results": [
                {
                    "strategy_name": name,
                    "metrics": result.metrics.model_dump(),
                    "equity_curve": result.equity_curve,
                    "trades": result.trades,
                }
                for name, result in zip(self.strategy_names, self.results)
            ],
            "rankings": self.rankings,
            "correlations": self.correlations,
        }


class StrategyComparison:
    """Compare multiple trading strategies."""

    def __init__(self):
        """Initialize the comparison engine."""
        self.downloader = MarketDataDownloader()

    def compare_strategies(
        self,
        strategies: List[Dict[str, Any]],
        ticker: str = "VTSAX",
        start_date: datetime = None,
        end_date: datetime = None,
        initial_capital: float = 100000.0,
        commission: float = 1.0,
    ) -> ComparisonResult:
        """
        Compare multiple strategies on the same data.

        Args:
            strategies: List of strategy configs [{name, type, params}, ...]
            ticker: Ticker symbol to test
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_capital: Initial capital for all strategies
            commission: Commission per trade

        Returns:
            ComparisonResult with metrics, rankings, and correlations
        """
        # Download market data
        df = self.downloader.download(ticker, start_date, end_date)

        if df.empty:
            raise ValueError(f"No data available for {ticker}")

        # Run backtest for each strategy
        results = []
        strategy_names = []

        for strategy_config in strategies:
            engine = BacktestEngine(
                data=df,
                strategy=strategy_config["type"],
                strategy_params=strategy_config.get("params", {}),
                initial_capital=initial_capital,
                commission=commission,
            )

            result = engine.run()
            results.append(result)
            strategy_names.append(strategy_config.get("name", strategy_config["type"]))

        # Calculate rankings
        rankings = self._calculate_rankings(results, strategy_names)

        # Calculate correlations
        correlations = self._calculate_correlations(results, strategy_names)

        return ComparisonResult(
            results=results,
            strategy_names=strategy_names,
            rankings=rankings,
            correlations=correlations,
        )

    def _calculate_rankings(
        self, results: List[BacktestResult], strategy_names: List[str]
    ) -> Dict[str, List[int]]:
        """
        Calculate rankings for each metric.

        Args:
            results: List of backtest results
            strategy_names: List of strategy names

        Returns:
            Dictionary of rankings by metric
        """
        rankings = {}

        # Metrics to rank (higher is better)
        metrics_higher_better = [
            "total_return_pct",
            "annual_return",
            "sharpe_ratio",
            "win_rate",
            "profit_factor",
        ]

        # Metrics to rank (lower is better)
        metrics_lower_better = ["max_drawdown_pct"]

        # Create ranking for each metric
        for metric in metrics_higher_better:
            values = [getattr(r.metrics, metric) or 0 for r in results]
            # Rank indices from best to worst (higher values are better)
            ranked_indices = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
            rankings[metric] = [strategy_names[i] for i in ranked_indices]

        for metric in metrics_lower_better:
            values = [abs(getattr(r.metrics, metric) or 0) for r in results]
            # Rank indices from best to worst (lower values are better)
            ranked_indices = sorted(range(len(values)), key=lambda i: values[i])
            rankings[metric] = [strategy_names[i] for i in ranked_indices]

        return rankings

    def _calculate_correlations(
        self, results: List[BacktestResult], strategy_names: List[str]
    ) -> Dict[str, float]:
        """
        Calculate correlation between strategy equity curves.

        Args:
            results: List of backtest results
            strategy_names: List of strategy names

        Returns:
            Dictionary of pairwise correlations
        """
        if len(results) < 2:
            return {}

        # Build dataframe with all equity curves
        equity_df = pd.DataFrame()

        for name, result in zip(strategy_names, results):
            if result.equity_curve:
                dates = [point["date"] for point in result.equity_curve]
                values = [point["equity"] for point in result.equity_curve]
                equity_df[name] = pd.Series(values, index=pd.to_datetime(dates))

        # Calculate correlation matrix
        corr_matrix = equity_df.corr()

        # Extract pairwise correlations
        correlations = {}
        for i in range(len(strategy_names)):
            for j in range(i + 1, len(strategy_names)):
                name1 = strategy_names[i]
                name2 = strategy_names[j]
                corr_value = corr_matrix.loc[name1, name2]

                if pd.notna(corr_value):
                    correlations[f"{name1}_vs_{name2}"] = round(float(corr_value), 4)

        return correlations
