from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
from prophet import Prophet

app = Flask(__name__)
def fetch_stock_data(symbol):
    df = yf.download(symbol, start="2020-01-01", end="2025-01-01")
    df = df.reset_index()[['Date', 'Close']]
    df.columns = ['ds', 'y']
    return df
def add_technical_indicators(df):
    df_ti = df.copy()
    df_ti['SMA_20'] = df_ti['y'].rolling(window=20).mean()
    df_ti['EMA_20'] = df_ti['y'].ewm(span=20, adjust=False).mean()

    delta = df_ti['y'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df_ti['RSI'] = 100 - (100 / (1 + rs))
    return df_ti


def predict_stock(symbol, days=365): 
    df = yf.download(symbol, start="2020-01-01", end="2025-04-15")
    df = df.reset_index()[['Date', 'Close']]
    df.columns = ['ds', 'y']
    df_ti = add_technical_indicators(df)
    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    forecast = forecast[forecast['ds'] >= '2025-05-01']
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    return df_ti.dropna().tail(60), forecast


@app.route("/predict/<symbol>", methods=["GET"])
def predict(symbol):
    try:
        target_date = request.args.get("date")  
        if not target_date:
            return jsonify({"error": "Please provide a target date like ?date=2025-05-15"}), 400

        df, forecast = predict_stock(symbol, days=365)  
        target_row = forecast[forecast['ds'] == target_date]

        if target_row.empty:
            return jsonify({"error": f"No prediction available for {target_date}"}), 404

        return jsonify({
            "symbol": symbol.upper(),
            "date": target_date,
            "predicted_price": target_row.iloc[0]['yhat'],
            "lower_bound": target_row.iloc[0]['yhat_lower'],
            "upper_bound": target_row.iloc[0]['yhat_upper']
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
