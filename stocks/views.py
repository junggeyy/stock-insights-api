from django.shortcuts import render

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .finnhub_service import get_company_details, get_stocks, get_home_stocks, get_index_data, is_market_open

from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import requests


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def index_data(request):
    try:
        indices_data = get_index_data()
        market_status = is_market_open()
        return Response({
            "indices_data": indices_data,
            "market_status": market_status
            })
    except Exception as e:
        return Response({"detail": f"Error fetching index data: {str(e)}"}, status=500)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stock_details(request, symbol):
    try:
        data = get_company_details(symbol)
        return Response(data)
    except Exception as e:
        return Response({"detail": f"Error fetching stock data: {str(e)}"}, status=500)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stock_lookup(request, symbol):
    try:
        data = get_stocks(symbol)
        return Response(data)
    except Exception as e:
        return Response({"detail": f"Error fetching stock data: {str(e)}"}, status=500)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def home_stocks(request):
    HOME_PAGE_SYMBOLS = [
        "AAPL", "MSFT", "NVDA", "TSLA", "AMD",        # Tech
        "JNJ", "PFE", "MRNA", "UNH", "LLY",           # Healthcare
        "JPM", "BRK-B",  "BAC", "WFC", "GS"           # Finance
    ]

    try:
        data = get_home_stocks(HOME_PAGE_SYMBOLS)
        return Response(data)
    except Exception as e:
        return Response({"detail": f"Error fetching stocks: {str(e)}"}, status=500)

    
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_stock_chart(request, symbol):
    API_KEY = settings.POLYGON_API_KEY

    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date.date()}/{end_date.date()}?adjusted=true&sort=asc&limit=5000&apiKey={API_KEY}"

    try:
        resp = requests.get(url)
        data = resp.json()

        candles = [
            {
                "date": datetime.fromtimestamp(item["t"] / 1000).strftime("%Y-%m-%d"),
                "open": item["o"],
                "high": item["h"],
                "low": item["l"],
                "close": item["c"],
                "volume": item["v"]
            }
            for item in data.get("results", [])
        ]

        return Response({"symbol": symbol, "candles": candles})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def stock_analysis(request, symbol):
    from .ml.predictor import generate_forecast

    try:
        days_ahead = 7
        today_price, forecast = generate_forecast(symbol, days=14)

        # Get the prediction for 7 days ahead
        target_date = datetime.today().date() + timedelta(days=days_ahead)
        target_row = forecast[forecast['ds'].dt.date == target_date]

        if target_row.empty:
            # Fallback: pick the next available forecast
            fallback_row = forecast[forecast['ds'].dt.date > datetime.today().date()].head(1)
            if fallback_row.empty:
                return Response({"error": f"No forecast available for {target_date}"}, status=404)
            target_row = fallback_row
            target_date = target_row.iloc[0]['ds'].date()

        predicted_price = target_row.iloc[0]['yhat']
        change_percent = ((predicted_price - today_price) / today_price) * 100

        # Recommendation logic
        if change_percent >= 3:
            recommendation = "buy"
        elif change_percent <= -3:
            recommendation = "sell"
        else:
            recommendation = "hold"

        # Cleaned 7-day forecast for frontend charting
        future_forecast = forecast[forecast['ds'].dt.date > datetime.today().date()].head(7)
        future_forecast = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        future_forecast['ds'] = future_forecast['ds'].astype(str)
        forecast_list = future_forecast.to_dict(orient='records')

        return Response({
            "symbol": symbol.upper(),
            "forecast": forecast_list,
            "recommendation": recommendation,
            "message": f"{symbol.upper()} is expected to change by {round(change_percent, 2)}% in {days_ahead} days, going from ${round(today_price,2)} to ${round(predicted_price,2)}. Recommended action: {recommendation.upper()}.",
            "current_price": round(today_price, 2),
            "predicted_price": round(predicted_price, 2),
            "change_percent": round(change_percent, 2)
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)