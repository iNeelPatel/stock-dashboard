import time
import httpx
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Dict
from backend.app.core.config import settings
from backend.app.services.market_data.base import (
    MarketDataProvider, QuoteData, CandleData, SearchResult, ProviderHealth
)

class UpstoxProvider(MarketDataProvider):
    """
    Upstox Developer API v2 Integration.
    API Docs: https://upstox.com/developer/api-documentation/
    """
    BASE_URL = "https://api.upstox.com/v2"

    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key or settings.UPSTOX_API_KEY
        self.access_token = access_token or os_access_token()

    @property
    def name(self) -> str:
        return "UPSTOX"

    def is_configured(self) -> bool:
        return bool(self.access_token)

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "AI-Investment-Terminal/1.0"
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def check_health(self) -> ProviderHealth:
        if not self.is_configured():
            return ProviderHealth(
                provider_name=self.name,
                is_connected=False,
                is_configured=False,
                latency_ms=0,
                message="Upstox API key / access token not configured. Visit Settings to connect your Upstox account."
            )

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"{self.BASE_URL}/user/profile",
                    headers=self._get_headers()
                )
                latency = int((time.time() - start) * 1000)
                if res.status_code == 200:
                    return ProviderHealth(
                        provider_name=self.name,
                        is_connected=True,
                        is_configured=True,
                        latency_ms=latency,
                        message="Connected to Upstox v2 API"
                    )
                else:
                    return ProviderHealth(
                        provider_name=self.name,
                        is_connected=False,
                        is_configured=True,
                        latency_ms=latency,
                        message=f"Upstox Auth Error: {res.status_code} - {res.text[:100]}"
                    )
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return ProviderHealth(
                provider_name=self.name,
                is_connected=False,
                is_configured=True,
                latency_ms=latency,
                message=f"Connection Error: {str(e)}"
            )

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[QuoteData]:
        quotes = await self.get_quotes([symbol], exchange=exchange)
        return quotes.get(symbol)

    async def get_quotes(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, QuoteData]:
        if not self.is_configured():
            return {}

        instrument_keys = [f"{exchange}_EQ|{s}" for s in symbols]
        url = f"{self.BASE_URL}/market-quote/quotes"
        params = {"instrument_key": ",".join(instrument_keys)}

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=self._get_headers(), params=params)
                if res.status_code != 200:
                    return {}

                data = res.json().get("data", {})
                results = {}
                for key, item in data.items():
                    sym = item.get("symbol", key.split("|")[-1])
                    ltp = Decimal(str(item.get("last_price", 0)))
                    close_prev = Decimal(str(item.get("ohlc", {}).get("close", ltp)))
                    open_p = Decimal(str(item.get("ohlc", {}).get("open", ltp)))
                    high_p = Decimal(str(item.get("ohlc", {}).get("high", ltp)))
                    low_p = Decimal(str(item.get("ohlc", {}).get("low", ltp)))
                    vol = int(item.get("volume", 0))
                    day_change = ltp - close_prev
                    day_change_pct = (day_change / close_prev * 100) if close_prev else Decimal("0.00")

                    results[sym] = QuoteData(
                        symbol=sym,
                        exchange=exchange,
                        ltp=ltp,
                        open=open_p,
                        high=high_p,
                        low=low_p,
                        close_prev=close_prev,
                        volume=vol,
                        day_change=day_change,
                        day_change_pct=day_change_pct,
                        timestamp=datetime.now(timezone.utc),
                        provider=self.name,
                        is_live=True
                    )
                return results
        except Exception:
            return {}

    async def get_historical_candles(
        self,
        symbol: str,
        exchange: str = "NSE",
        timeframe: str = "1d",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[CandleData]:
        if not self.is_configured():
            return []

        interval_map = {"1d": "day", "1m": "1minute", "5m": "5minute", "30m": "30minute"}
        interval = interval_map.get(timeframe, "day")
        inst_key = f"{exchange}_EQ|{symbol}"
        t_date = to_date.strftime("%Y-%m-%d") if to_date else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        f_date = from_date.strftime("%Y-%m-%d") if from_date else (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

        url = f"{self.BASE_URL}/historical-candle/{inst_key}/{interval}/{t_date}/{f_date}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code != 200:
                    return []
                candles_data = res.json().get("data", {}).get("candles", [])
                candles = []
                for c in candles_data:
                    # c format: [timestamp, open, high, low, close, volume, open_interest]
                    ts = datetime.fromisoformat(c[0].replace("Z", "+00:00"))
                    candles.append(CandleData(
                        timestamp=ts,
                        open=Decimal(str(c[1])),
                        high=Decimal(str(c[2])),
                        low=Decimal(str(c[3])),
                        close=Decimal(str(c[4])),
                        volume=int(c[5])
                    ))
                # Return in chronological order (oldest to newest)
                candles.reverse()
                return candles
        except Exception:
            return []

    async def search_instruments(self, query: str) -> List[SearchResult]:
        # Upstox doesn't have a live fuzzy search endpoint; users download the instrument master.
        # Fallback or master file is queried in MarketDataService.
        return []

    async def get_market_indices(self) -> List[QuoteData]:
        index_symbols = ["Nifty 50", "Nifty Bank", "Nifty IT", "INDIA VIX", "BSE SENSEX"]
        inst_keys = [
            "NSE_INDEX|Nifty 50",
            "NSE_INDEX|Nifty Bank",
            "NSE_INDEX|Nifty IT",
            "NSE_INDEX|India VIX",
            "BSE_INDEX|SENSEX"
        ]
        if not self.is_configured():
            return []

        url = f"{self.BASE_URL}/market-quote/quotes"
        params = {"instrument_key": ",".join(inst_keys)}
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=self._get_headers(), params=params)
                if res.status_code != 200:
                    return []
                data = res.json().get("data", {})
                quotes = []
                for key, item in data.items():
                    name = item.get("symbol", key.split("|")[-1])
                    ltp = Decimal(str(item.get("last_price", 0)))
                    close_prev = Decimal(str(item.get("ohlc", {}).get("close", ltp)))
                    open_p = Decimal(str(item.get("ohlc", {}).get("open", ltp)))
                    high_p = Decimal(str(item.get("ohlc", {}).get("high", ltp)))
                    low_p = Decimal(str(item.get("ohlc", {}).get("low", ltp)))
                    day_change = ltp - close_prev
                    day_change_pct = (day_change / close_prev * 100) if close_prev else Decimal("0.00")
                    quotes.append(QuoteData(
                        symbol=name,
                        exchange="NSE",
                        ltp=ltp,
                        open=open_p,
                        high=high_p,
                        low=low_p,
                        close_prev=close_prev,
                        volume=int(item.get("volume", 0)),
                        day_change=day_change,
                        day_change_pct=day_change_pct,
                        timestamp=datetime.now(timezone.utc),
                        provider=self.name,
                        is_live=True
                    ))
                return quotes
        except Exception:
            return []

def os_access_token() -> Optional[str]:
    import os
    return os.getenv("UPSTOX_ACCESS_TOKEN", "")
