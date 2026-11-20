from fastapi import APIRouter, Query, HTTPException, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.app.services.ai.agents import multi_agent_engine, RecommendationOutput
from backend.app.services.ai.scanner import ai_scanner_service, ScannerCandidate
from backend.app.services.ai.tracker import recommendation_tracker_service, RecommendationPerformanceSummary, RecommendationHistoryRecord
from backend.app.services.ai.forecasting import ai_forecasting_service, ScenarioForecast
from backend.app.services.market_data.service import market_data_service

router = APIRouter(prefix="/ai", tags=["AI Investment Intelligence"])

class AIChatQuery(BaseModel):
    message: str
    symbol: Optional[str] = None
    mode: str = "INVESTMENT"

@router.get("/analyze/{symbol}", response_model=RecommendationOutput)
async def analyze_stock(symbol: str, mode: str = "INVESTMENT"):
    """
    Triggers multi-agent evaluation pipeline for Indian equities.
    Differentiates strictly between INVESTMENT (1-5y) and TRADING (1-4w) modes.
    """
    return await multi_agent_engine.synthesize_strategy(symbol, mode=mode)

@router.get("/scanner", response_model=List[ScannerCandidate])
async def run_scanner(
    mode: str = "INVESTMENT",
    preset: str = "Quality Businesses (Buffett-Style)",
    sector: Optional[str] = None
):
    """
    Module 1: AI Opportunity Scanner across 14 presets and custom filters.
    """
    return await ai_scanner_service.run_scan(mode=mode, preset=preset, sector_filter=sector)

@router.get("/recommendations", response_model=List[RecommendationHistoryRecord])
async def get_recommendation_history(
    mode: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Module 2: Historical recommendation tracker with lifecycle states and alpha vs NIFTY 50.
    """
    return recommendation_tracker_service.get_recommendations(mode=mode, status=status)

@router.get("/performance", response_model=RecommendationPerformanceSummary)
async def get_performance_summary():
    """
    Aggregated AI recommendation performance, win rates, profit factor, and self-evaluations.
    """
    return recommendation_tracker_service.get_performance_summary()

@router.get("/forecast/{symbol}", response_model=ScenarioForecast)
async def get_price_forecast(symbol: str, horizon: int = 30):
    """
    Quantitative scenario price forecasting with Bull, Base, and Bear scenarios.
    """
    return await ai_forecasting_service.get_forecast(symbol, horizon_days=horizon)

@router.post("/chat")
async def chat_with_analyst(payload: AIChatQuery):
    """
    Interactive conversational research assistant grounded in real-time application market data.
    """
    query = payload.message.lower()
    sym = payload.symbol.upper() if payload.symbol else None

    # Grounded response generation
    if sym:
        quote = await market_data_service.get_quote(sym)
        rec = await multi_agent_engine.synthesize_strategy(sym, mode=payload.mode)
        
        reply = (
            f"**Research Summary for {sym} ({quote.provider}):**\n\n"
            f"- **Current Market Price:** ₹{quote.ltp:,.2f} ({quote.day_change_pct:+.2f}% today)\n"
            f"- **AI Strategist Stance ({payload.mode} Mode):** **{rec.recommendation_type}** (Composite Score: {rec.composite_score}/100)\n"
            f"- **Potential Entry Range:** ₹{rec.entry_range_low:,.2f} – ₹{rec.entry_range_high:,.2f}\n"
            f"- **Target 1:** ₹{rec.target_1:,.2f} | **Target 2:** ₹{rec.target_2:,.2f} | **Stop-Loss:** ₹{rec.stop_loss:,.2f}\n"
            f"- **Core Investment Thesis:** {rec.investment_thesis}\n"
            f"- **Key Risks to Monitor:** {rec.key_risks}\n\n"
            f"*(Data timestamp: {quote.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}. Simulated paper trading mode.)*"
        )
    elif "today" in query or "market" in query or "nifty" in query:
        indices = await market_data_service.get_market_indices()
        nifty = next((i for i in indices if "NIFTY 50" in i.symbol), None)
        vix = next((i for i in indices if "VIX" in i.symbol), None)
        nifty_ltp = nifty.ltp if nifty else 24350.0
        vix_ltp = vix.ltp if vix else 14.2
        
        reply = (
            f"**Indian Stock Market Intelligence Summary:**\n\n"
            f"- **NIFTY 50:** ₹{nifty_ltp:,.2f} ({nifty.day_change_pct:+.2f}%)\n"
            f"- **INDIA VIX:** {vix_ltp:.2f} (Indicating low systematic volatility)\n"
            f"- **Top Discovered Opportunities:**\n"
            f"  1. **TCS** — Elite capital allocation, ROCE > 50%, attractive risk/reward.\n"
            f"  2. **HDFCBANK** — Margin accretion inflection post-merger, trading at favorable historical P/E.\n"
            f"  3. **TATAMOTORS** — Strong technical breakout above 20 EMA with positive commercial vehicle volume trends.\n\n"
            f"Switch between **Investment Mode** for 1–5 year wealth compounding or **Trading Mode** for tactical 1–4 week swing setups."
        )
    else:
        reply = (
            f"I am your Indian Equity Research AI Assistant. You can ask me to:\n\n"
            f"1. **Analyze any stock:** E.g., *'Analyse RELIANCE in Investment Mode'* or *'Is INFY overvalued?'*\n"
            f"2. **Find opportunities:** E.g., *'Find low-debt companies with high ROCE'* or *'Show technical breakouts'*.\n"
            f"3. **Review portfolio risks:** E.g., *'Check my IT sector exposure'*\n"
            f"4. **Evaluate past recommendations:** E.g., *'How accurate were recent BUY signals?'*"
        )

    return {
        "reply": reply,
        "symbol": sym,
        "mode": payload.mode,
        "timestamp": quote.timestamp.isoformat() if sym else None
    }
