from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from backend.app.core.config import settings
from backend.app.core.tax_calculator import calculate_charges, round_curr
from backend.app.models.entities import (
    User, Portfolio, Wallet, WalletTransaction, Order, Trade, Holding, DailyPortfolioSnapshot, Instrument
)
from backend.app.services.market_data.service import market_data_service

class OrderPlacementRequest:
    def __init__(
        self,
        symbol: str,
        direction: str, # "BUY" or "SELL"
        quantity: int,
        order_type: str = "MARKET", # "MARKET", "LIMIT", "STOP_LOSS"
        mode: str = "INVESTMENT", # "INVESTMENT" or "TRADING"
        limit_price: Optional[Decimal] = None,
        trigger_price: Optional[Decimal] = None
    ):
        self.symbol = symbol.upper()
        self.direction = direction.upper()
        self.quantity = quantity
        self.order_type = order_type.upper()
        self.mode = mode.upper()
        self.limit_price = limit_price
        self.trigger_price = trigger_price

class PaperTradingEngine:
    async def get_or_create_default_portfolio(self, db: AsyncSession, user_id: str, mode: str = "INVESTMENT") -> Portfolio:
        stmt = select(Portfolio).where(and_(Portfolio.user_id == user_id, Portfolio.mode == mode))
        res = await db.execute(stmt)
        portfolio = res.scalar_one_or_none()
        
        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                name=f"Primary {mode.capitalize()} Portfolio",
                mode=mode,
                is_default=True
            )
            db.add(portfolio)
            await db.flush()

            # Create wallet with ₹10,00,000 initial capital
            wallet = Wallet(
                portfolio_id=portfolio.id,
                currency="INR",
                initial_capital=settings.INITIAL_WALLET_BALANCE,
                cash_balance=settings.INITIAL_WALLET_BALANCE,
                reserved_margin=Decimal("0.00")
            )
            db.add(wallet)
            await db.flush()

            # Create initial deposit ledger transaction
            initial_tx = WalletTransaction(
                wallet_id=wallet.id,
                type="CREDIT",
                category="INITIAL_DEPOSIT",
                amount=settings.INITIAL_WALLET_BALANCE,
                balance_after=settings.INITIAL_WALLET_BALANCE,
                description="Initial virtual capital credited"
            )
            db.add(initial_tx)
            await db.commit()
            await db.refresh(portfolio)

        return portfolio

    async def get_wallet(self, db: AsyncSession, portfolio_id: str) -> Optional[Wallet]:
        stmt = select(Wallet).where(Wallet.portfolio_id == portfolio_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def execute_order(
        self,
        db: AsyncSession,
        portfolio_id: str,
        req: OrderPlacementRequest
    ) -> Dict[str, Any]:
        """
        Executes or opens a simulated order with statutory tax deductions and balance validation.
        """
        if req.quantity <= 0:
            raise ValueError("Order quantity must be greater than zero.")

        # 1. Fetch current quote
        quote = await market_data_service.get_quote(req.symbol)
        exec_price = quote.ltp if req.order_type == "MARKET" else (req.limit_price or quote.ltp)

        # 2. Find or register instrument
        stmt_inst = select(Instrument).where(Instrument.symbol == req.symbol)
        inst_res = await db.execute(stmt_inst)
        instrument = inst_res.scalar_one_or_none()
        if not instrument:
            instrument = Instrument(
                symbol=req.symbol,
                exchange_code="NSE",
                name=req.symbol,
                instrument_type="EQUITY",
                lot_size=1,
                tick_size=Decimal("0.05")
            )
            db.add(instrument)
            await db.flush()

        # 3. Calculate statutory charges
        is_intraday = (req.mode == "TRADING")
        charges = calculate_charges(
            direction=req.direction,
            order_mode=req.mode,
            quantity=req.quantity,
            price=exec_price,
            is_intraday=is_intraday
        )

        wallet = await self.get_wallet(db, portfolio_id)
        if not wallet:
            raise ValueError("Portfolio wallet not found.")

        # 4. Validate Funds / Holdings
        if req.direction == "BUY":
            if wallet.cash_balance < charges.net_amount:
                raise ValueError(
                    f"Insufficient funds: Required ₹{charges.net_amount:,.2f} (Turnover: ₹{charges.turnover:,.2f} + Taxes: ₹{charges.total_charges:,.2f}), Available: ₹{wallet.cash_balance:,.2f}"
                )
        else: # SELL
            # Check existing holdings
            stmt_hold = select(Holding).where(
                and_(
                    Holding.portfolio_id == portfolio_id,
                    Holding.instrument_id == instrument.id,
                    Holding.mode == req.mode
                )
            )
            hold_res = await db.execute(stmt_hold)
            holding = hold_res.scalar_one_or_none()
            if not holding or holding.total_quantity < req.quantity:
                avail_qty = holding.total_quantity if holding else 0
                raise ValueError(f"Cannot sell {req.quantity} shares of {req.symbol}. Available: {avail_qty}")

        # 5. Create Order Record
        order = Order(
            portfolio_id=portfolio_id,
            instrument_id=instrument.id,
            mode=req.mode,
            order_type=req.order_type,
            direction=req.direction,
            quantity=req.quantity,
            filled_quantity=req.quantity if req.order_type == "MARKET" else 0,
            limit_price=req.limit_price,
            trigger_price=req.trigger_price,
            status="FILLED" if req.order_type == "MARKET" else "OPEN",
            executed_at=datetime.now(timezone.utc) if req.order_type == "MARKET" else None
        )
        db.add(order)
        await db.flush()

        # If Market Order, execute immediately:
        if order.status == "FILLED":
            # Create Trade Record
            trade = Trade(
                order_id=order.id,
                portfolio_id=portfolio_id,
                instrument_id=instrument.id,
                direction=req.direction,
                quantity=req.quantity,
                execution_price=exec_price,
                gross_value=charges.turnover,
                brokerage=charges.brokerage,
                stt=charges.stt,
                exchange_charges=charges.exchange_charges,
                gst=charges.gst,
                stamp_duty=charges.stamp_duty,
                sebi_charges=charges.sebi_charges,
                total_charges=charges.total_charges,
                net_amount=charges.net_amount,
                executed_at=datetime.now(timezone.utc)
            )
            db.add(trade)

            # Update Wallet & Ledger
            if req.direction == "BUY":
                wallet.cash_balance -= charges.net_amount
                tx = WalletTransaction(
                    wallet_id=wallet.id,
                    type="DEBIT",
                    category="BUY_PAYOUT",
                    amount=charges.net_amount,
                    balance_after=wallet.cash_balance,
                    reference_order_id=order.id,
                    description=f"Bought {req.quantity} {req.symbol} @ ₹{exec_price:.2f} + ₹{charges.total_charges:.2f} taxes"
                )
                db.add(tx)

                # Update or create Holding
                stmt_hold = select(Holding).where(
                    and_(
                        Holding.portfolio_id == portfolio_id,
                        Holding.instrument_id == instrument.id,
                        Holding.mode == req.mode
                    )
                )
                hold_res = await db.execute(stmt_hold)
                holding = hold_res.scalar_one_or_none()

                if not holding:
                    holding = Holding(
                        portfolio_id=portfolio_id,
                        instrument_id=instrument.id,
                        mode=req.mode,
                        total_quantity=req.quantity,
                        average_buy_price=exec_price,
                        invested_value=charges.turnover,
                        current_ltp=exec_price,
                        current_value=charges.turnover,
                        unrealized_pnl=Decimal("0.00"),
                        unrealized_pnl_pct=Decimal("0.00"),
                        realized_pnl=Decimal("0.00")
                    )
                    db.add(holding)
                else:
                    new_qty = holding.total_quantity + req.quantity
                    new_invested = holding.invested_value + charges.turnover
                    holding.average_buy_price = round_curr(new_invested / Decimal(new_qty))
                    holding.total_quantity = new_qty
                    holding.invested_value = new_invested
                    holding.current_ltp = exec_price
                    holding.current_value = round_curr(Decimal(new_qty) * exec_price)
                    holding.unrealized_pnl = holding.current_value - holding.invested_value
                    holding.unrealized_pnl_pct = round_curr((holding.unrealized_pnl / holding.invested_value) * 100)

            else: # SELL
                wallet.cash_balance += charges.net_amount
                tx = WalletTransaction(
                    wallet_id=wallet.id,
                    type="CREDIT",
                    category="SELL_RECEIPT",
                    amount=charges.net_amount,
                    balance_after=wallet.cash_balance,
                    reference_order_id=order.id,
                    description=f"Sold {req.quantity} {req.symbol} @ ₹{exec_price:.2f} - ₹{charges.total_charges:.2f} taxes"
                )
                db.add(tx)

                # Update Holding and calculate Realized P&L
                stmt_hold = select(Holding).where(
                    and_(
                        Holding.portfolio_id == portfolio_id,
                        Holding.instrument_id == instrument.id,
                        Holding.mode == req.mode
                    )
                )
                hold_res = await db.execute(stmt_hold)
                holding = hold_res.scalar_one()

                cost_basis_sold = round_curr(holding.average_buy_price * Decimal(req.quantity))
                realized_gain = round_curr((exec_price - holding.average_buy_price) * Decimal(req.quantity) - charges.total_charges)
                
                holding.total_quantity -= req.quantity
                holding.realized_pnl += realized_gain
                
                if holding.total_quantity == 0:
                    holding.invested_value = Decimal("0.00")
                    holding.current_value = Decimal("0.00")
                    holding.unrealized_pnl = Decimal("0.00")
                    holding.unrealized_pnl_pct = Decimal("0.00")
                else:
                    holding.invested_value = round_curr(holding.average_buy_price * Decimal(holding.total_quantity))
                    holding.current_value = round_curr(Decimal(holding.total_quantity) * exec_price)
                    holding.unrealized_pnl = holding.current_value - holding.invested_value
                    holding.unrealized_pnl_pct = round_curr((holding.unrealized_pnl / holding.invested_value) * 100)

            await db.commit()

        return {
            "order_id": order.id,
            "status": order.status,
            "symbol": req.symbol,
            "direction": req.direction,
            "quantity": req.quantity,
            "execution_price": float(exec_price),
            "charges": charges.model_dump()
        }

    async def get_portfolio_summary(self, db: AsyncSession, portfolio_id: str) -> Dict[str, Any]:
        wallet = await self.get_wallet(db, portfolio_id)
        if not wallet:
            return {}

        # Fetch active holdings with instrument details
        stmt = (
            select(Holding, Instrument)
            .join(Instrument, Holding.instrument_id == Instrument.id)
            .where(and_(Holding.portfolio_id == portfolio_id, Holding.total_quantity > 0))
        )
        res = await db.execute(stmt)
        holdings_rows = res.all()

        total_invested = Decimal("0.00")
        total_current_value = Decimal("0.00")
        total_realized_pnl = Decimal("0.00")
        holdings_list = []

        for h, inst in holdings_rows:
            # Refresh with latest market LTP
            quote = await market_data_service.get_quote(inst.symbol)
            cur_ltp = quote.ltp
            cur_val = round_curr(Decimal(h.total_quantity) * cur_ltp)
            unreal_pnl = round_curr(cur_val - h.invested_value)
            unreal_pct = round_curr((unreal_pnl / h.invested_value * 100)) if h.invested_value > 0 else Decimal("0.00")

            total_invested += h.invested_value
            total_current_value += cur_val
            total_realized_pnl += h.realized_pnl

            holdings_list.append({
                "symbol": inst.symbol,
                "name": inst.name,
                "sector": inst.sector,
                "quantity": h.total_quantity,
                "average_price": float(h.average_buy_price),
                "current_price": float(cur_ltp),
                "invested_value": float(h.invested_value),
                "current_value": float(cur_val),
                "unrealized_pnl": float(unreal_pnl),
                "unrealized_pnl_pct": float(unreal_pct),
                "realized_pnl": float(h.realized_pnl),
                "day_change_pct": float(quote.day_change_pct)
            })

        total_portfolio_value = wallet.cash_balance + total_current_value
        total_unrealized_pnl = total_current_value - total_invested
        total_pnl = total_unrealized_pnl + total_realized_pnl
        overall_return_pct = round_curr((total_pnl / wallet.initial_capital) * 100)

        return {
            "portfolio_id": portfolio_id,
            "initial_capital": float(wallet.initial_capital),
            "cash_balance": float(wallet.cash_balance),
            "invested_capital": float(total_invested),
            "current_holdings_value": float(total_current_value),
            "total_portfolio_value": float(total_portfolio_value),
            "unrealized_pnl": float(total_unrealized_pnl),
            "realized_pnl": float(total_realized_pnl),
            "total_pnl": float(total_pnl),
            "overall_return_pct": float(overall_return_pct),
            "holdings_count": len(holdings_list),
            "holdings": holdings_list
        }

paper_trading_engine = PaperTradingEngine()
