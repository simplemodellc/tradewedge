"""Tests for technical indicators."""

import pandas as pd
import pytest

from app.studies import (
    ATR,
    CCI,
    DEMA,
    EMA,
    HMA,
    MACD,
    MFI,
    OBV,
    ROC,
    RSI,
    SMA,
    TEMA,
    VWAP,
    WMA,
    AD,
    BollingerBands,
    IndicatorFactory,
    KeltnerChannels,
    StandardDeviation,
    Stochastic,
    VolumeSMA,
    WilliamsR,
)


@pytest.fixture
def sample_price_data():
    """Create sample OHLCV data for testing."""
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


class TestIndicatorFactory:
    """Tests for IndicatorFactory."""

    def test_create_sma(self):
        """Test creating SMA indicator."""
        indicator = IndicatorFactory.create("sma", {"length": 20})
        assert isinstance(indicator, SMA)
        assert indicator.length == 20

    def test_create_rsi(self):
        """Test creating RSI indicator."""
        indicator = IndicatorFactory.create("rsi", {"length": 14})
        assert isinstance(indicator, RSI)
        assert indicator.length == 14

    def test_create_unknown_indicator(self):
        """Test creating unknown indicator raises error."""
        with pytest.raises(ValueError, match="Unknown indicator"):
            IndicatorFactory.create("unknown")

    def test_create_with_invalid_params(self):
        """Test creating indicator with invalid parameters."""
        with pytest.raises(ValueError, match="Invalid parameters"):
            IndicatorFactory.create("sma", {"invalid_param": 20})

    def test_list_indicators(self):
        """Test listing all available indicators."""
        indicators = IndicatorFactory.list_indicators()
        assert isinstance(indicators, dict)
        assert len(indicators) > 0
        assert "sma" in indicators
        assert "rsi" in indicators
        assert "category" in indicators["sma"]
        assert "params" in indicators["sma"]

    def test_indicator_aliases(self):
        """Test that indicator aliases work."""
        bb1 = IndicatorFactory.create("bb")
        bb2 = IndicatorFactory.create("bbands")
        bb3 = IndicatorFactory.create("bollingerbands")
        assert type(bb1) == type(bb2) == type(bb3)


class TestTrendIndicators:
    """Tests for trend indicators."""

    def test_sma_calculation(self, sample_price_data):
        """Test SMA calculation."""
        indicator = SMA(length=20)
        result = indicator.calculate(sample_price_data)
        assert "SMA_20" in result.columns
        assert result["SMA_20"].notna().sum() > 0

    def test_ema_calculation(self, sample_price_data):
        """Test EMA calculation."""
        indicator = EMA(length=20)
        result = indicator.calculate(sample_price_data)
        assert "EMA_20" in result.columns
        assert result["EMA_20"].notna().sum() > 0

    def test_wma_calculation(self, sample_price_data):
        """Test WMA calculation."""
        indicator = WMA(length=20)
        result = indicator.calculate(sample_price_data)
        assert "WMA_20" in result.columns
        assert result["WMA_20"].notna().sum() > 0

    def test_dema_calculation(self, sample_price_data):
        """Test DEMA calculation."""
        indicator = DEMA(length=20)
        result = indicator.calculate(sample_price_data)
        assert "DEMA_20" in result.columns
        assert result["DEMA_20"].notna().sum() > 0

    def test_tema_calculation(self, sample_price_data):
        """Test TEMA calculation."""
        indicator = TEMA(length=20)
        result = indicator.calculate(sample_price_data)
        assert "TEMA_20" in result.columns
        assert result["TEMA_20"].notna().sum() > 0

    def test_hma_calculation(self, sample_price_data):
        """Test HMA calculation."""
        indicator = HMA(length=20)
        result = indicator.calculate(sample_price_data)
        assert "HMA_20" in result.columns
        assert result["HMA_20"].notna().sum() > 0


class TestMomentumIndicators:
    """Tests for momentum indicators."""

    def test_rsi_calculation(self, sample_price_data):
        """Test RSI calculation."""
        indicator = RSI(length=14)
        result = indicator.calculate(sample_price_data)
        assert "RSI_14" in result.columns
        assert result["RSI_14"].notna().sum() > 0
        # RSI should be between 0 and 100
        assert result["RSI_14"].dropna().min() >= 0
        assert result["RSI_14"].dropna().max() <= 100

    def test_macd_calculation(self, sample_price_data):
        """Test MACD calculation."""
        indicator = MACD(fast=12, slow=26, signal=9)
        result = indicator.calculate(sample_price_data)
        assert "MACD_12_26_9" in result.columns
        assert "MACDh_12_26_9" in result.columns
        assert "MACDs_12_26_9" in result.columns

    def test_stochastic_calculation(self, sample_price_data):
        """Test Stochastic calculation."""
        indicator = Stochastic(k=14, d=3, smooth_k=3)
        result = indicator.calculate(sample_price_data)
        assert "STOCHk_14_3_3" in result.columns
        assert "STOCHd_14_3_3" in result.columns

    def test_cci_calculation(self, sample_price_data):
        """Test CCI calculation."""
        indicator = CCI(length=20)
        result = indicator.calculate(sample_price_data)
        assert "CCI_20" in result.columns
        assert result["CCI_20"].notna().sum() > 0

    def test_roc_calculation(self, sample_price_data):
        """Test ROC calculation."""
        indicator = ROC(length=10)
        result = indicator.calculate(sample_price_data)
        assert "ROC_10" in result.columns
        assert result["ROC_10"].notna().sum() > 0

    def test_willr_calculation(self, sample_price_data):
        """Test Williams %R calculation."""
        indicator = WilliamsR(length=14)
        result = indicator.calculate(sample_price_data)
        assert "WILLR_14" in result.columns
        assert result["WILLR_14"].notna().sum() > 0


class TestVolatilityIndicators:
    """Tests for volatility indicators."""

    def test_bollinger_bands_calculation(self, sample_price_data):
        """Test Bollinger Bands calculation."""
        indicator = BollingerBands(length=20, std=2.0)
        result = indicator.calculate(sample_price_data)
        assert "BBL_20_2.0" in result.columns
        assert "BBM_20_2.0" in result.columns
        assert "BBU_20_2.0" in result.columns
        assert "BBB_20_2.0" in result.columns
        assert "BBP_20_2.0" in result.columns

    def test_atr_calculation(self, sample_price_data):
        """Test ATR calculation."""
        indicator = ATR(length=14)
        result = indicator.calculate(sample_price_data)
        assert "ATR_14" in result.columns
        assert result["ATR_14"].notna().sum() > 0

    def test_keltner_channels_calculation(self, sample_price_data):
        """Test Keltner Channels calculation."""
        indicator = KeltnerChannels(length=20, scalar=2.0)
        result = indicator.calculate(sample_price_data)
        assert "KCL_20_2.0" in result.columns
        assert "KCB_20_2.0" in result.columns
        assert "KCU_20_2.0" in result.columns

    def test_standard_deviation_calculation(self, sample_price_data):
        """Test Standard Deviation calculation."""
        indicator = StandardDeviation(length=20)
        result = indicator.calculate(sample_price_data)
        assert "STDEV_20" in result.columns
        assert result["STDEV_20"].notna().sum() > 0


class TestVolumeIndicators:
    """Tests for volume indicators."""

    def test_obv_calculation(self, sample_price_data):
        """Test OBV calculation."""
        indicator = OBV()
        result = indicator.calculate(sample_price_data)
        assert "OBV" in result.columns
        assert result["OBV"].notna().sum() > 0

    def test_volume_sma_calculation(self, sample_price_data):
        """Test Volume SMA calculation."""
        indicator = VolumeSMA(length=20)
        result = indicator.calculate(sample_price_data)
        assert "Volume_SMA_20" in result.columns
        assert result["Volume_SMA_20"].notna().sum() > 0

    def test_vwap_calculation(self, sample_price_data):
        """Test VWAP calculation."""
        indicator = VWAP()
        result = indicator.calculate(sample_price_data)
        assert "VWAP" in result.columns
        assert result["VWAP"].notna().sum() > 0

    def test_mfi_calculation(self, sample_price_data):
        """Test MFI calculation."""
        indicator = MFI(length=14)
        result = indicator.calculate(sample_price_data)
        assert "MFI_14" in result.columns
        assert result["MFI_14"].notna().sum() > 0

    def test_ad_calculation(self, sample_price_data):
        """Test A/D calculation."""
        indicator = AD()
        result = indicator.calculate(sample_price_data)
        assert "AD" in result.columns
        assert result["AD"].notna().sum() > 0


class TestIndicatorValidation:
    """Tests for indicator validation."""

    def test_empty_dataframe(self):
        """Test indicator with empty DataFrame."""
        indicator = SMA(length=20)
        with pytest.raises(ValueError, match="DataFrame is empty"):
            indicator.calculate(pd.DataFrame())

    def test_missing_required_columns(self, sample_price_data):
        """Test indicator with missing required columns."""
        indicator = SMA(length=20)
        df = sample_price_data.drop(columns=["Close"])
        with pytest.raises(ValueError, match="Missing required columns"):
            indicator.calculate(df)

    def test_indicator_description(self):
        """Test getting indicator description."""
        indicator = SMA(length=20)
        description = indicator.get_description()
        assert "SMA" in description
        assert "20" in description
