import os
import json
import asyncio
import websockets
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer


API_KEY = os.getenv("FINNHUB_API_KEY")
FINNHUB_WS_URL = f"wss://ws.finnhub.io?token={API_KEY}"

# defining 15 ticker symbols to display
HOME_PAGE_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD",         # Tech
    "JNJ", "PFE", "MRNA", "UNH", "LLY",            # Healthcare
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT",  "BINANCE:ADAUSDT", "BINANCE:SOLUSDT", "BINANCE:XRPUSDT" 
]

class HomeStockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser

        user = self.scope.get("user", None)

        if user is None or user == AnonymousUser() or user.is_anonymous:
            print("[Consumer] Anonymous user, rejecting WebSocket.")
            await self.close(code=403)
            return

        print(f"[Consumer] WebSocket accepted for: {user.username}")
        await self.accept()
        self.finnhub_task = asyncio.create_task(self.stream_from_finnhub())

    async def disconnect(self, close_code):
        print(f"[Consumer] Disconnecting WebSocket.")
        if hasattr(self, 'finnhub_ws'):
            try:
                await self.finnhub_ws.close()
                print("[Finnhub] WebSocket closed.")
            except Exception as e:
                print(f"[Finnhub] Error while closing: {e}")

        if hasattr(self, 'finnhub_task'):
            self.finnhub_task.cancel()

    async def stream_from_finnhub(self):
        all_prices = {symbol: None for symbol in HOME_PAGE_SYMBOLS}

        try:
            print("[Finnhub] Connecting to Finnhub WebSocket...")
            self.finnhub_ws = await websockets.connect(FINNHUB_WS_URL)
            print("[Finnhub] Connected.")

            for symbol in HOME_PAGE_SYMBOLS:
                await self.finnhub_ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))
                print(f"[Finnhub] Subscribed to {symbol}")

            # Send initial response with all symbols and no prices
            await self.send(text_data=json.dumps({
                "timestamp": datetime.now().isoformat(),
                "data": [{"symbol": sym, "price": None} for sym in HOME_PAGE_SYMBOLS]
            }))

            while True:
                try:
                    message = await asyncio.wait_for(self.finnhub_ws.recv(), timeout=5)
                    parsed = json.loads(message)

                    if parsed.get("type") == "trade":
                        for item in parsed.get("data", []):
                            symbol = item["s"]
                            price = item["p"]
                            all_prices[symbol] = price
                except asyncio.TimeoutError:
                    pass  # No updates in 5s

                # Send current prices (including symbols with price=None)
                formatted = [
                    {"symbol": sym, "price": all_prices[sym]}
                    for sym in HOME_PAGE_SYMBOLS
                ]

                await self.send(text_data=json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "data": formatted
                }))

                await asyncio.sleep(10)

        except Exception as e:
            print(f"[Finnhub] Error: {e}")
            await self.send(text_data=json.dumps({"error": str(e)}))