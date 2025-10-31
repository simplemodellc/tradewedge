"""API endpoints for technical indicators."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.data.downloader import MarketDataDownloader
from app.studies import IndicatorFactory, IndicatorListResponse, IndicatorRequest, IndicatorResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("/list", response_model=IndicatorListResponse)
async def list_indicators() -> IndicatorListResponse:
    """
    Get a list of all available technical indicators.

    Returns:
        IndicatorListResponse with metadata for all indicators
    """
    try:
        indicators_dict = IndicatorFactory.list_indicators()
        indicators_list = [
            {"name": name, **metadata} for name, metadata in indicators_dict.items()
        ]

        return IndicatorListResponse(
            status="success", indicators=indicators_list, count=len(indicators_list)
        )
    except Exception as e:
        logger.error(f"Error listing indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate", response_model=IndicatorResponse)
async def calculate_indicator(request: IndicatorRequest) -> IndicatorResponse:
    """
    Calculate a technical indicator on historical data.

    Args:
        request: IndicatorRequest with ticker, indicator name, and parameters

    Returns:
        IndicatorResponse with calculated indicator data
    """
    try:
        # Get historical data
        downloader = MarketDataDownloader(ticker=request.ticker)
        df = downloader.download()

        if df is None or df.empty:
            raise HTTPException(
                status_code=404, detail=f"No data available for {request.ticker}"
            )

        # Filter by date range if provided
        if request.start_date or request.end_date:
            if request.start_date:
                df = df[df.index >= request.start_date]
            if request.end_date:
                df = df[df.index <= request.end_date]

        # Create and calculate indicator
        indicator = IndicatorFactory.create(request.indicator, request.params)
        result_df = indicator.calculate(df)

        # Convert to JSON-serializable format
        result_df_copy = result_df.copy()
        result_df_copy.index = result_df_copy.index.strftime("%Y-%m-%dT%H:%M:%S")
        result_df_copy.index.name = "Date"  # Set index name for proper serialization
        data_dict = result_df_copy.reset_index().to_dict(orient="records")

        return IndicatorResponse(
            status="success",
            ticker=request.ticker,
            indicator=request.indicator,
            params=request.params,
            data=data_dict,
            count=len(data_dict),
            columns=list(result_df.columns),
        )

    except HTTPException:
        # Re-raise HTTPException as-is (don't wrap in 500)
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating indicator: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calculate", response_model=IndicatorResponse)
async def calculate_indicator_get(
    ticker: str = Query(default="SPY", description="Ticker symbol"),
    indicator: str = Query(..., description="Indicator name (e.g., 'sma', 'rsi')"),
    start_date: Optional[datetime] = Query(default=None, description="Start date"),
    end_date: Optional[datetime] = Query(default=None, description="End date"),
) -> IndicatorResponse:
    """
    Calculate a technical indicator using GET request (for simple indicators with default params).

    Args:
        ticker: Ticker symbol (default: SPY)
        indicator: Indicator name
        start_date: Optional start date
        end_date: Optional end date

    Returns:
        IndicatorResponse with calculated indicator data
    """
    request = IndicatorRequest(
        ticker=ticker,
        indicator=indicator,
        params={},
        start_date=start_date,
        end_date=end_date,
    )
    return await calculate_indicator(request)
