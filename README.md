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

1. ✅ Project Setup & Data Foundation
2. ⏳ Backend Core API
3. ⏳ Core Indicators Library
4. ⏳ Backtesting Engine Core
5. ⏳ Advanced Metrics & Complete Indicators
6. ⏳ Frontend Foundation
7. ⏳ Strategy Builder UI
8. ⏳ Results Visualization
9. ⏳ Strategy Management & Comparison
10. ⏳ Polish & Production Ready

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
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
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
