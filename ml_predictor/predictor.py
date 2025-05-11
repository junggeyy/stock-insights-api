import yfinance as yf
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

def fetch_stock_data(symbol):
    df = yf.download(symbol, start="2020-01-01", end="2025-01-01")
    df = df.reset_index()[['Date', 'Close']]
    df.columns = ['ds', 'y']
    return df

def predict_stock(symbol, days=30):
    df = fetch_stock_data(symbol)
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    return df, forecast

def plot_forecast(df, forecast, symbol):
    plt.figure(figsize=(12, 6))
    plt.plot(df['ds'], df['y'], label="Historical", linewidth=2)
    plt.plot(forecast['ds'], forecast['yhat'], label="Forecast", linestyle='--')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.3, label='Confidence Interval')
    plt.title(f"{symbol.upper()} Stock Forecast")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def run_forecast(symbol):
    try:
        df, forecast = predict_stock(symbol)
        print(f"--- {symbol.upper()} 30-Day Forecast ---")
        print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30).to_string(index=False))
        plot_forecast(df, forecast, symbol)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    symbol = input("Enter stock ticker (e.g., AAPL, TSLA): ").upper()
    run_forecast(symbol)
