# Stock Insights REST API

REST API built using Django REST Framework, offering authenticated stock data services and ML-based forecasting.

## Features

- Token-based User Authentication 
- Portfolio and Watchlist Management
- Real-Time Stock Price Streaming (via WebSocket)
- Stocks Lookup and Quote Retrieval
- Historical Chart Data 
- Market Index Summary and Status
- 7-Day Stock Forecast and Recommendation (Facebook Prophet)

## Project Structure

- `stockInsights/` – Root project config
- `user/` – User auth, profile, avatar, portfolio, watchlist
- `stocks/` – Stock lookup, chart, forecast, and live data
- `stocks/ml/` – ML-related data utils 

## ML Forecasting

- Source: 5-year price history from `yfinance`
- Forecast: 14-day prediction with 7-day visual
- Model: Facebook Prophet
- Output includes:
  - Price forecast
  - Percentage change
  - Action recommendation (buy/sell/hold)

## Real-Time Streaming

- WebSocket endpoint (via Channels)
- Currently, I have put up some handselected stocks for websocket subscription but 
 it can be easily changed by adding/removing symbols.

## Tech Stack

- Python, Django, Django REST Framework
- SQLite (dev DB)
- Channels + Websockets
- External APIs: Finnhub, Polygon.io, yfinance
- ML: Facebook Prophet

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # add your API keys
python manage.py migrate
python manage.py runserver
