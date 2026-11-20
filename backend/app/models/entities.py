import uuid
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, BigInteger, Numeric, DateTime, Date, Boolean,
    ForeignKey, Text, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def gen_uuid() -> str:
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

# ==========================================
# 1. USER & SETTINGS
# ==========================================
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    settings = relationship("UserSettings", back_populates="user", uselist=False)
    portfolios = relationship("Portfolio", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")
    journals = relationship("InvestmentJournal", back_populates="user")
    alert_rules = relationship("AlertRule", back_populates="user")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    active_mode = Column(String(20), default="INVESTMENT", nullable=False) # 'INVESTMENT' or 'TRADING'
    theme = Column(String(10), default="light", nullable=False)
    broker_provider = Column(String(50), default="DHAN", nullable=False) # 'DHAN', 'UPSTOX', 'KITE'
    encrypted_dhan_token = Column(Text, nullable=True)
    encrypted_upstox_token = Column(Text, nullable=True)
    encrypted_kite_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="settings")


# ==========================================
# 2. EXCHANGES & INSTRUMENTS
# ==========================================
class Exchange(Base):
    __tablename__ = "exchanges"

    code = Column(String(10), primary_key=True) # 'NSE', 'BSE'
    name = Column(String(100), nullable=False)
    timezone = Column(String(50), default="Asia/Kolkata", nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    trading_start_time = Column(String(10), default="09:15:00", nullable=False)
    trading_end_time = Column(String(10), default="15:30:00", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    symbol = Column(String(50), nullable=False, index=True)
    exchange_code = Column(String(10), ForeignKey("exchanges.code"), nullable=False, default="NSE")
    isin = Column(String(20), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    instrument_type = Column(String(20), default="EQUITY", nullable=False) # 'EQUITY' or 'INDEX'
    lot_size = Column(Integer, default=1, nullable=False)
    tick_size = Column(Numeric(6, 4), default=Decimal("0.05"), nullable=False)
    is_tradable = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "exchange_code", name="uq_instrument_symbol_exchange"),
    )

    quote = relationship("MarketQuote", back_populates="instrument", uselist=False)
    profile = relationship("CompanyProfile", back_populates="instrument", uselist=False)
    financials = relationship("FinancialStatement", back_populates="instrument")
    recommendations = relationship("AIRecommendation", back_populates="instrument")


class MarketQuote(Base):
    __tablename__ = "market_quotes"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    instrument_id = Column(String(36), ForeignKey("instruments.id", ondelete="CASCADE"), unique=True, nullable=False)
    ltp = Column(Numeric(12, 2), nullable=False)
    open_price = Column(Numeric(12, 2), nullable=False)
    high_price = Column(Numeric(12, 2), nullable=False)
    low_price = Column(Numeric(12, 2), nullable=False)
    close_prev = Column(Numeric(12, 2), nullable=False)
    volume = Column(BigInteger, default=0, nullable=False)
    turnover = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    day_change = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    day_change_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    provider = Column(String(50), default="DHAN", nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)

    instrument = relationship("Instrument", back_populates="quote")


class HistoricalCandle(Base):
    __tablename__ = "historical_candles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    instrument_id = Column(String(36), ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False)
    timeframe = Column(String(10), nullable=False, default="1d") # '1m', '5m', '15m', '1d'
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Numeric(12, 2), nullable=False)
    high = Column(Numeric(12, 2), nullable=False)
    low = Column(Numeric(12, 2), nullable=False)
    close = Column(Numeric(12, 2), nullable=False)
    volume = Column(BigInteger, default=0, nullable=False)

    __table_args__ = (
        Index("ix_candles_inst_tf_time", "instrument_id", "timeframe", "timestamp"),
        UniqueConstraint("instrument_id", "timeframe", "timestamp", name="uq_candle_inst_tf_time"),
    )


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    instrument_id = Column(String(36), ForeignKey("instruments.id", ondelete="CASCADE"), unique=True, nullable=False)
    market_cap_cr = Column(Numeric(14, 2), nullable=True) # Market Cap in Crore INR
    business_summary = Column(Text, nullable=True)
    promoter_holding_pct = Column(Numeric(6, 2), nullable=True)
    fii_holding_pct = Column(Numeric(6, 2), nullable=True)
    dii_holding_pct = Column(Numeric(6, 2), nullable=True)
    public_holding_pct = Column(Numeric(6, 2), nullable=True)
    ceo_md = Column(String(100), nullable=True)
    headquarters = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    instrument = relationship("Instrument", back_populates="profile")


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    instrument_id = Column(String(36), ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False)
    period_type = Column(String(20), default="ANNUAL", nullable=False) # 'ANNUAL' or 'QUARTERLY'
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)
    revenue = Column(Numeric(14, 2), nullable=False) # in Cr INR
    revenue_growth_yoy = Column(Numeric(8, 4), nullable=True)
    operating_profit = Column(Numeric(14, 2), nullable=False)
    ebitda_margin = Column(Numeric(6, 2), nullable=True)
    net_profit = Column(Numeric(14, 2), nullable=False)
    profit_growth_yoy = Column(Numeric(8, 4), nullable=True)
    eps = Column(Numeric(10, 2), nullable=True)
    pe_ratio = Column(Numeric(10, 2), nullable=True)
    pb_ratio = Column(Numeric(10, 2), nullable=True)
    roe = Column(Numeric(6, 2), nullable=True)
    roce = Column(Numeric(6, 2), nullable=True)
    debt_to_equity = Column(Numeric(6, 2), nullable=True)
    free_cash_flow = Column(Numeric(14, 2), nullable=True)
    dividend_yield = Column(Numeric(6, 2), nullable=True)
    reported_date = Column(Date, nullable=False)

    instrument = relationship("Instrument", back_populates="financials")

    __table_args__ = (
        Index("ix_fin_inst_year_qtr", "instrument_id", "period_type", "fiscal_year", "fiscal_quarter"),
    )


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    instrument_id = Column(String(36), ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False)
    timeframe = Column(String(10), default="1d", nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    sma_20 = Column(Numeric(12, 2), nullable=True)
    sma_50 = Column(Numeric(12, 2), nullable=True)
    sma_200 = Column(Numeric(12, 2), nullable=True)
    ema_20 = Column(Numeric(12, 2), nullable=True)
    ema_50 = Column(Numeric(12, 2), nullable=True)
    ema_200 = Column(Numeric(12, 2), nullable=True)
    rsi_14 = Column(Numeric(8, 2), nullable=True)
    macd_line = Column(Numeric(10, 4), nullable=True)
    macd_signal = Column(Numeric(10, 4), nullable=True)
    macd_hist = Column(Numeric(10, 4), nullable=True)
    bollinger_upper = Column(Numeric(12, 2), nullable=True)
    bollinger_mid = Column(Numeric(12, 2), nullable=True)
    bollinger_lower = Column(Numeric(12, 2), nullable=True)
    vwap = Column(Numeric(12, 2), nullable=True)
    atr_14 = Column(Numeric(10, 2), nullable=True)


# ==========================================
# 3. NEWS & INTELLIGENCE
# ==========================================
class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    source = Column(String(100), nullable=False)
    title = Column(String(300), nullable=False)
    url = Column(String(500), nullable=True)
    content_summary = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False, index=True)
    sentiment = Column(String(20), default="NEUTRAL", nullable=False) # 'POSITIVE', 'NEUTRAL', 'NEGATIVE'
    sentiment_score = Column(Numeric(6, 4), default=Decimal("0.0000"), nullable=False)
    hash_dedup = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime, default=utc_now)


class NewsStockRelation(Base):
    __tablename__ = "news_stock_relations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    news_id = Column(String(36), ForeignKey("news_articles.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Numeric(4, 2), default=Decimal("1.00"), nullable=False)
    impact_summary = Column(String(255), nullable=True)


# ==========================================
# 4. WATCHLISTS
# ==========================================
class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    mode = Column(String(20), default="GENERAL", nullable=False) # 'INVESTMENT', 'TRADING', 'GENERAL'
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    watchlist_id = Column(String(36), ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False)
    target_entry_price = Column(Numeric(12, 2), nullable=True)
    notes = Column(String(255), nullable=True)
    added_at = Column(DateTime, default=utc_now, nullable=False)

    watchlist = relationship("Watchlist", back_populates="items")
    instrument = relationship("Instrument")


# ==========================================
# 5. PAPER TRADING, WALLET & HOLDINGS
# ==========================================
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    mode = Column(String(20), default="INVESTMENT", nullable=False) # 'INVESTMENT' or 'TRADING'
    is_default = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="portfolios")
    wallet = relationship("Wallet", back_populates="portfolio", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="portfolio")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    snapshots = relationship("DailyPortfolioSnapshot", back_populates="portfolio")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), unique=True, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    initial_capital = Column(Numeric(14, 2), default=Decimal("1000000.00"), nullable=False) # ₹10,00,000
    cash_balance = Column(Numeric(14, 2), default=Decimal("1000000.00"), nullable=False)
    reserved_margin = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    portfolio = relationship("Portfolio", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(10), nullable=False) # 'CREDIT' or 'DEBIT'
    category = Column(String(30), nullable=False) # 'INITIAL_DEPOSIT', 'BUY_PAYOUT', 'SELL_RECEIPT', 'STATUTORY_CHARGES'
    amount = Column(Numeric(14, 2), nullable=False)
    balance_after = Column(Numeric(14, 2), nullable=False)
    reference_order_id = Column(String(36), nullable=True)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)

    wallet = relationship("Wallet", back_populates="transactions")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    mode = Column(String(20), default="INVESTMENT", nullable=False) # 'INVESTMENT' or 'TRADING'
    order_type = Column(String(20), default="MARKET", nullable=False) # 'MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LOSS_MARKET'
    direction = Column(String(10), nullable=False) # 'BUY' or 'SELL'
    quantity = Column(Integer, nullable=False)
    filled_quantity = Column(Integer, default=0, nullable=False)
    limit_price = Column(Numeric(12, 2), nullable=True)
    trigger_price = Column(Numeric(12, 2), nullable=True)
    status = Column(String(20), default="PENDING", nullable=False) # 'PENDING', 'OPEN', 'FILLED', 'CANCELLED', 'REJECTED'
    status_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    executed_at = Column(DateTime, nullable=True)

    portfolio = relationship("Portfolio", back_populates="orders")
    instrument = relationship("Instrument")
    trades = relationship("Trade", back_populates="order")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    direction = Column(String(10), nullable=False) # 'BUY' or 'SELL'
    quantity = Column(Integer, nullable=False)
    execution_price = Column(Numeric(12, 2), nullable=False)
    gross_value = Column(Numeric(14, 2), nullable=False)
    brokerage = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    stt = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    exchange_charges = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    gst = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    stamp_duty = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    sebi_charges = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    total_charges = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    net_amount = Column(Numeric(14, 2), nullable=False)
    executed_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    order = relationship("Order", back_populates="trades")
    instrument = relationship("Instrument")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    mode = Column(String(20), default="INVESTMENT", nullable=False)
    total_quantity = Column(Integer, default=0, nullable=False)
    average_buy_price = Column(Numeric(12, 2), nullable=False)
    invested_value = Column(Numeric(14, 2), nullable=False)
    current_ltp = Column(Numeric(12, 2), nullable=False)
    current_value = Column(Numeric(14, 2), nullable=False)
    unrealized_pnl = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    unrealized_pnl_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    realized_pnl = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("portfolio_id", "instrument_id", "mode", name="uq_holding_port_inst_mode"),
    )

    portfolio = relationship("Portfolio", back_populates="holdings")
    instrument = relationship("Instrument")


class DailyPortfolioSnapshot(Base):
    __tablename__ = "daily_portfolio_snapshots"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    total_portfolio_value = Column(Numeric(14, 2), nullable=False)
    invested_value = Column(Numeric(14, 2), nullable=False)
    cash_balance = Column(Numeric(14, 2), nullable=False)
    daily_realized_pnl = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    daily_unrealized_pnl = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    total_daily_pnl = Column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    daily_return_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    trades_count = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("portfolio_id", "date", name="uq_daily_snapshot_port_date"),
    )

    portfolio = relationship("Portfolio", back_populates="snapshots")


# ==========================================
# 6. AI RECOMMENDATIONS & PERFORMANCE TRACKING
# ==========================================
class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    mode = Column(String(20), default="INVESTMENT", nullable=False) # 'INVESTMENT' or 'TRADING'
    recommendation_type = Column(String(20), nullable=False) # 'BUY', 'HOLD', 'WATCH', 'SELL', 'AVOID'
    cmp_at_rec = Column(Numeric(12, 2), nullable=False)
    entry_range_low = Column(Numeric(12, 2), nullable=False)
    entry_range_high = Column(Numeric(12, 2), nullable=False)
    target_1 = Column(Numeric(12, 2), nullable=False)
    target_2 = Column(Numeric(12, 2), nullable=True)
    stop_loss = Column(Numeric(12, 2), nullable=False)
    expected_holding_period = Column(String(50), nullable=False)
    risk_reward_ratio = Column(Numeric(6, 2), nullable=False)
    fundamental_score = Column(Numeric(5, 2), nullable=False)
    technical_score = Column(Numeric(5, 2), nullable=False)
    news_score = Column(Numeric(5, 2), nullable=False)
    risk_score = Column(Numeric(5, 2), nullable=False)
    composite_score = Column(Numeric(5, 2), nullable=False)
    investment_thesis = Column(Text, nullable=False)
    catalysts = Column(Text, nullable=True)
    key_risks = Column(Text, nullable=False)
    ai_model = Column(String(50), default="gemini-2.5-flash", nullable=False)
    model_version = Column(String(20), default="1.0.0", nullable=False)
    status = Column(String(30), default="ACTIVE", nullable=False) # 'ACTIVE', 'ENTRY_TRIGGERED', 'TARGET_REACHED', 'STOP_LOSS_REACHED', 'EXPIRED', 'INVALIDATED'
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)

    instrument = relationship("Instrument", back_populates="recommendations")
    events = relationship("RecommendationEvent", back_populates="recommendation", cascade="all, delete-orphan")
    performance = relationship("RecommendationPerformance", back_populates="recommendation", uselist=False)


class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    recommendation_id = Column(String(36), ForeignKey("ai_recommendations.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False) # 'ENTRY_TRIGGERED', 'TARGET_1_HIT', 'STOP_LOSS_HIT', 'THESIS_INVALIDATED'
    current_price = Column(Numeric(12, 2), nullable=False)
    pnl_percentage = Column(Numeric(8, 4), nullable=False)
    notes = Column(Text, nullable=True)
    event_timestamp = Column(DateTime, default=utc_now, nullable=False)

    recommendation = relationship("AIRecommendation", back_populates="events")


class RecommendationPerformance(Base):
    __tablename__ = "recommendation_performance"

    recommendation_id = Column(String(36), ForeignKey("ai_recommendations.id", ondelete="CASCADE"), primary_key=True)
    final_status = Column(String(30), nullable=False)
    max_gain_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    max_drawdown_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    days_to_outcome = Column(Integer, default=0, nullable=False)
    actual_return_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    benchmark_nifty_return_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    alpha = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)
    brier_score = Column(Numeric(6, 4), nullable=True)
    evaluated_at = Column(DateTime, default=utc_now, nullable=False)

    recommendation = relationship("AIRecommendation", back_populates="performance")


# ==========================================
# 7. AI PREDICTIONS & EVALUATION
# ==========================================
class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    horizon_days = Column(Integer, nullable=False) # 1, 5, 30, 90
    base_price = Column(Numeric(12, 2), nullable=False)
    predicted_bull_price = Column(Numeric(12, 2), nullable=False)
    predicted_base_price = Column(Numeric(12, 2), nullable=False)
    predicted_bear_price = Column(Numeric(12, 2), nullable=False)
    confidence_score = Column(Numeric(5, 2), nullable=False) # 0 to 100
    model_version = Column(String(20), default="1.0.0", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    evaluation_date = Column(Date, nullable=False)


class AIPredictionResult(Base):
    __tablename__ = "ai_prediction_results"

    prediction_id = Column(String(36), ForeignKey("ai_predictions.id", ondelete="CASCADE"), primary_key=True)
    actual_closing_price = Column(Numeric(12, 2), nullable=False)
    percentage_error = Column(Numeric(8, 4), nullable=False)
    directional_accuracy = Column(Boolean, nullable=False)
    is_within_expected_range = Column(Boolean, nullable=False)
    evaluated_at = Column(DateTime, default=utc_now, nullable=False)


class AIAgentRun(Base):
    __tablename__ = "ai_agent_runs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    agent_name = Column(String(50), nullable=False, index=True)
    instrument_id = Column(String(36), nullable=True)
    input_payload_hash = Column(String(64), nullable=False)
    raw_response_json = Column(Text, nullable=False)
    execution_time_ms = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)


# ==========================================
# 8. SCANNER, ALERTS & BENCHMARKS
# ==========================================
class ScannerRun(Base):
    __tablename__ = "scanner_runs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    mode = Column(String(20), default="INVESTMENT", nullable=False)
    preset_name = Column(String(100), nullable=False)
    filters_json = Column(Text, nullable=True)
    stocks_scanned_count = Column(Integer, default=0, nullable=False)
    matches_found_count = Column(Integer, default=0, nullable=False)
    executed_at = Column(DateTime, default=utc_now, nullable=False, index=True)


class ScannerResult(Base):
    __tablename__ = "scanner_results"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    run_id = Column(String(36), ForeignKey("scanner_runs.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    opportunity_score = Column(Numeric(5, 2), nullable=False)
    fundamental_score = Column(Numeric(5, 2), nullable=False)
    technical_score = Column(Numeric(5, 2), nullable=False)
    catalyst_summary = Column(String(300), nullable=True)
    entry_zone = Column(String(100), nullable=True)
    stop_loss = Column(Numeric(12, 2), nullable=True)
    target_price = Column(Numeric(12, 2), nullable=True)

    instrument = relationship("Instrument")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=True)
    category = Column(String(30), nullable=False) # 'PRICE', 'TECHNICAL', 'FUNDAMENTAL', 'NEWS', 'PORTFOLIO_RISK'
    condition_type = Column(String(30), nullable=False) # 'GREATER_THAN', 'LESS_THAN', 'DRAWDOWN_LIMIT'
    threshold_value = Column(Numeric(14, 4), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="alert_rules")
    events = relationship("AlertEvent", back_populates="rule", cascade="all, delete-orphan")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    rule_id = Column(String(36), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)
    trigger_value = Column(Numeric(14, 4), nullable=False)
    ai_explanation = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    triggered_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    rule = relationship("AlertRule", back_populates="events")


class BenchmarkIndex(Base):
    __tablename__ = "benchmark_indices"

    symbol = Column(String(30), primary_key=True) # 'NIFTY50', 'SENSEX', 'NIFTY500'
    name = Column(String(100), nullable=False)
    is_tri = Column(Boolean, default=True, nullable=False)


class BenchmarkSnapshot(Base):
    __tablename__ = "benchmark_snapshots"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    symbol = Column(String(30), ForeignKey("benchmark_indices.symbol"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    closing_value = Column(Numeric(12, 2), nullable=False)
    daily_return_pct = Column(Numeric(8, 4), default=Decimal("0.00"), nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_bench_sym_date"),
    )


class PortfolioBenchmarkResult(Base):
    __tablename__ = "portfolio_benchmark_results"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    benchmark_symbol = Column(String(30), ForeignKey("benchmark_indices.symbol"), nullable=False)
    period = Column(String(10), default="ALL", nullable=False)
    portfolio_twr = Column(Numeric(8, 4), nullable=False)
    benchmark_return = Column(Numeric(8, 4), nullable=False)
    alpha = Column(Numeric(8, 4), nullable=False)
    beta = Column(Numeric(8, 4), nullable=True)
    calculated_at = Column(DateTime, default=utc_now, nullable=False)


class InvestmentJournal(Base):
    __tablename__ = "investment_journals"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trade_id = Column(String(36), ForeignKey("trades.id"), nullable=True)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    entry_thesis = Column(Text, nullable=False)
    exit_review = Column(Text, nullable=True)
    cognitive_biases_identified = Column(String(255), nullable=True)
    lessons_learned = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="journals")
    instrument = relationship("Instrument")


class APIProviderStatus(Base):
    __tablename__ = "api_provider_status"

    provider = Column(String(50), primary_key=True) # 'DHAN', 'UPSTOX', 'KITE', 'SIMULATED'
    is_healthy = Column(Boolean, default=True, nullable=False)
    last_ping_latency_ms = Column(Integer, default=0, nullable=False)
    daily_requests_count = Column(Integer, default=0, nullable=False)
    last_synced_at = Column(DateTime, default=utc_now, nullable=False)
