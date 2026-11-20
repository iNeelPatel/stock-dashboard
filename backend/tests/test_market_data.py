import pytest
from decimal import Decimal
from backend.app.services.market_data.service import market_data_service

@pytest.mark.anyio
async def test_search_instruments():
    results = await market_data_service.search_instruments("reliance")
    assert len(results) > 0
    assert results[0].symbol == "RELIANCE"
    assert results[0].exchange == "NSE"

@pytest.mark.anyio
async def test_get_quote():
    quote = await market_data_service.get_quote("TCS")
    assert quote.symbol == "TCS"
    assert quote.ltp > Decimal("3000.00")
    assert quote.exchange == "NSE"
    assert quote.timestamp is not None

@pytest.mark.anyio
async def test_get_market_indices():
    indices = await market_data_service.get_market_indices()
    assert len(indices) >= 5
    symbols = [idx.symbol for idx in indices]
    assert "NIFTY 50" in symbols
    assert "SENSEX" in symbols

@pytest.mark.anyio
async def test_historical_candles_and_technicals():
    candles = await market_data_service.get_historical_candles("HDFCBANK", days=100)
    assert len(candles) >= 50
    # Test indicators calculation
    indicators = market_data_service.calculate_technical_indicators(candles)
    assert "sma_20" in indicators
    assert "rsi_14" in indicators
    assert "macd_line" in indicators
    assert "bollinger_upper" in indicators
    assert indicators["rsi_14"] is not None
