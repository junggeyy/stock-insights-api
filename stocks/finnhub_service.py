from django.utils import timezone
import finnhub
import requests
from django.conf import settings
import yfinance as yf


client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)

INDEX_LABELS = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "NASDAQ"
}

def get_index_data():
    symbols = INDEX_LABELS.keys()
    data = {}
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            continue

        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2]
        change_percent = ((current_price - previous_close) / previous_close) * 100

        label = INDEX_LABELS[symbol]
        data[label] = {
            "price": round(current_price, 2),
            "change_percent": round(change_percent, 2)
        }
    return data

def is_market_open():
    market_status = client.market_status(exchange='US').get("isOpen")
    return market_status


def get_company_details(symbol):
    profile = client.company_profile2(symbol=symbol)
    recommendation_data = client.recommendation_trends(symbol) # returns a list, we only take the first data
    recommendation = recommendation_data[0] if recommendation_data else {}
    price = client.quote(symbol)    # current price of the stock

    buy = recommendation.get("buy", 0)
    sell = recommendation.get("sell", 0)
    hold = recommendation.get("hold", 0)

    total = buy + sell + hold

    if total > 0:
        buy_percent = round((buy / total) * 100)
        sell_percent = round((sell / total) * 100)
        hold_percent = round((hold / total) * 100)
    else:
        buy_percent = sell_percent = hold_percent = 0.0

    return {
        "symbol": symbol.upper(),
        "current_price": price.get("c"),
        "company_name": profile.get("name"),
        "exchange": profile.get("exchange"),
        "ipo": profile.get("ipo"),
        "market_cap": profile.get("marketCapitalization"),
        "currency": profile.get("currency"),
        "share_outstanding": profile.get("shareOutstanding"),
        "website": profile.get("weburl"),
        "country": profile.get("country"),
        "industry": profile.get("finnhubIndustry"),
        "recommendation": {
            "total": total,
            "buy": buy_percent,
            "sell": sell_percent,
            "hold": hold_percent
        }
    }

def get_stocks(symbol):
    # reverted back to request method, as SDK didn't support exchange filter
    url = "https://finnhub.io/api/v1/search"
    params = {
        "q": symbol,
        "exchange": "US",
        "token": settings.FINNHUB_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()
    results = data.get("result", [])

    if results:
        first = results[0]
        return {
            "description": first.get("description"),
            "symbol": first.get("symbol")
        }

    return {"detail": "No US-listed stock found"}

def get_home_stocks(HOME_PAGE_SYMBOLS):
    results = []
    for sym in HOME_PAGE_SYMBOLS:
        try:
            quote = client.quote(sym)
            profile = client.company_profile2(symbol=sym)
            results.append({
                "symbol": sym,
                "company": profile.get("name", "N/A"),
                "price": quote.get("c")  # current price
            })
        except Exception as e:
            results.append({
                "symbol": sym,
                "company": "N/A",
                "price": None
            })

    return {
        "timestamp": timezone.now(),
        "data": results
    }