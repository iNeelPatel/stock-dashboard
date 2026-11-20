from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from backend.app.services.market_data.service import market_data_service
from backend.app.services.market_data.base import QuoteData, CandleData, SearchResult, ProviderHealth

router = APIRouter(prefix="/market", tags=["Market Data"])

@router.get("/indices", response_model=List[QuoteData])
async def get_indices():
    """Fetch live or cached quotes for primary Indian benchmark indices."""
    return await market_data_service.get_market_indices()

@router.get("/search", response_model=List[SearchResult])
async def search_stocks(q: str = Query(..., min_length=1, description="Stock symbol or company name")):
    """Search Indian equities across NSE and BSE."""
    return await market_data_service.search_instruments(q)

@router.get("/quote/{symbol}", response_model=QuoteData)
async def get_stock_quote(symbol: str, exchange: str = "NSE"):
    """Fetch real-time quote with timestamp and provider source."""
    return await market_data_service.get_quote(symbol, exchange)

@router.get("/candles/{symbol}", response_model=List[CandleData])
async def get_candles(symbol: str, timeframe: str = "1d", days: int = 180):
    """Fetch historical OHLCV candle series."""
    return await market_data_service.get_historical_candles(symbol, timeframe=timeframe, days=days)

@router.get("/provider-status", response_model=ProviderHealth)
async def get_provider_status():
    """Check connectivity, latency and health of the active market data provider."""
    return await market_data_service.get_provider_health()
