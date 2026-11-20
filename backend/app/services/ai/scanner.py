from typing import List, Dict, Any, Optional
from decimal import Decimal
from pydantic import BaseModel
from backend.app.services.market_data.service import market_data_service, INDIAN_STOCKS_MASTER
from backend.app.services.ai.agents import multi_agent_engine

class ScannerCandidate(BaseModel):
    symbol: str
    name: str
    sector: str
    exchange: str
    ltp: float
    day_change_pct: float
    opportunity_score: float
    fundamental_score: float
    technical_score: float
    mode: str
    preset_matched: str
    entry_zone: str
    target_price: float
    stop_loss: float
    catalyst_summary: str
    reason_to_buy: str
    reasons_to_avoid: str

class AIScannerService:
    PRESETS = [
        "Quality Businesses (Buffett-Style)",
        "Undervalued Opportunities",
        "Consistent Profit Compounders",
        "Low-Debt Strong Balance Sheet",
        "High-ROCE Elite Franchise",
        "Dividend Aristocrats",
        "Growth Opportunities",
        "Technical Breakouts",
        "Momentum Setups",
        "Unusual Volume Anomalies",
        "Positive News Catalysts",
        "Turnaround Candidates",
        "Approaching Value Zone",
        "Negative News Warnings (Avoid)"
    ]

    async def run_scan(
        self,
        mode: str = "INVESTMENT",
        preset: str = "Quality Businesses (Buffett-Style)",
        sector_filter: Optional[str] = None
    ) -> List[ScannerCandidate]:
        results: List[ScannerCandidate] = []
        mode = mode.upper()

        for stock in INDIAN_STOCKS_MASTER:
            if sector_filter and sector_filter.lower() not in stock.get("sector", "").lower():
                continue

            sym = stock["symbol"]
            quote = await market_data_service.get_quote(sym)
            rec = await multi_agent_engine.synthesize_strategy(sym, mode=mode)

            pe = float(stock.get("pe", 25.0))
            roce = float(stock.get("roce", 15.0))
            debt_eq = float(stock.get("debt_equity", 0.5))

            # Preset criteria evaluation
            matches = False
            if preset == "Quality Businesses (Buffett-Style)":
                matches = (roce >= 18.0 and debt_eq <= 0.6)
            elif preset == "Undervalued Opportunities":
                matches = (pe <= 22.0 and roce >= 14.0)
            elif preset == "Low-Debt Strong Balance Sheet":
                matches = (debt_eq <= 0.15)
            elif preset == "High-ROCE Elite Franchise":
                matches = (roce >= 25.0)
            elif preset == "Technical Breakouts":
                matches = (rec.technical_score >= 65.0)
            elif preset == "Momentum Setups":
                matches = (rec.technical_score >= 60.0 and float(quote.day_change_pct) >= 0.0)
            else:
                # Default general match
                matches = (rec.composite_score >= 60.0)

            if matches:
                entry_zone = f"₹{rec.entry_range_low:,.2f} – ₹{rec.entry_range_high:,.2f}"
                avoid_reason = "Avoid if debt rises or quarterly margins compress below 12%." if mode == "INVESTMENT" else f"Avoid if price closes below stop-loss ₹{rec.stop_loss:,.2f}."
                
                results.append(ScannerCandidate(
                    symbol=sym,
                    name=stock["name"],
                    sector=stock.get("sector", "Diversified"),
                    exchange="NSE",
                    ltp=float(quote.ltp),
                    day_change_pct=float(quote.day_change_pct),
                    opportunity_score=rec.composite_score,
                    fundamental_score=rec.fundamental_score,
                    technical_score=rec.technical_score,
                    mode=mode,
                    preset_matched=preset,
                    entry_zone=entry_zone,
                    target_price=rec.target_1,
                    stop_loss=rec.stop_loss,
                    catalyst_summary=rec.catalysts,
                    reason_to_buy=rec.investment_thesis,
                    reasons_to_avoid=avoid_reason
                ))

        # Sort descending by opportunity score
        results.sort(key=lambda x: x.opportunity_score, reverse=True)
        return results

ai_scanner_service = AIScannerService()
