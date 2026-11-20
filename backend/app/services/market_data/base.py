from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel

class QuoteData(BaseModel):
    symbol: str
    exchange: str
    ltp: Decimal
    open: Decimal
    high: Decimal
    low: Decimal
    close_prev: Decimal
    volume: int
    day_change: Decimal
    day_change_pct: Decimal
    timestamp: datetime
    provider: str
    is_live: bool = True

class CandleData(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

class SearchResult(BaseModel):
    symbol: str
    exchange: str
    name: str
    isin: Optional[str] = None
    instrument_type: str = "EQUITY"
    sector: Optional[str] = None

class ProviderHealth(BaseModel):
    provider_name: str
    is_connected: bool
    is_configured: bool
    latency_ms: int
    message: str

class MarketDataProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider, e.g. UPSTOX, DHAN, KITE"""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the provider has necessary API credentials configured."""
        pass

    @abstractmethod
    async def check_health(self) -> ProviderHealth:
        """Check provider connectivity, latency and health."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Optional[QuoteData]:
        """Fetch live or recent market quote for a given instrument."""
        pass

    @abstractmethod
    async def get_quotes(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, QuoteData]:
        """Fetch multiple quotes concurrently."""
        pass

    @abstractmethod
    async def get_historical_candles(
        self,
        symbol: str,
        exchange: str = "NSE",
        timeframe: str = "1d",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[CandleData]:
        """Fetch historical OHLCV candle series."""
        pass

    @abstractmethod
    async def search_instruments(self, query: str) -> List[SearchResult]:
        """Search instruments by symbol or company name."""
        pass

    @abstractmethod
    async def get_market_indices(self) -> List[QuoteData]:
        """Fetch primary indices (NIFTY 50, SENSEX, NIFTY BANK, NIFTY IT, etc.)."""
        pass
