import yfinance as yf
import pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta

def fetch_stock_data(symbol):
    df = yf.download(symbol, start="2020-01-01", end=datetime.today())
    df = df.reset_index()[['Date', 'Close']]
    df.columns = ['ds', 'y']
    return df

def generate_forecast(symbol, days=14):
    df = fetch_stock_data(symbol)
    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    today_price = df.iloc[-1]['y']

    return today_price, forecast