from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid

class AlertEventItem(BaseModel):
    id: str
    symbol: str
    category: str # "PRICE", "TECHNICAL", "FUNDAMENTAL", "NEWS", "PORTFOLIO_RISK"
    title: str
    current_price: float
    trigger_condition: str
    ai_explanation: str
    potential_impact: str # "HIGH", "MEDIUM", "LOW"
    event_timestamp: str
    is_read: bool = False

class AlertRuleItem(BaseModel):
    id: str
    symbol: Optional[str]
    category: str
    condition_type: str
    threshold_value: float
    is_active: bool

class AlertEngineService:
    def __init__(self):
        self._rules: List[AlertRuleItem] = [
            AlertRuleItem(id="rule-1", symbol="RELIANCE", category="PRICE", condition_type="LESS_THAN", threshold_value=2450.0, is_active=True),
            AlertRuleItem(id="rule-2", symbol="TCS", category="PRICE", condition_type="GREATER_THAN", threshold_value=4200.0, is_active=True),
            AlertRuleItem(id="rule-3", symbol=None, category="PORTFOLIO_RISK", condition_type="DRAWDOWN_LIMIT", threshold_value=3.0, is_active=True),
        ]

        self._events: List[AlertEventItem] = [
            AlertEventItem(
                id="evt-001",
                symbol="RELIANCE",
                category="PRICE",
                title="Approaching Long-Term Value Entry Zone",
                current_price=2485.50,
                trigger_condition="Price within 1.5% of value accumulation range (₹2,450)",
                ai_explanation="Reliance is testing strong multi-month horizontal support and 200 EMA confluence. Valuation multiple is in the 15th percentile of 3-year range.",
                potential_impact="HIGH",
                event_timestamp="2026-11-20T10:15:00Z",
                is_read=False
            ),
            AlertEventItem(
                id="evt-002",
                symbol="HDFCBANK",
                category="FUNDAMENTAL",
                title="Q2 Earnings Inflection & Margin Expansion",
                current_price=1650.00,
                trigger_condition="Net Interest Margin expanded +18 bps QoQ",
                ai_explanation="Core deposits grew 15.2% YoY outperforming system credit growth. Gross NPA contracted to 1.24% demonstrating solid credit discipline.",
                potential_impact="HIGH",
                event_timestamp="2026-11-19T16:30:00Z",
                is_read=False
            ),
            AlertEventItem(
                id="evt-003",
                symbol="TATAMOTORS",
                category="TECHNICAL",
                title="Bullish Symmetrical Triangle Breakout",
                current_price=980.00,
                trigger_condition="Closed above resistance ₹965 with 2.4x 20-day average volume",
                ai_explanation="Momentum indicators confirm institutional absorption with RSI at 64.2. Next tactical target projected at ₹1,040.",
                potential_impact="MEDIUM",
                event_timestamp="2026-11-19T11:45:00Z",
                is_read=True
            ),
            AlertEventItem(
                id="evt-004",
                symbol="PORTFOLIO",
                category="PORTFOLIO_RISK",
                title="Sector Concentration Caution",
                current_price=0.0,
                trigger_condition="Information Technology sector allocation reached 26.5%",
                ai_explanation="Portfolio concentration in IT equities is approaching the 30% prudential guardrail. Consider diversifying upcoming allocations into Capital Goods or FMCG.",
                potential_impact="MEDIUM",
                event_timestamp="2026-11-18T15:35:00Z",
                is_read=True
            )
        ]

    def get_alerts(self, unread_only: bool = False) -> List[AlertEventItem]:
        if unread_only:
            return [e for e in self._events if not e.is_read]
        return self._events

    def mark_as_read(self, alert_id: str) -> bool:
        for e in self._events:
            if e.id == alert_id:
                e.is_read = True
                return True
        return False

    def add_rule(self, symbol: Optional[str], category: str, condition_type: str, threshold: float) -> AlertRuleItem:
        rule = AlertRuleItem(
            id=str(uuid.uuid4())[:8],
            symbol=symbol.upper() if symbol else None,
            category=category.upper(),
            condition_type=condition_type.upper(),
            threshold_value=threshold,
            is_active=True
        )
        self._rules.append(rule)
        return rule

    def get_rules(self) -> List[AlertRuleItem]:
        return self._rules

alert_engine_service = AlertEngineService()
