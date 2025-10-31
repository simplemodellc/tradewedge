"""Tests for data validator."""

import pandas as pd
import pytest

from app.data.validator import DataValidator


class TestDataValidator:
    """Test suite for DataValidator."""

    def test_validate_valid_ohlcv_dataframe(self, sample_ohlcv_data):
        """Test validation of valid OHLCV data."""
        is_valid, errors = DataValidator.validate_ohlcv_dataframe(sample_ohlcv_data, "VTSAX")

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_ohlcv_dataframe(self, invalid_ohlcv_data):
        """Test validation of invalid OHLCV data."""
        is_valid, errors = DataValidator.validate_ohlcv_dataframe(invalid_ohlcv_data, "VTSAX")

        assert is_valid is False
        assert len(errors) > 0
        # Check for specific errors
        error_text = " ".join(errors)
        assert "High < Low" in error_text
        assert "negative" in error_text.lower() or "non-positive" in error_text.lower()

    def test_validate_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        empty_df = pd.DataFrame()
        is_valid, errors = DataValidator.validate_ohlcv_dataframe(empty_df, "VTSAX")

        assert is_valid is False
        assert any("empty" in error.lower() for error in errors)

    def test_validate_missing_columns(self):
        """Test validation with missing columns."""
        df = pd.DataFrame({"Open": [100], "High": [105], "Low": [95]})  # Missing Close and Volume
        is_valid, errors = DataValidator.validate_ohlcv_dataframe(df, "VTSAX")

        assert is_valid is False
        assert any("missing" in error.lower() for error in errors)

    def test_validate_nan_values(self):
        """Test validation with NaN values."""
        df = pd.DataFrame(
            {
                "Open": [100, None, 102],
                "High": [105, 106, None],
                "Low": [95, 96, 97],
                "Close": [102, 103, 104],
                "Volume": [1000000, 1010000, 1020000],
            }
        )
        is_valid, errors = DataValidator.validate_ohlcv_dataframe(df, "VTSAX")

        assert is_valid is False
        assert any("NaN" in error for error in errors)

    def test_check_missing_dates_no_gaps(self, sample_ohlcv_data):
        """Test missing date detection with no gaps."""
        missing = DataValidator.check_missing_dates(sample_ohlcv_data, expected_frequency="B")

        assert len(missing) == 0

    def test_check_missing_dates_with_gaps(self, data_with_gaps):
        """Test missing date detection with gaps."""
        missing = DataValidator.check_missing_dates(data_with_gaps, expected_frequency="D")

        assert len(missing) > 0

    def test_check_missing_dates_empty_dataframe(self):
        """Test missing date detection with empty DataFrame."""
        empty_df = pd.DataFrame()
        missing = DataValidator.check_missing_dates(empty_df)

        assert len(missing) == 0

    def test_calculate_data_quality_score_perfect(self, sample_ohlcv_data):
        """Test quality score calculation for perfect data."""
        missing_dates = DataValidator.check_missing_dates(sample_ohlcv_data)
        score = DataValidator.calculate_data_quality_score(sample_ohlcv_data, missing_dates)

        assert score == 100.0

    def test_calculate_data_quality_score_with_issues(self, invalid_ohlcv_data):
        """Test quality score calculation for data with issues."""
        missing_dates = DataValidator.check_missing_dates(invalid_ohlcv_data)
        score = DataValidator.calculate_data_quality_score(invalid_ohlcv_data, missing_dates)

        assert 0 <= score < 100

    def test_calculate_data_quality_score_empty(self):
        """Test quality score calculation for empty DataFrame."""
        empty_df = pd.DataFrame()
        score = DataValidator.calculate_data_quality_score(empty_df, [])

        assert score == 0.0

    def test_create_summary(self, sample_ohlcv_data):
        """Test summary creation."""
        summary = DataValidator.create_summary(sample_ohlcv_data, "VTSAX")

        assert summary.ticker == "VTSAX"
        assert summary.total_records == len(sample_ohlcv_data)
        assert summary.data_quality_score >= 0
        assert summary.data_quality_score <= 100
        assert summary.start_date < summary.end_date

    def test_create_summary_empty(self):
        """Test summary creation with empty DataFrame."""
        empty_df = pd.DataFrame()
        summary = DataValidator.create_summary(empty_df, "VTSAX")

        assert summary.ticker == "VTSAX"
        assert summary.total_records == 0
        assert summary.data_quality_score == 0.0
