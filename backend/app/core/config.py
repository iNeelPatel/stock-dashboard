import os
from decimal import Decimal
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Investment Terminal — Indian Equities"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database: Supports SQLite (aiosqlite) or PostgreSQL (asyncpg)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./terminal.db")
    
    # Secret Key for JWT / Sessions
    SECRET_KEY: str = os.getenv("SECRET_KEY", "terminal-super-secret-key-development-mode-2026")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Market Data Providers
    PRIMARY_MARKET_PROVIDER: str = os.getenv("PRIMARY_MARKET_PROVIDER", "UPSTOX") # UPSTOX (Primary), DHAN, KITE, or MARKET_FALLBACK
    
    # DhanHQ Credentials
    DHAN_CLIENT_ID: Optional[str] = os.getenv("DHAN_CLIENT_ID", "")
    DHAN_ACCESS_TOKEN: Optional[str] = os.getenv("DHAN_ACCESS_TOKEN", "")

    # Upstox Credentials
    UPSTOX_API_KEY: Optional[str] = os.getenv("UPSTOX_API_KEY", "")
    UPSTOX_API_SECRET: Optional[str] = os.getenv("UPSTOX_API_SECRET", "")

    # Zerodha Kite Connect Credentials
    KITE_API_KEY: Optional[str] = os.getenv("KITE_API_KEY", "")
    KITE_ACCESS_TOKEN: Optional[str] = os.getenv("KITE_ACCESS_TOKEN", "")

    # AI Model Providers
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_AI_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "gemini-2.5-flash")

    # Paper Trading Defaults
    INITIAL_WALLET_BALANCE: Decimal = Decimal("1000000.00") # ₹10,00,000.00

    # Indian Statutory Charges for Equity Delivery & Intraday
    # Equity Delivery:
    DELIVERY_BROKERAGE_FLAT: Decimal = Decimal("0.00") # Zerodha/Dhan style ₹0 delivery brokerage
    DELIVERY_STT_RATE: Decimal = Decimal("0.001") # 0.1% on buy & sell turnover
    DELIVERY_EXCHANGE_TXN_RATE: Decimal = Decimal("0.0000345") # 0.00345% NSE
    DELIVERY_GST_RATE: Decimal = Decimal("0.18") # 18% on (Brokerage + Exchange Txn + SEBI)
    DELIVERY_SEBI_CHARGES_RATE: Decimal = Decimal("0.000001") # ₹10 per crore (0.0001%)
    DELIVERY_STAMP_DUTY_RATE: Decimal = Decimal("0.00015") # 0.015% on buy turnover only

    # Equity Intraday:
    INTRADAY_BROKERAGE_FLAT: Decimal = Decimal("20.00") # ₹20 max per order
    INTRADAY_BROKERAGE_RATE: Decimal = Decimal("0.0003") # 0.03%
    INTRADAY_STT_RATE: Decimal = Decimal("0.00025") # 0.025% on sell only
    INTRADAY_STAMP_DUTY_RATE: Decimal = Decimal("0.00003") # 0.003% on buy only

    # Risk Management Guardrails
    MAX_POSITION_PORTFOLIO_PCT: Decimal = Decimal("0.15") # Max 15% in single stock
    MAX_SECTOR_PORTFOLIO_PCT: Decimal = Decimal("0.30") # Max 30% in single sector
    MIN_RISK_REWARD_RATIO: Decimal = Decimal("2.0") # Minimum 1:2 R:R for trading mode

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
