"""Data management API endpoints."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.data.downloader import VTSAXDownloader
from app.data.schemas import DataDownloadRequest, MarketDataSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/summary", response_model=MarketDataSummary)
async def get_data_summary() -> MarketDataSummary:
    """
    Get summary statistics for VTSAX historical data.

    Returns:
        MarketDataSummary with statistics
    """
    try:
        downloader = VTSAXDownloader()
        summary = downloader.get_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def download_data(request: DataDownloadRequest) -> JSONResponse:
    """
    Download VTSAX historical data.

    Args:
        request: Download request parameters

    Returns:
        JSON response with download status
    """
    try:
        downloader = VTSAXDownloader()
        df = downloader.download(
            start_date=request.start_date,
            end_date=request.end_date,
            force_refresh=request.force_refresh,
        )

        summary = downloader.get_summary(df)

        return JSONResponse(
            content={
                "status": "success",
                "message": f"Downloaded {len(df)} records",
                "summary": summary.model_dump(mode="json"),
            }
        )
    except Exception as e:
        logger.error(f"Error downloading data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_data() -> JSONResponse:
    """
    Refresh cached VTSAX data with latest available data.

    Returns:
        JSON response with refresh status
    """
    try:
        downloader = VTSAXDownloader()
        df = downloader.refresh_data()

        summary = downloader.get_summary(df)

        return JSONResponse(
            content={
                "status": "success",
                "message": f"Refreshed data with {len(df)} records",
                "summary": summary.model_dump(mode="json"),
            }
        )
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_data(
    start_date: Optional[datetime] = Query(None, description="Start date for data"),
    end_date: Optional[datetime] = Query(None, description="End date for data"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Limit number of records"),
) -> JSONResponse:
    """
    Get historical VTSAX data.

    Args:
        start_date: Start date filter
        end_date: End date filter
        limit: Maximum number of records to return

    Returns:
        JSON response with historical data
    """
    try:
        downloader = VTSAXDownloader()
        df = downloader.download(start_date=start_date, end_date=end_date)

        if limit:
            df = df.tail(limit)

        # Convert to records format with date as ISO string
        df_copy = df.reset_index()
        df_copy["Date"] = df_copy["Date"].dt.strftime("%Y-%m-%dT%H:%M:%S")
        data = df_copy.to_dict(orient="records")

        return JSONResponse(content={"status": "success", "data": data, "count": len(data)})
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
