# Data Storage Structure

TradeWedge stores all persistent data locally in the `data/` directory. This directory is excluded from version control to keep your data private and avoid repository bloat.

## Directory Structure

```
backend/data/
├── database/
│   └── tradewedge.db          # SQLite database (strategies, backtests)
├── market_data/
│   └── vtsax_historical.parquet   # VTSAX OHLCV data cache
└── logs/
    └── app.log                # Application logs (future)
```

## Data Components

### 1. Database (`data/database/`)

**File**: `tradewedge.db`

SQLite database containing:
- **Strategies Table**: User-defined trading strategies with configuration
- **Backtests Table**: Historical backtest results with performance metrics

Schema managed via Alembic migrations in `alembic/versions/`.

### 2. Market Data Cache (`data/market_data/`)

**File**: `vtsax_historical.parquet`

Parquet file containing complete VTSAX historical data:
- **Format**: Apache Parquet (columnar, compressed)
- **Columns**: Date (index), Open, High, Low, Close, Volume, Dividends, Stock Splits, Capital Gains
- **Date Range**: 2000-11-13 to present (~6,277+ records)
- **Update Strategy**: Cached locally, refreshed on demand via API

**Benefits of Parquet:**
- Fast read/write performance
- Efficient compression (~90% smaller than CSV)
- Preserves data types
- Column-based queries

### 3. Logs (`data/logs/`)

Application logs for debugging and monitoring (future feature).

## Data Persistence

### Initial Download
On first run, VTSAX data is downloaded from yfinance and cached locally:
```bash
# Automatically happens when accessing data endpoints
curl http://localhost:8000/api/v1/data/summary
```

### Incremental Updates
To refresh with latest data:
```bash
curl -X POST http://localhost:8000/api/v1/data/refresh
```

The system intelligently:
1. Loads existing cached data if available
2. Only downloads missing date ranges when refreshing
3. Validates data quality before caching

### Manual Backup

To backup your data:
```bash
# From backend directory
tar -czf ../tradewedge-backup-$(date +%Y%m%d).tar.gz data/
```

To restore:
```bash
tar -xzf tradewedge-backup-YYYYMMDD.tar.gz
```

## Data Quality

Market data includes quality metrics:
- **Completeness**: Missing business days detection
- **Validation**: OHLCV relationship checks
- **Quality Score**: 0-100 score (VTSAX typically 97-98/100)

View data quality:
```bash
curl http://localhost:8000/api/v1/data/summary
```

## Storage Requirements

- **Database**: ~1-10 MB (grows with strategies and backtests)
- **VTSAX Cache**: ~2-5 MB (parquet compressed)
- **Total**: ~5-15 MB for typical usage

## Migration & Schema Evolution

Database schema changes are managed through Alembic:
```bash
# Create a migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Security Notes

- Data directory is in `.gitignore` - never committed to repository
- Database contains only trading configurations and results
- No sensitive credentials stored (use environment variables)
- Consider encrypting backups for sensitive strategies
