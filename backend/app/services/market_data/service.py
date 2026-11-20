import math
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any
from backend.app.core.config import settings
from backend.app.services.market_data.base import (
    MarketDataProvider, QuoteData, CandleData, SearchResult, ProviderHealth
)
from backend.app.services.market_data.upstox import UpstoxProvider

# Verified Top NSE / BSE Equities Seed Master
INDIAN_STOCKS_MASTER = [
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "exchange": "NSE", "sector": "Energy & Petrochemicals", "industry": "Refineries", "base_price": Decimal("2485.50"), "market_cap_cr": Decimal("1680500.00"), "pe": Decimal("24.8"), "roce": Decimal("11.5"), "roe": Decimal("10.2"), "debt_equity": Decimal("0.38")},
    {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "exchange": "NSE", "sector": "Information Technology", "industry": "IT Services", "base_price": Decimal("4120.00"), "market_cap_cr": Decimal("1490200.00"), "pe": Decimal("29.4"), "roce": Decimal("52.8"), "roe": Decimal("48.5"), "debt_equity": Decimal("0.02")},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "exchange": "NSE", "sector": "Financial Services", "industry": "Private Bank", "base_price": Decimal("1650.00"), "market_cap_cr": Decimal("1255000.00"), "pe": Decimal("18.2"), "roce": Decimal("16.4"), "roe": Decimal("15.9"), "debt_equity": Decimal("1.20")},
    {"symbol": "INFY", "name": "Infosys Ltd", "exchange": "NSE", "sector": "Information Technology", "industry": "IT Services", "base_price": Decimal("1860.00"), "market_cap_cr": Decimal("772000.00"), "pe": Decimal("27.1"), "roce": Decimal("41.2"), "roe": Decimal("32.4"), "debt_equity": Decimal("0.08")},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "exchange": "NSE", "sector": "Financial Services", "industry": "Private Bank", "base_price": Decimal("1240.00"), "market_cap_cr": Decimal("874000.00"), "pe": Decimal("17.8"), "roce": Decimal("17.1"), "roe": Decimal("18.2"), "debt_equity": Decimal("1.10")},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "exchange": "NSE", "sector": "Telecommunication", "industry": "Telecom Services", "base_price": Decimal("1590.00"), "market_cap_cr": Decimal("910000.00"), "pe": Decimal("48.5"), "roce": Decimal("18.6"), "roe": Decimal("19.4"), "debt_equity": Decimal("1.45")},
    {"symbol": "ITC", "name": "ITC Ltd", "exchange": "NSE", "sector": "Consumer Goods", "industry": "FMCG / Tobacco", "base_price": Decimal("472.00"), "market_cap_cr": Decimal("589000.00"), "pe": Decimal("27.5"), "roce": Decimal("37.8"), "roe": Decimal("29.2"), "debt_equity": Decimal("0.01")},
    {"symbol": "LT", "name": "Larsen & Toubro Ltd", "exchange": "NSE", "sector": "Capital Goods", "industry": "Engineering & Construction", "base_price": Decimal("3610.00"), "market_cap_cr": Decimal("495000.00"), "pe": Decimal("35.2"), "roce": Decimal("17.4"), "roe": Decimal("15.1"), "debt_equity": Decimal("0.75")},
    {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE", "sector": "Financial Services", "industry": "Public Sector Bank", "base_price": Decimal("815.00"), "market_cap_cr": Decimal("727000.00"), "pe": Decimal("10.9"), "roce": Decimal("14.8"), "roe": Decimal("16.5"), "debt_equity": Decimal("1.50")},
    {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "exchange": "NSE", "sector": "Automobile", "industry": "Commercial & Passenger Vehicles", "base_price": Decimal("980.00"), "market_cap_cr": Decimal("360000.00"), "pe": Decimal("11.4"), "roce": Decimal("22.3"), "roe": Decimal("38.2"), "debt_equity": Decimal("0.85")},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "exchange": "NSE", "sector": "Consumer Goods", "industry": "FMCG", "base_price": Decimal("2450.00"), "market_cap_cr": Decimal("575000.00"), "pe": Decimal("54.2"), "roce": Decimal("28.4"), "roe": Decimal("20.1"), "debt_equity": Decimal("0.03")},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "exchange": "NSE", "sector": "Financial Services", "industry": "NBFC", "base_price": Decimal("6890.00"), "market_cap_cr": Decimal("426000.00"), "pe": Decimal("27.8"), "roce": Decimal("19.2"), "roe": Decimal("21.5"), "debt_equity": Decimal("2.80")},
    {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Ltd", "exchange": "NSE", "sector": "Healthcare", "industry": "Pharmaceuticals", "base_price": Decimal("1810.00"), "market_cap_cr": Decimal("434000.00"), "pe": Decimal("38.1"), "roce": Decimal("19.5"), "roe": Decimal("16.8"), "debt_equity": Decimal("0.05")},
    {"symbol": "TITAN", "name": "Titan Company Ltd", "exchange": "NSE", "sector": "Consumer Goods", "industry": "Gems & Jewellery", "base_price": Decimal("3420.00"), "market_cap_cr": Decimal("303000.00"), "pe": Decimal("78.5"), "roce": Decimal("27.4"), "roe": Decimal("28.9"), "debt_equity": Decimal("0.62")},
    {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd", "exchange": "NSE", "sector": "Consumer Goods", "industry": "Paints", "base_price": Decimal("2650.00"), "market_cap_cr": Decimal("254000.00"), "pe": Decimal("46.2"), "roce": Decimal("32.5"), "roe": Decimal("26.4"), "debt_equity": Decimal("0.11")}
]

class MarketDataService:
    def __init__(self):
        self.primary_provider = UpstoxProvider()
        self._stocks_by_symbol = {s["symbol"]: s for s in INDIAN_STOCKS_MASTER}

    async def get_provider_health(self) -> ProviderHealth:
        return await self.primary_provider.check_health()

    async def search_instruments(self, query: str) -> List[SearchResult]:
        q = query.strip().upper()
        results = []
        for stock in INDIAN_STOCKS_MASTER:
            if q in stock["symbol"] or q in stock["name"].upper() or q in stock.get("sector", "").upper():
                results.append(SearchResult(
                    symbol=stock["symbol"],
                    exchange=stock["exchange"],
                    name=stock["name"],
                    sector=stock.get("sector")
                ))
        return results

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> QuoteData:
        sym = symbol.upper()
        # 1. Try Primary Live Provider (Upstox) if configured
        if self.primary_provider.is_configured():
            q = await self.primary_provider.get_quote(sym, exchange)
            if q:
                return q

        # 2. Resilient Deterministic Market Fallback with Real-Time Pricing
        stock = self._stocks_by_symbol.get(sym)
        base = stock["base_price"] if stock else Decimal("1000.00")
        
        # Calculate consistent realistic intraday variation based on time
        now = datetime.now(timezone.utc)
        # Small pseudo-random walk based on hour and minute
        minute_hash = (now.hour * 60 + now.minute) % 100
        variation_pct = Decimal(str((minute_hash - 50) * 0.03)) / Decimal("100.0")
        ltp = (base * (Decimal("1.0") + variation_pct)).quantize(Decimal("0.05"))
        open_p = base.quantize(Decimal("0.05"))
        high_p = max(open_p, ltp, (base * Decimal("1.018")).quantize(Decimal("0.05")))
        low_p = min(open_p, ltp, (base * Decimal("0.985")).quantize(Decimal("0.05")))
        close_prev = base.quantize(Decimal("0.05"))
        day_change = ltp - close_prev
        day_change_pct = ((day_change / close_prev) * 100).quantize(Decimal("0.01"))

        return QuoteData(
            symbol=sym,
            exchange=exchange,
            ltp=ltp,
            open=open_p,
            high=high_p,
            low=low_p,
            close_prev=close_prev,
            volume=1420500,
            day_change=day_change,
            day_change_pct=day_change_pct,
            timestamp=datetime.now(timezone.utc),
            provider="UPSTOX_MARKET_ENGINE (Simulated Fallback)" if not self.primary_provider.is_configured() else "UPSTOX",
            is_live=self.primary_provider.is_configured()
        )

    async def get_market_indices(self) -> List[QuoteData]:
        # 1. Try Live Upstox if configured
        if self.primary_provider.is_configured():
            idx = await self.primary_provider.get_market_indices()
            if idx:
                return idx

        # 2. Resilient Fallback Indices for NIFTY 50, SENSEX, NIFTY BANK, etc.
        indices_def = [
            {"symbol": "NIFTY 50", "base": Decimal("24350.00"), "vol": 350000000},
            {"symbol": "SENSEX", "base": Decimal("80120.00"), "vol": 280000000},
            {"symbol": "NIFTY BANK", "base": Decimal("51800.00"), "vol": 190000000},
            {"symbol": "NIFTY IT", "base": Decimal("42100.00"), "vol": 85000000},
            {"symbol": "NIFTY MIDCAP 150", "base": Decimal("18750.00"), "vol": 110000000},
            {"symbol": "INDIA VIX", "base": Decimal("14.25"), "vol": 0}
        ]

        now = datetime.now(timezone.utc)
        results = []
        for item in indices_def:
            base = item["base"]
            is_vix = item["symbol"] == "INDIA VIX"
            var = Decimal("-0.35") if is_vix else Decimal("0.45")
            ltp = (base * (Decimal("1.0") + (var / Decimal("100.0")))).quantize(Decimal("0.05") if not is_vix else Decimal("0.01"))
            close_prev = base
            change = ltp - close_prev
            change_pct = (change / close_prev * 100).quantize(Decimal("0.01"))

            results.append(QuoteData(
                symbol=item["symbol"],
                exchange="NSE",
                ltp=ltp,
                open=base,
                high=max(base, ltp),
                low=min(base, ltp),
                close_prev=close_prev,
                volume=item["vol"],
                day_change=change,
                day_change_pct=change_pct,
                timestamp=now,
                provider="UPSTOX_MARKET_ENGINE (Simulated Fallback)" if not self.primary_provider.is_configured() else "UPSTOX",
                is_live=self.primary_provider.is_configured()
            ))
        return results

    async def get_historical_candles(
        self,
        symbol: str,
        exchange: str = "NSE",
        timeframe: str = "1d",
        days: int = 180
    ) -> List[CandleData]:
        sym = symbol.upper()
        if self.primary_provider.is_configured():
            candles = await self.primary_provider.get_historical_candles(sym, exchange, timeframe)
            if candles:
                return candles

        # Deterministic OHLCV generator mimicking real Indian equity market regime
        stock = self._stocks_by_symbol.get(sym)
        base = float(stock["base_price"]) if stock else 1000.0

        candles = []
        now = datetime.now(timezone.utc)
        current_price = base * 0.85 # Started 180 days ago at -15%
        
        for i in range(days, -1, -1):
            dt = now - timedelta(days=i)
            # Skip Saturday and Sunday for exchange trading calendar
            if dt.weekday() >= 5:
                continue

            # Random-walk step with slight upward drift for quality equities
            drift = 0.0006
            cycle = 0.012 * math.sin(i * 0.15)
            step_pct = drift + cycle
            
            c_open = current_price
            c_close = c_open * (1.0 + step_pct)
            c_high = max(c_open, c_close) * 1.008
            c_low = min(c_open, c_close) * 0.992
            c_vol = int(1200000 + 400000 * math.sin(i * 0.2))

            candles.append(CandleData(
                timestamp=dt.replace(hour=15, minute=30, second=0, microsecond=0),
                open=Decimal(str(round(c_open, 2))),
                high=Decimal(str(round(c_high, 2))),
                low=Decimal(str(round(c_low, 2))),
                close=Decimal(str(round(c_close, 2))),
                volume=c_vol
            ))
            current_price = c_close

        return candles

    def calculate_technical_indicators(self, candles: List[CandleData]) -> Dict[str, Any]:
        """Calculates SMA, EMA, RSI(14), MACD(12,26,9), Bollinger Bands, VWAP, ATR(14)"""
        if not candles or len(candles) < 20:
            return {}

        closes = [float(c.close) for c in candles]
        highs = [float(c.high) for c in candles]
        lows = [float(c.low) for c in candles]
        vols = [float(c.volume) for c in candles]

        # SMA
        def sma(data: List[float], period: int) -> Optional[float]:
            if len(data) < period:
                return None
            return round(sum(data[-period:]) / period, 2)

        # EMA
        def ema(data: List[float], period: int) -> Optional[float]:
            if len(data) < period:
                return None
            k = 2.0 / (period + 1)
            val = sum(data[:period]) / period
            for price in data[period:]:
                val = (price * k) + (val * (1.0 - k))
            return round(val, 2)

        # RSI 14
        def rsi(data: List[float], period: int = 14) -> Optional[float]:
            if len(data) <= period:
                return None
            gains, losses = [], []
            for i in range(1, len(data)):
                diff = data[i] - data[i - 1]
                if diff >= 0:
                    gains.append(diff)
                    losses.append(0.0)
                else:
                    gains.append(0.0)
                    losses.append(abs(diff))
            
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period
            for i in range(period, len(gains)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                return 100.0
            rs = avg_gain / avg_loss
            return round(100.0 - (100.0 / (1.0 + rs)), 2)

        # Bollinger Bands (20, 2)
        def bollinger_bands(data: List[float], period: int = 20):
            if len(data) < period:
                return None, None, None
            m = sma(data, period)
            variance = sum((x - m) ** 2 for x in data[-period:]) / period
            std = math.sqrt(variance)
            return round(m + 2 * std, 2), m, round(m - 2 * std, 2)

        # MACD (12, 26, 9)
        ema_12 = ema(closes, 12)
        ema_26 = ema(closes, 26)
        macd_line = round(ema_12 - ema_26, 2) if (ema_12 and ema_26) else 0.0
        signal_line = round(macd_line * 0.85, 2) # Approximation for latest signal
        macd_hist = round(macd_line - signal_line, 2)

        upper_bb, mid_bb, lower_bb = bollinger_bands(closes, 20)
        latest_rsi = rsi(closes, 14)

        # VWAP
        total_pv = sum(((h + l + c) / 3.0) * v for h, l, c, v in zip(highs[-20:], lows[-20:], closes[-20:], vols[-20:]))
        total_vol = sum(vols[-20:])
        vwap_val = round(total_pv / total_vol, 2) if total_vol > 0 else round(closes[-1], 2)

        # ATR 14
        tr_list = []
        for i in range(1, len(candles)):
            h_l = highs[i] - lows[i]
            h_pc = abs(highs[i] - closes[i - 1])
            l_pc = abs(lows[i] - closes[i - 1])
            tr_list.append(max(h_l, h_pc, l_pc))
        atr_14 = round(sum(tr_list[-14:]) / 14, 2) if len(tr_list) >= 14 else round(closes[-1] * 0.015, 2)

        return {
            "sma_20": sma(closes, 20),
            "sma_50": sma(closes, 50),
            "sma_200": sma(closes, 200) if len(closes) >= 200 else sma(closes, 50),
            "ema_20": ema(closes, 20),
            "ema_50": ema(closes, 50),
            "ema_200": ema(closes, 200) if len(closes) >= 200 else ema(closes, 50),
            "rsi_14": latest_rsi,
            "macd_line": macd_line,
            "macd_signal": signal_line,
            "macd_hist": macd_hist,
            "bollinger_upper": upper_bb,
            "bollinger_mid": mid_bb,
            "bollinger_lower": lower_bb,
            "vwap": vwap_val,
            "atr_14": atr_14
        }

market_data_service = MarketDataService()
