import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.core.database import Base
from backend.app.models.entities import User, Exchange
from backend.app.services.trading.engine import paper_trading_engine, OrderPlacementRequest

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        # Seed exchange
        nse = Exchange(code="NSE", name="National Stock Exchange of India")
        session.add(nse)
        # Seed test user
        user = User(id="user_test_123", email="investor@terminal.test", hashed_password="dummy", full_name="Test Investor")
        session.add(user)
        await session.commit()
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.anyio
async def test_wallet_initialization_and_buy_order(db_session):
    portfolio = await paper_trading_engine.get_or_create_default_portfolio(db_session, "user_test_123", "INVESTMENT")
    assert portfolio is not None
    wallet = await paper_trading_engine.get_wallet(db_session, portfolio.id)
    assert wallet.cash_balance == Decimal("1000000.00")

    # Buy 20 shares of RELIANCE
    req = OrderPlacementRequest(
        symbol="RELIANCE",
        direction="BUY",
        quantity=20,
        order_type="MARKET",
        mode="INVESTMENT"
    )
    result = await paper_trading_engine.execute_order(db_session, portfolio.id, req)
    assert result["status"] == "FILLED"
    assert result["quantity"] == 20
    assert result["charges"]["stt"] > 0

    # Refresh wallet
    wallet = await paper_trading_engine.get_wallet(db_session, portfolio.id)
    # Wallet balance must be strictly less than 10,00,000 - turnover
    assert wallet.cash_balance < Decimal("1000000.00")

@pytest.mark.anyio
async def test_sell_order_and_oversell_prevention(db_session):
    portfolio = await paper_trading_engine.get_or_create_default_portfolio(db_session, "user_test_123", "INVESTMENT")
    
    # 1. Buy 10 shares of TCS
    buy_req = OrderPlacementRequest(symbol="TCS", direction="BUY", quantity=10, mode="INVESTMENT")
    await paper_trading_engine.execute_order(db_session, portfolio.id, buy_req)

    # 2. Try to oversell 20 shares (should fail)
    oversell_req = OrderPlacementRequest(symbol="TCS", direction="SELL", quantity=20, mode="INVESTMENT")
    with pytest.raises(ValueError, match="Cannot sell 20 shares"):
        await paper_trading_engine.execute_order(db_session, portfolio.id, oversell_req)

    # 3. Sell 5 shares (should succeed)
    sell_req = OrderPlacementRequest(symbol="TCS", direction="SELL", quantity=5, mode="INVESTMENT")
    sell_res = await paper_trading_engine.execute_order(db_session, portfolio.id, sell_req)
    assert sell_res["status"] == "FILLED"

    summary = await paper_trading_engine.get_portfolio_summary(db_session, portfolio.id)
    assert summary["holdings_count"] == 1
    assert summary["holdings"][0]["quantity"] == 5
