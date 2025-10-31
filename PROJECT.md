# TradeWedge Project Status

**Last Updated:** October 30, 2025

## Project Overview

TradeWedge is a comprehensive backtesting platform for VTSAX trading strategies, built with a focus on data quality, testing, and maintainability.

## Completed Iterations

### ✅ Iteration 1: Data Foundation & VTSAX Downloader

**Components:**
- **VTSAX Data Downloader**: Complete historical data from inception (Nov 2000 - Present)
  - 6,277+ daily OHLCV records
  - Parquet caching for 90% storage efficiency
  - Timezone handling and data normalization

- **Data Validation Engine**:
  - OHLCV relationship validation (High >= Low, Close within range)
  - Missing business day detection
  - Data quality scoring (0-100 scale)
  - Current VTSAX score: 97.65/100

- **Testing**: 24 comprehensive tests
  - Downloader tests with mocking
  - Validator tests with edge cases
  - Test fixtures for various scenarios

### ✅ Iteration 2: Backend Core API & Database

**Components:**
- **Database Models**:
  - Strategy model with JSON configuration storage
  - Backtest model with performance metrics
  - Foreign key relationships with cascading deletes

- **Alembic Migrations**:
  - Auto-migration from SQLAlchemy models
  - Version control for schema changes
  - Upgrade/downgrade support

- **REST API Endpoints**:
  - `/health` - Health check
  - `/api/v1/data/summary` - Data quality metrics
  - `/api/v1/data/download` - Download/refresh historical data
  - `/api/v1/data/refresh` - Incremental updates
  - `/api/v1/data/historical` - Query with filters

- **Testing**: 15 API integration tests
  - FastAPI TestClient for all endpoints
  - Mock dependencies for reliability
  - Error handling validation

### ✅ Data Organization Improvements

**Structure:**
```
backend/data/
├── database/           # SQLite database (strategies, backtests)
├── market_data/        # VTSAX parquet cache
└── logs/               # Application logs (future)
```

**Features:**
- Single directory for all persistent data
- Excluded from git (only .gitkeep tracked)
- Auto-created on application startup
- Simple backup: copy data/ directory
- Documented in DATA_STRUCTURE.md

## Current Statistics

### Code Metrics
- **Total Tests**: 39 (100% passing)
- **Code Coverage**: 67%
- **Backend Lines**: ~422 statements
- **Test Lines**: ~300+ statements

### Data Metrics
- **VTSAX Records**: 6,277+ daily bars
- **Date Range**: 2000-11-13 to Present
- **Data Quality**: 97.65/100
- **Storage Size**: ~2-5 MB (compressed parquet)
- **Database Size**: ~36 KB (empty strategies/backtests)

### API Endpoints
- **Health/Status**: 2 endpoints
- **Data Management**: 4 endpoints
- **Documentation**: Auto-generated OpenAPI/Swagger

## Technology Stack

### Backend
- **Python**: 3.13
- **Framework**: FastAPI 0.109
- **ORM**: SQLAlchemy 2.0.44
- **Migrations**: Alembic 1.17
- **Validation**: Pydantic 2.12
- **Data**: pandas, numpy, yfinance
- **Storage**: Parquet (pyarrow), SQLite
- **Testing**: pytest, pytest-cov, httpx

### Frontend (Planned)
- **Next.js**: 14+
- **TypeScript**: 5.3+
- **Charts**: Lightweight Charts (TradingView)
- **UI**: shadcn/ui, Tailwind CSS
- **State**: TanStack Query

## File Structure

```
tradewedge/
├── backend/
│   ├── data/                    # Persistent storage (not in git)
│   │   ├── database/            # SQLite DB
│   │   ├── market_data/         # VTSAX cache
│   │   └── logs/                # Logs
│   ├── app/
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # DB session management
│   │   ├── main.py              # FastAPI app
│   │   ├── data/                # Data pipeline
│   │   │   ├── downloader.py    # VTSAX downloader
│   │   │   ├── validator.py     # Data validation
│   │   │   └── schemas.py       # Pydantic models
│   │   ├── models/              # Database models
│   │   │   ├── database.py      # SQLAlchemy models
│   │   │   └── schemas.py       # API schemas
│   │   └── routers/             # API endpoints
│   │       └── data.py          # Data endpoints
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite
│   │   ├── conftest.py          # Test fixtures
│   │   ├── test_api.py          # API tests
│   │   ├── test_downloader.py   # Downloader tests
│   │   └── test_validator.py    # Validator tests
│   ├── DATA_STRUCTURE.md        # Data documentation
│   └── requirements.txt         # Dependencies
└── frontend/                    # (To be implemented)
```

## API Usage Examples

### Get Data Summary
```bash
curl http://localhost:8000/api/v1/data/summary

# Response:
{
  "ticker": "VTSAX",
  "start_date": "2000-11-13T00:00:00",
  "end_date": "2025-10-29T00:00:00",
  "total_records": 6277,
  "missing_dates": 236,
  "data_quality_score": 97.65
}
```

### Download Historical Data
```bash
curl -X POST http://localhost:8000/api/v1/data/download \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "VTSAX",
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-12-31T23:59:59"
  }'
```

### Refresh Latest Data
```bash
curl -X POST http://localhost:8000/api/v1/data/refresh
```

### Query Historical Data
```bash
# Get last 10 records
curl "http://localhost:8000/api/v1/data/historical?limit=10"

# Get specific date range
curl "http://localhost:8000/api/v1/data/historical?start_date=2023-01-01T00:00:00&end_date=2023-12-31T23:59:59"
```

## Development Workflow

### Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head

# Run
uvicorn app.main:app --reload
```

### Testing
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test file
pytest tests/test_api.py -v

# Watch mode
pytest-watch
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Data Backup
```bash
# Backup all data
cd backend
tar -czf ../backup-$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf backup-YYYYMMDD.tar.gz
```

## Next Steps (Iteration 3)

### Core Indicators Library
- **Trend Indicators**: SMA, EMA, WMA, DEMA, TEMA, HMA
- **Momentum**: RSI, MACD, Stochastic, CCI, ROC, Williams %R
- **Volatility**: Bollinger Bands, ATR, Keltner Channels
- **Volume**: OBV, Volume SMA, VWAP, MFI
- **Testing**: Unit tests for each indicator with known outputs

### Implementation Plan
1. Base indicator class with common interface
2. Implement each indicator with pandas-ta
3. Comprehensive tests with edge cases
4. Performance benchmarks for large datasets
5. Documentation with usage examples

## Notes

- All data stored locally in `backend/data/` (not in git)
- Database schema managed via Alembic migrations
- Market data cached in efficient Parquet format
- Tests run fast with mocked external dependencies
- API documented automatically via OpenAPI
- Ready for incremental data updates

## Resources

- **Repository**: https://github.com/simplemodellc/tradewedge
- **API Docs**: http://localhost:8000/docs (when running)
- **Data Structure**: See `backend/DATA_STRUCTURE.md`
- **Project Plan**: See main `README.md`
