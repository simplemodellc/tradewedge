"""Tests for API endpoints."""

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
def mock_downloader(sample_ohlcv_data):
    """Create mock downloader with sample data."""
    with patch("app.routers.data.MarketDataDownloader") as mock:
        instance = Mock()
        instance.ticker = "SPY"  # Default ticker
        instance.download.return_value = sample_ohlcv_data
        instance.refresh_data.return_value = sample_ohlcv_data
        instance.get_summary.return_value = Mock(
            ticker="SPY",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
            total_records=len(sample_ohlcv_data),
            missing_dates=0,
            data_quality_score=100.0,
            model_dump=lambda mode=None: {
                "ticker": "SPY",
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-01-31T00:00:00",
                "total_records": len(sample_ohlcv_data),
                "missing_dates": 0,
                "data_quality_score": 100.0,
            },
        )
        mock.return_value = instance
        yield mock


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data


class TestDataEndpoints:
    """Tests for data management endpoints."""

    def test_get_data_summary(self, client, mock_downloader):
        """Test get data summary endpoint."""
        response = client.get("/api/v1/data/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "SPY"  # Default ticker is now SPY
        assert data["total_records"] > 0
        assert "data_quality_score" in data

    def test_download_data(self, client, mock_downloader):
        """Test download data endpoint."""
        request_data = {
            "ticker": "SPY",
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-01-31T23:59:59",
            "force_refresh": False,
        }

        response = client.post("/api/v1/data/download", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data
        assert data["summary"]["ticker"] == "SPY"

    def test_download_data_minimal(self, client, mock_downloader):
        """Test download data with minimal parameters."""
        response = client.post("/api/v1/data/download", json={"ticker": "SPY"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_refresh_data(self, client, mock_downloader):
        """Test refresh data endpoint."""
        response = client.post("/api/v1/data/refresh")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data

    def test_get_historical_data(self, client, mock_downloader):
        """Test get historical data endpoint."""
        response = client.get("/api/v1/data/historical")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)

    def test_get_historical_data_with_date_filters(self, client, mock_downloader):
        """Test get historical data with date filters."""
        params = {
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-01-31T23:59:59",
        }

        response = client.get("/api/v1/data/historical", params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_get_historical_data_with_limit(self, client, mock_downloader):
        """Test get historical data with limit."""
        params = {"limit": 10}

        response = client.get("/api/v1/data/historical", params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["count"] <= 10

    def test_get_historical_data_invalid_limit(self, client):
        """Test get historical data with invalid limit."""
        params = {"limit": 20000}  # Over the max limit

        response = client.get("/api/v1/data/historical", params=params)

        assert response.status_code == 422  # Validation error


class TestAPIDocumentation:
    """Tests for API documentation."""

    def test_openapi_schema(self, client):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "TradeWedge API"

    def test_docs_redirect(self, client):
        """Test that /docs is accessible."""
        response = client.get("/docs", follow_redirects=False)

        # Should redirect or return docs page
        assert response.status_code in [200, 307]


class TestErrorHandling:
    """Tests for error handling."""

    def test_download_data_invalid_json(self, client):
        """Test download data with invalid JSON."""
        response = client.post(
            "/api/v1/data/download",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    def test_download_data_missing_ticker(self, client, mock_downloader):
        """Test download data with default ticker."""
        # Ticker has a default value, so this should succeed
        response = client.post("/api/v1/data/download", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch("app.routers.data.MarketDataDownloader")
    def test_download_data_exception(self, mock_downloader, client):
        """Test download data when exception occurs."""
        instance = Mock()
        instance.download.side_effect = Exception("Download failed")
        mock_downloader.return_value = instance

        response = client.post("/api/v1/data/download", json={"ticker": "SPY"})

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
