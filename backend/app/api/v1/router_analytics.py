from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from backend.app.core.database import get_db
from backend.app.services.analytics.service import analytics_service
from backend.app.services.trading.engine import paper_trading_engine
from backend.app.api.v1.router_trading import DEFAULT_USER_ID, ensure_demo_user

router = APIRouter(prefix="/analytics", tags=["Portfolio Analytics & Benchmarks"])

@router.get("/heatmap")
async def get_heatmap(
    mode: str = "INVESTMENT",
    db: AsyncSession = Depends(get_db)
):
    """
    Mandatory Feature: GitHub-style daily calendar heatmap for portfolio P&L.
    Returns daily realized, unrealized, total P&L and key metrics.
    """
    await ensure_demo_user(db)
    portfolio = await paper_trading_engine.get_or_create_default_portfolio(db, DEFAULT_USER_ID, mode=mode.upper())
    return await analytics_service.get_calendar_heatmap(db, portfolio.id)

@router.get("/benchmarks")
async def get_benchmark_comparison(
    mode: str = "INVESTMENT",
    period_days: int = 180,
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive benchmarking against NIFTY 50 Total Return Index (TRI).
    Answers: 'Am I actually investing better than simply holding the NIFTY 50?'
    """
    await ensure_demo_user(db)
    portfolio = await paper_trading_engine.get_or_create_default_portfolio(db, DEFAULT_USER_ID, mode=mode.upper())
    return await analytics_service.get_benchmark_comparison(db, portfolio.id, period_days=period_days)
