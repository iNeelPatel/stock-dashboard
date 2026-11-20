from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from decimal import Decimal
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.core.tax_calculator import calculate_charges, ChargeBreakdown
from backend.app.services.trading.engine import paper_trading_engine, OrderPlacementRequest
from backend.app.models.entities import User, Portfolio

router = APIRouter(prefix="/trading", tags=["Paper Trading & Wallet"])

# Simulated default demo user ID for zero-friction setup
DEFAULT_USER_ID = "usr-demo-investor-001"

async def ensure_demo_user(db: AsyncSession) -> User:
    user = await db.get(User, DEFAULT_USER_ID)
    if not user:
        user = User(
            id=DEFAULT_USER_ID,
            email="demo.investor@ai-terminal.in",
            hashed_password="demo_password_hash",
            full_name="Personal Investor (Paper Account)"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

class OrderCreatePayload(BaseModel):
    symbol: str
    direction: str # "BUY" or "SELL"
    quantity: int
    order_type: str = "MARKET" # "MARKET", "LIMIT", "STOP_LOSS"
    mode: str = "INVESTMENT" # "INVESTMENT" or "TRADING"
    limit_price: Optional[float] = None
    trigger_price: Optional[float] = None

class ChargePreviewQuery(BaseModel):
    symbol: str
    direction: str
    quantity: int
    price: float
    is_intraday: bool = False

@router.get("/summary")
async def get_trading_summary(
    mode: str = "INVESTMENT",
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full portfolio summary, wallet balance, active holdings, and P&L."""
    await ensure_demo_user(db)
    portfolio = await paper_trading_engine.get_or_create_default_portfolio(db, DEFAULT_USER_ID, mode=mode.upper())
    return await paper_trading_engine.get_portfolio_summary(db, portfolio.id)

@router.post("/orders")
async def place_paper_order(
    payload: OrderCreatePayload,
    db: AsyncSession = Depends(get_db)
):
    """Submits and simulates order execution with Indian statutory taxes and cash deductions."""
    await ensure_demo_user(db)
    portfolio = await paper_trading_engine.get_or_create_default_portfolio(db, DEFAULT_USER_ID, mode=payload.mode.upper())
    
    req = OrderPlacementRequest(
        symbol=payload.symbol,
        direction=payload.direction,
        quantity=payload.quantity,
        order_type=payload.order_type,
        mode=payload.mode,
        limit_price=Decimal(str(payload.limit_price)) if payload.limit_price else None,
        trigger_price=Decimal(str(payload.trigger_price)) if payload.trigger_price else None
    )

    try:
        result = await paper_trading_engine.execute_order(db, portfolio.id, req)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/preview-charges", response_model=ChargeBreakdown)
async def preview_charges(
    direction: str = Query("BUY"),
    order_mode: str = Query("INVESTMENT"),
    quantity: int = Query(..., gt=0),
    price: float = Query(..., gt=0)
):
    """Preview accurate Indian statutory levies (STT, Stamp Duty, GST, Exchange fees)."""
    return calculate_charges(
        direction=direction,
        order_mode=order_mode,
        quantity=quantity,
        price=Decimal(str(price)),
        is_intraday=(order_mode.upper() == "TRADING")
    )
