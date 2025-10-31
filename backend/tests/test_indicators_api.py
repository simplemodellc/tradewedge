"""Tests for indicators API endpoints."""

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_market_data():
    """Create mock market data."""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    df = pd.DataFrame(
        {
            "Open": range(100, 200),
            "High": range(105, 205),
            "Low": range(95, 195),
            "Close": range(100, 200),
            "Volume": [1000000 + i * 10000 for i in range(100)],
        },
        index=dates,
    )
    return df


@pytest.fixture
def mock_downloader(mock_market_data):
    """Create mock downloader with sample data."""
    with patch("app.routers.indicators.MarketDataDownloader") as mock:
        instance = Mock()
        instance.download.return_value = mock_market_data
        mock.return_value = instance
        yield mock


class TestIndicatorsListEndpoint:
    """Tests for indicators list endpoint."""

    def test_list_indicators(self, client):
        """Test listing all indicators."""
        response = client.get("/api/v1/indicators/list")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "indicators" in data
        assert "count" in data
        assert data["count"] > 0

        # Check that we have all major indicator types
        indicator_names = [ind["name"] for ind in data["indicators"]]
        assert "sma" in indicator_names
        assert "rsi" in indicator_names
        assert "macd" in indicator_names
        assert "bbands" in indicator_names or "bb" in indicator_names

    def test_list_indicators_structure(self, client):
        """Test that indicator metadata has correct structure."""
        response = client.get("/api/v1/indicators/list")
        data = response.json()

        # Check first indicator has required fields
        first_indicator = data["indicators"][0]
        assert "name" in first_indicator
        assert "class" in first_indicator
        assert "category" in first_indicator
        assert "params" in first_indicator
        assert "description" in first_indicator


class TestCalculateIndicatorEndpoint:
    """Tests for calculate indicator endpoints."""

    def test_calculate_sma_post(self, client, mock_downloader):
        """Test calculating SMA via POST."""
        request_data = {
            "ticker": "SPY",
            "indicator": "sma",
            "params": {"length": 20},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["ticker"] == "SPY"
        assert data["indicator"] == "sma"
        assert "SMA_20" in data["columns"]
        assert len(data["data"]) > 0

    def test_calculate_rsi_post(self, client, mock_downloader):
        """Test calculating RSI via POST."""
        request_data = {
            "ticker": "SPY",
            "indicator": "rsi",
            "params": {"length": 14},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "RSI_14" in data["columns"]

    def test_calculate_macd_post(self, client, mock_downloader):
        """Test calculating MACD via POST."""
        request_data = {
            "ticker": "SPY",
            "indicator": "macd",
            "params": {"fast": 12, "slow": 26, "signal": 9},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "MACD_12_26_9" in data["columns"]
        assert "MACDh_12_26_9" in data["columns"]
        assert "MACDs_12_26_9" in data["columns"]

    def test_calculate_bollinger_bands_post(self, client, mock_downloader):
        """Test calculating Bollinger Bands via POST."""
        request_data = {
            "ticker": "SPY",
            "indicator": "bb",
            "params": {"length": 20, "std": 2.0},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert any("BBL" in col for col in data["columns"])
        assert any("BBU" in col for col in data["columns"])

    def test_calculate_with_date_range(self, client, mock_downloader):
        """Test calculating indicator with date range."""
        request_data = {
            "ticker": "SPY",
            "indicator": "sma",
            "params": {"length": 20},
            "start_date": "2023-02-01T00:00:00",
            "end_date": "2023-03-01T00:00:00",
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        # Data should be filtered by date range
        assert len(data["data"]) < 100  # Less than full dataset

    def test_calculate_sma_get(self, client, mock_downloader):
        """Test calculating SMA via GET."""
        response = client.get("/api/v1/indicators/calculate?ticker=SPY&indicator=sma")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["ticker"] == "SPY"
        assert data["indicator"] == "sma"

    def test_calculate_invalid_indicator(self, client, mock_downloader):
        """Test calculating invalid indicator."""
        request_data = {
            "ticker": "SPY",
            "indicator": "invalid",
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 400
        assert "detail" in response.json()

    def test_calculate_invalid_params(self, client, mock_downloader):
        """Test calculating with invalid parameters."""
        request_data = {
            "ticker": "SPY",
            "indicator": "sma",
            "params": {"invalid_param": 20},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 400

    @patch("app.routers.indicators.MarketDataDownloader")
    def test_calculate_with_no_data(self, mock_downloader, client):
        """Test calculating indicator when no data available."""
        instance = Mock()
        instance.download.return_value = None
        mock_downloader.return_value = instance

        request_data = {
            "ticker": "INVALID",
            "indicator": "sma",
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 404
        assert "No data available" in response.json()["detail"]


class TestIndicatorDataFormat:
    """Tests for indicator data format."""

    def test_data_serialization(self, client, mock_downloader):
        """Test that data is properly serialized to JSON."""
        request_data = {
            "ticker": "SPY",
            "indicator": "sma",
            "params": {"length": 20},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Check data structure
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # Check first record structure
        first_record = data["data"][0]
        assert "Date" in first_record
        assert "Close" in first_record
        assert isinstance(first_record["Close"], (int, float))

    def test_column_list_included(self, client, mock_downloader):
        """Test that column list is included in response."""
        request_data = {
            "ticker": "SPY",
            "indicator": "sma",
            "params": {"length": 20},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "columns" in data
        assert isinstance(data["columns"], list)
        assert "Close" in data["columns"]
        assert "SMA_20" in data["columns"]

    def test_record_count_matches(self, client, mock_downloader):
        """Test that record count matches data length."""
        request_data = {
            "ticker": "SPY",
            "indicator": "sma",
            "params": {"length": 20},
        }

        response = client.post("/api/v1/indicators/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == len(data["data"])
