"""Tests for backtesting API endpoints."""

from datetime import datetime
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_trending_data():
    """Create mock trending market data."""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    prices = [100 + i * 0.5 for i in range(100)]
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p * 1.02 for p in prices],
            "Low": [p * 0.98 for p in prices],
            "Close": prices,
            "Volume": [1000000] * 100,
        },
        index=dates,
    )
    return df


@pytest.fixture
def mock_downloader(mock_trending_data):
    """Create mock downloader with trending data."""
    with patch("app.routers.backtesting.MarketDataDownloader") as mock:
        instance = Mock()
        instance.download.return_value = mock_trending_data
        mock.return_value = instance
        yield mock


class TestStrategiesEndpoint:
    """Tests for strategies list endpoint."""

    def test_list_strategies(self, client):
        """Test listing all available strategies."""
        response = client.get("/api/v1/backtesting/strategies")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "strategies" in data
        assert "count" in data
        assert data["count"] > 0

        # Check that we have buy_hold and sma_crossover
        strategy_names = [s["name"] for s in data["strategies"]]
        assert any("buy" in name and "hold" in name for name in strategy_names)
        assert any("sma" in name for name in strategy_names)


class TestRunBacktestEndpoint:
    """Tests for run backtest endpoint."""

    def test_run_buy_hold_backtest(self, client, mock_downloader):
        """Test running buy and hold backtest."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "buy_hold",
            "strategy_params": {},
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data

        result = data["result"]
        assert result["ticker"] == "SPY"
        assert result["strategy_type"] == "BuyAndHold"
        assert result["initial_capital"] > 0
        assert result["final_capital"] > 0
        assert "metrics" in result
        assert "positions" in result
        assert "signals" in result
        assert "equity_curve" in result

    def test_run_sma_crossover_backtest(self, client, mock_downloader):
        """Test running SMA crossover backtest."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "sma_crossover",
            "strategy_params": {"fast_period": 10, "slow_period": 30},
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        assert result["strategy_type"] == "SMACrossover"
        assert result["strategy_params"]["fast_period"] == 10
        assert result["strategy_params"]["slow_period"] == 30

    def test_run_backtest_with_custom_config(self, client, mock_downloader):
        """Test running backtest with custom configuration."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "buy_hold",
            "config": {
                "initial_capital": 50000,
                "commission_pct": 0.002,
                "position_size_pct": 0.5,
            },
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        assert result["initial_capital"] == 50000

    def test_run_backtest_with_date_range(self, client, mock_downloader):
        """Test running backtest with date range."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "buy_hold",
            "start_date": "2023-01-15T00:00:00",
            "end_date": "2023-03-01T00:00:00",
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        # Result should be within specified range
        assert result["start_date"].startswith("2023-01")
        assert result["end_date"].startswith("2023-02") or result["end_date"].startswith("2023-03")

    def test_run_backtest_invalid_strategy(self, client, mock_downloader):
        """Test running backtest with invalid strategy."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "invalid_strategy",
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 400
        assert "detail" in response.json()

    @patch("app.routers.backtesting.MarketDataDownloader")
    def test_run_backtest_no_data(self, mock_downloader, client):
        """Test running backtest when no data available."""
        instance = Mock()
        instance.download.return_value = None
        mock_downloader.return_value = instance

        request_data = {
            "ticker": "INVALID",
            "strategy_type": "buy_hold",
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 404
        assert "No data available" in response.json()["detail"]


class TestBacktestResultStructure:
    """Tests for backtest result structure."""

    def test_result_has_metrics(self, client, mock_downloader):
        """Test that result includes performance metrics."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "buy_hold",
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        result = response.json()["result"]
        metrics = result["metrics"]

        # Check all expected metrics are present
        assert "total_return" in metrics
        assert "total_return_pct" in metrics
        assert "annual_return_pct" in metrics
        assert "sharpe_ratio" in metrics
        assert "max_drawdown" in metrics
        assert "max_drawdown_pct" in metrics
        assert "win_rate" in metrics
        assert "total_trades" in metrics
        assert "winning_trades" in metrics
        assert "losing_trades" in metrics
        assert "avg_win" in metrics
        assert "avg_loss" in metrics
        assert "total_commission" in metrics

    def test_result_has_positions(self, client, mock_downloader):
        """Test that result includes position details."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "buy_hold",
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        result = response.json()["result"]
        positions = result["positions"]

        assert isinstance(positions, list)
        if len(positions) > 0:
            pos = positions[0]
            assert "entry_date" in pos
            assert "entry_price" in pos
            assert "exit_date" in pos
            assert "exit_price" in pos
            assert "quantity" in pos
            assert "pnl" in pos
            assert "pnl_pct" in pos

    def test_result_has_signals(self, client, mock_downloader):
        """Test that result includes trading signals."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "buy_hold",
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        result = response.json()["result"]
        signals = result["signals"]

        assert isinstance(signals, list)
        assert len(signals) > 0

        # Check signal structure
        signal = signals[0]
        assert "date" in signal
        assert "signal" in signal
        assert "price" in signal
        assert signal["signal"] in ["buy", "sell", "hold"]

    def test_result_has_equity_curve(self, client, mock_downloader):
        """Test that result includes equity curve."""
        request_data = {
            "ticker": "SPY",
            "strategy_type": "buy_hold",
        }

        response = client.post("/api/v1/backtesting/run", json=request_data)

        assert response.status_code == 200
        result = response.json()["result"]
        equity_curve = result["equity_curve"]

        assert isinstance(equity_curve, list)
        assert len(equity_curve) > 0

        # Check equity curve point structure
        point = equity_curve[0]
        assert "date" in point
        assert "equity" in point
        assert "cash" in point
        assert "return" in point
        assert "return_pct" in point
