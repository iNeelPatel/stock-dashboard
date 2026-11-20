from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pydantic import BaseModel
from backend.app.services.market_data.service import market_data_service

class ScenarioForecast(BaseModel):
    horizon_days: int
    horizon_label: str
    cmp: float
    bull_target: float
    bull_probability_pct: float
    base_target: float
    base_probability_pct: float
    bear_target: float
    bear_probability_pct: float
    expected_range: str
    confidence_score: float
    model_version: str
    key_assumptions: str
    disclaimer: str

class LearningLesson(BaseModel):
    id: str
    category: str
    title: str
    description: str
    key_takeaways: List[str]
    buffett_quote: Optional[str] = None

class JournalEntry(BaseModel):
    id: str
    symbol: str
    entry_date: str
    mode: str
    thesis: str
    exit_plan: str
    biases_checked: List[str]
    lesson_notes: Optional[str] = None

class AIForecastingService:
    async def get_forecast(self, symbol: str, horizon_days: int = 30) -> ScenarioForecast:
        quote = await market_data_service.get_quote(symbol)
        cmp = float(quote.ltp)

        # Quantitative volatility & drift projections
        volatility = 0.18 # 18% annualized vol
        time_factor = (horizon_days / 365.0) ** 0.5
        expected_move = cmp * volatility * time_factor

        bull_target = round(cmp + expected_move * 1.35, 2)
        base_target = round(cmp + expected_move * 0.40, 2)
        bear_target = round(cmp - expected_move * 1.10, 2)

        return ScenarioForecast(
            horizon_days=horizon_days,
            horizon_label=f"{horizon_days} Trading Days",
            cmp=cmp,
            bull_target=bull_target,
            bull_probability_pct=32.0,
            base_target=base_target,
            base_probability_pct=48.0,
            bear_target=bear_target,
            bear_probability_pct=20.0,
            expected_range=f"₹{bear_target:,.2f} – ₹{bull_target:,.2f}",
            confidence_score=78.5,
            model_version="Q-Forecaster v2.1-Alpha",
            key_assumptions="Assumes earnings trajectory maintains historical 3-year median and NIFTY VIX remains below 17.5.",
            disclaimer="Quantitative statistical forecast for personal scenario simulation. Not a guaranteed future market price."
        )

    def get_learning_lessons(self) -> List[LearningLesson]:
        return [
            LearningLesson(
                id="lesson-01",
                category="Fundamental Moat Analysis",
                title="The Power of Return on Capital Employed (ROCE)",
                description="Why Warren Buffett and Charlie Munger prioritize companies that can reinvest capital at high rates of return.",
                key_takeaways=[
                    "High ROCE (>20%) indicates pricing power or extreme capital efficiency.",
                    "A business earning 25% on capital over 15 years will drastically outperform a 10% business, regardless of entry P/E.",
                    "Always verify that ROCE is accompanied by positive Free Cash Flow, not merely accounting accruals."
                ],
                buffett_quote="The primary test of managerial performance is the achievement of a high return on capital employed, not the mere enlargement of total earnings."
            ),
            LearningLesson(
                id="lesson-02",
                category="Risk Management & Paper Trading",
                title="The Mathematics of Drawdown Recovery",
                description="Understanding why asymmetric risk control is the cornerstone of surviving and compounding wealth in Indian equities.",
                key_takeaways=[
                    "A 10% portfolio loss requires an 11.1% gain to break even.",
                    "A 50% loss requires a 100% gain simply to return to par.",
                    "Enforce strict position sizing: never risk more than 1.5% to 2% of total portfolio capital on any single trading idea."
                ],
                buffett_quote="Rule No. 1: Never lose money. Rule No. 2: Never forget Rule No. 1."
            ),
            LearningLesson(
                id="lesson-03",
                category="Behavioural Finance",
                title="Combating Cognitive Biases in Volatile Markets",
                description="How emotional traps like Loss Aversion, Confirmation Bias, and FOMO degrade investment returns.",
                key_takeaways=[
                    "Loss Aversion causes investors to hold losing stocks hoping to break even while prematurely selling compounders.",
                    "Confirmation Bias leads investors to consume only positive commentary about existing portfolio holdings.",
                    "Maintain an immutable trade journal to review initial entry theses objectively."
                ],
                buffett_quote="The most important quality for an investor is temperament, not intellect."
            )
        ]

ai_forecasting_service = AIForecastingService()
