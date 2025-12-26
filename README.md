# Stock Market Finance Application

A full-stack application for fetching, storing, and analyzing stock market data.

## Architecture

### Frontend (Streamlit)
- Interactive dashboard for stock data visualization
- Price charts (candlestick and line)
- Projection and analysis tools

```
frontend/
├── app.py              # Main Streamlit application
└── requirements.txt
```

## Setup

### Frontend Setup

```bash
cd frontend

# Create virtual environment (or use same as backend)
py -3.12 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py
```

The frontend will be available at: http://localhost:8501

## Features

### Stock Management
- Add stocks manually or fetch from Yahoo Finance
- View and manage tracked stocks
- Fetch historical price data

### Price Analysis
- View historical prices with interactive charts
- Candlestick and line chart options
- Volume analysis

### Projections
- Simple linear price projections
- Moving average calculations
- Volatility analysis

## API Endpoints

### Stocks
- `GET /api/v1/stocks/` - List all stocks
- `GET /api/v1/stocks/{id}` - Get stock by ID
- `GET /api/v1/stocks/symbol/{symbol}` - Get stock by symbol
- `POST /api/v1/stocks/` - Create stock manually
- `POST /api/v1/stocks/fetch/{symbol}` - Fetch and add stock from Yahoo Finance
- `PUT /api/v1/stocks/{id}` - Update stock
- `DELETE /api/v1/stocks/{id}` - Delete stock

### Prices
- `GET /api/v1/prices/{stock_id}` - Get price history
- `POST /api/v1/prices/fetch` - Fetch prices from Yahoo Finance
- `GET /api/v1/prices/{stock_id}/stats` - Get price statistics
- `GET /api/v1/prices/{stock_id}/moving-average` - Calculate moving average
- `GET /api/v1/prices/{stock_id}/projection` - Get price projection
- `GET /api/v1/prices/{stock_id}/volatility` - Get volatility metrics

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Application
APP_NAME=Stock Market Finance App
DEBUG=True

# Database (SQLite by default, or use PostgreSQL)
DATABASE_URL=sqlite:///./stock_market.db

# Optional: Alpha Vantage API key for additional data sources
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

## Data Sources

- **Yahoo Finance** (via yfinance) - Primary data source for stock information and prices
- **Alpha Vantage** (optional) - Can be integrated for additional market data

## Technology Stack

- **Frontend**: Streamlit, Plotly, Pandas
