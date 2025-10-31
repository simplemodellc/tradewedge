# TradeWedge

A comprehensive backtesting platform for VTSAX trading strategies with end-of-day data analysis.

## Overview

TradeWedge is a full-stack application designed to backtest trading strategies on VTSAX using historical end-of-day market data. It features a comprehensive suite of technical indicators, interactive visualizations, and detailed performance metrics.

## Features

- **Historical Data Management**: Download and cache complete VTSAX historical data
- **Comprehensive Technical Indicators**:
  - Trend: SMA, EMA, WMA, DEMA, TEMA, HMA
  - Momentum: RSI, MACD, Stochastic, CCI, ROC, Williams %R
  - Volatility: Bollinger Bands, ATR, Keltner Channels, Standard Deviation
  - Volume: OBV, Volume SMA, VWAP, MFI
- **Flexible Backtesting**: Test strategies across multiple timeframes (daily, weekly, monthly)
- **Rich Visualizations**: Interactive charts with signal overlays, equity curves, and performance dashboards
- **Strategy Management**: Save, load, and compare multiple strategies
- **Performance Metrics**: Comprehensive analytics including Sharpe ratio, max drawdown, win rate, CAGR

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI**: High-performance REST API
- **SQLite**: Local database for strategies and results
- **pandas-ta**: Technical analysis indicators
- **yfinance**: Historical market data
- **Pydantic**: Data validation
- **pytest**: Testing framework

### Frontend
- **Next.js 14+**: React framework with App Router
- **TypeScript**: Type-safe development
- **Lightweight Charts**: Professional trading charts
- **TanStack Query**: Data fetching and caching
- **shadcn/ui**: UI component library
- **Tailwind CSS**: Styling

## Project Structure

```
tradewedge/
├── backend/              # Python FastAPI backend
│   ├── app/             # Application code
│   │   ├── data/        # Data downloading and management
│   │   ├── studies/     # Technical indicators
│   │   ├── backtesting/ # Backtesting engine
│   │   ├── models/      # Database models
│   │   └── routers/     # API endpoints
│   └── tests/           # Backend tests
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/         # Next.js pages
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities and API client
│   └── tests/           # Frontend tests
└── README.md
```

## Development Plan

The project is being built iteratively with testing at each step:

1. ✅ **Project Setup & Data Foundation** - Complete VTSAX data pipeline with validation
2. ✅ **Backend Core API** - Database models, migrations, and REST endpoints
3. ⏳ Core Indicators Library
4. ⏳ Backtesting Engine Core
5. ⏳ Advanced Metrics & Complete Indicators
6. ⏳ Frontend Foundation
7. ⏳ Strategy Builder UI
8. ⏳ Results Visualization
9. ⏳ Strategy Management & Comparison
10. ⏳ Polish & Production Ready

### Current Status

**Completed:**
- ✅ VTSAX data downloader with yfinance integration (6,277+ records)
- ✅ Data validation and quality scoring (97.65/100)
- ✅ Parquet caching for efficient storage
- ✅ FastAPI backend with CORS and configuration
- ✅ SQLAlchemy ORM with Alembic migrations
- ✅ Strategy and Backtest database models
- ✅ RESTful API endpoints for data management
- ✅ Comprehensive test suite (39 tests, 67% coverage)
- ✅ Organized data persistence structure

**Next Up:**
- Core technical indicators library (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
- Backtesting engine with buy/sell simulation

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- pip and npm/yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
```

The backend will create a `data/` directory for persistent storage:
- `data/database/` - SQLite database (strategies, backtests)
- `data/market_data/` - VTSAX historical data cache
- `data/logs/` - Application logs

See [DATA_STRUCTURE.md](backend/DATA_STRUCTURE.md) for details.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Data Persistence

All application data is stored locally in `backend/data/` (excluded from git):

- **Historical Market Data**: Downloaded once and cached locally in Parquet format
- **Incremental Updates**: API endpoints refresh only new data as needed
- **Database**: SQLite stores strategies and backtest results
- **Backup**: Simply copy the `data/` directory to backup all application data

### Initial Data Download

On first API call, VTSAX data is automatically downloaded (~6,277 records from 2000):
```bash
curl http://localhost:8000/api/v1/data/summary
```

### Refresh Data

To update with latest market data:
```bash
curl -X POST http://localhost:8000/api/v1/data/refresh
```

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:e2e
```

## License

MIT

## Contributing

This is a personal project, but suggestions and feedback are welcome!
