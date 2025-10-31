"""API endpoints for backtesting."""

import logging

from fastapi import APIRouter, HTTPException

from app.backtesting import BacktestEngine, BacktestRequest, BacktestResponse, StrategyFactory
from app.data.downloader import MarketDataDownloader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/backtesting", tags=["backtesting"])


@router.get("/strategies")
async def list_strategies() -> dict:
    """
    Get a list of all available trading strategies.

    Returns:
        Dictionary with available strategies and their metadata
    """
    try:
        strategies_dict = StrategyFactory.list_strategies()
        strategies_list = [
            {"name": name, **metadata} for name, metadata in strategies_dict.items()
        ]

        return {
            "status": "success",
            "strategies": strategies_list,
            "count": len(strategies_list),
        }
    except Exception as e:
        logger.error(f"Error listing strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest on historical data.

    Args:
        request: BacktestRequest with strategy, ticker, and configuration

    Returns:
        BacktestResponse with results and performance metrics
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
        if request.start_date:
            df = df[df.index >= request.start_date]
        if request.end_date:
            df = df[df.index <= request.end_date]

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="No data available for the specified date range",
            )

        # Create strategy
        strategy = StrategyFactory.create(
            request.strategy_type, request.strategy_params
        )

        # Run backtest
        engine = BacktestEngine(config=request.config)
        result = engine.run(
            strategy=strategy,
            df=df,
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return BacktestResponse(status="success", result=result)

    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
