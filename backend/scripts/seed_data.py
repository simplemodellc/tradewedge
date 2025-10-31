"""Seed database with initial ticker data for SPY and VTSAX."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import logging
from datetime import datetime

from app.database import SessionLocal, init_db
from app.models.database import Ticker
from app.data.downloader import MarketDataDownloader

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Ticker definitions with metadata
TICKERS_TO_SEED = [
    {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "asset_type": "ETF",
        "description": "Tracks the S&P 500 index. One of the largest and most liquid ETFs, "
        "representing large-cap U.S. equities across all sectors.",
    },
    {
        "symbol": "VTSAX",
        "name": "Vanguard Total Stock Market Index Fund",
        "asset_type": "Mutual Fund",
        "description": "Seeks to track the performance of the CRSP US Total Market Index. "
        "Provides exposure to the entire U.S. stock market, including small-, mid-, and large-cap stocks.",
    },
]


def seed_tickers():
    """Seed tickers table with SPY and VTSAX, and download their historical data."""
    logger.info("Starting database seeding...")

    # Initialize database (create tables if they don't exist)
    init_db()

    db = SessionLocal()
    try:
        for ticker_data in TICKERS_TO_SEED:
            symbol = ticker_data["symbol"]
            logger.info(f"\nProcessing {symbol}...")

            # Check if ticker already exists
            existing_ticker = db.query(Ticker).filter(Ticker.symbol == symbol).first()

            if existing_ticker:
                logger.info(f"  ✓ {symbol} already exists in database (ID: {existing_ticker.id})")
                ticker_obj = existing_ticker
            else:
                # Create new ticker entry
                ticker_obj = Ticker(
                    symbol=symbol,
                    name=ticker_data["name"],
                    asset_type=ticker_data["asset_type"],
                    description=ticker_data["description"],
                    is_active=True,
                )
                db.add(ticker_obj)
                db.commit()
                db.refresh(ticker_obj)
                logger.info(f"  ✓ Created {symbol} ticker entry (ID: {ticker_obj.id})")

            # Download historical data
            try:
                logger.info(f"  → Downloading {symbol} historical data...")
                downloader = MarketDataDownloader(ticker=symbol)
                df = downloader.download()

                # Get data summary
                summary = downloader.get_summary(df)

                # Update ticker with data metrics
                ticker_obj.last_updated = datetime.utcnow()
                ticker_obj.total_records = summary.total_records
                ticker_obj.data_quality_score = summary.data_quality_score
                db.commit()

                logger.info(f"  ✓ Downloaded {summary.total_records} records for {symbol}")
                logger.info(f"    Date range: {summary.start_date.date()} to {summary.end_date.date()}")
                logger.info(f"    Data quality: {summary.data_quality_score:.2f}/100")
                logger.info(f"    Missing dates: {summary.missing_dates}")

            except Exception as e:
                logger.error(f"  ✗ Error downloading {symbol} data: {e}")
                db.rollback()

        logger.info("\n" + "=" * 60)
        logger.info("Database seeding completed!")
        logger.info("=" * 60)

        # Summary
        all_tickers = db.query(Ticker).all()
        logger.info(f"\nTotal tickers in database: {len(all_tickers)}")
        for ticker in all_tickers:
            status = "✓ Active" if ticker.is_active else "✗ Inactive"
            logger.info(f"  {status} {ticker.symbol} - {ticker.name}")
            if ticker.total_records:
                logger.info(f"    {ticker.total_records} records, Quality: {ticker.data_quality_score:.2f}/100")

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_tickers()
