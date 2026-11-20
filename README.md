# AI Investment Terminal — Indian Stock Market Research & Paper Trading

A production-grade personal investment research, quantitative analysis, portfolio management, and simulated paper-trading platform tailored for the **National Stock Exchange of India (NSE)** and **Bombay Stock Exchange (BSE)**.

Inspired by **Google Finance** (minimal, high-contrast, data-dense UI), **TradingView** (high-performance candlestick charting & indicators), and **Warren Buffett's investment philosophy** (business moat, return on capital employed, intrinsic value, and margin of safety).

---

## 🌟 Key Features

### 1. Indian Market Data Engine
- **Primary Market Adapter:** **Upstox Developer API v2** (with extensible DhanHQ & Kite Connect support).
- **Indices Feed:** Live and tick data for NIFTY 50, SENSEX, NIFTY BANK, NIFTY IT, NIFTY MIDCAP 150, and INDIA VIX.
- **Stock Autocomplete:** Instant search across leading NSE/BSE equities.
- **Historical OHLCV & Technical Suite:** SMA, EMA (20/50/200), RSI (14), MACD, Bollinger Bands, VWAP, and ATR.

### 2. Five Mandatory AI Intelligence Modules
- **Module 1: AI Opportunity Scanner:** Continuous screening across 14 fundamental and technical presets (Buffett-style quality, undervalued plays, high ROCE, technical breakouts, momentum setups, volume anomalies).
- **Module 2: Recommendation Performance Tracker:** Permanent historical tracking with lifecycle state machine (`ACTIVE`, `ENTRY_TRIGGERED`, `TARGET_REACHED`, `STOP_LOSS_REACHED`), win rate, profit factor, alpha over NIFTY 50, and AI self-evaluation retrospectives.
- **Module 3: Investment Mode vs. Trading Mode Isolation:**
  - **Investment Mode (1–5 Years):** Prioritizes business quality, ROCE, ROE, debt-to-equity, free cash flow, and margin of safety.
  - **Trading Mode (1–4 Weeks):** Prioritizes multi-timeframe price action, EMA alignments, ATR stop losses, and minimum 1:2 risk/reward ratios.
- **Module 4: AI Investment Opportunity Alerts:** Real-time event and threshold monitors for price entries, target hit events, quarterly earnings inflections, and portfolio drawdown caps.
- **Module 5: Comprehensive Benchmark Engine:** Time-Weighted Return (TWR) comparative equity curves and alpha/beta/Sharpe metrics relative to NIFTY 50 Total Return Index (TRI).

### 3. Institutional Paper Trading & Wallet Engine
- Initial virtual capital: **₹10,00,000.00**.
- Double-entry immutable financial ledger.
- Exact Indian statutory charge simulation:
  - Securities Transaction Tax (STT): 0.1% delivery, 0.025% intraday.
  - Exchange transaction charges: 0.00345%.
  - Goods and Services Tax (GST): 18% on brokerage + turnover fees.
  - SEBI Turnover Charges: ₹10 per crore (0.0001%).
  - Stamp Duty: 0.015% delivery buy.
- Position tracking with average buy price, current market value, unrealized P&L, and realized P&L.

### 4. Mandatory Personal P&L Heatmap
- **GitHub-style calendar heatmap:** 52-week trading calendar displaying daily realized, unrealized, and net portfolio P&L with 5-tier green/red color intensities.
- **Interactive Day Modal:** Inspect executed trades, net return %, and win/loss breakdown for any calendar session.

---

## 🛠 Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 Async, Pydantic v2, aiosqlite / SQLite (with PostgreSQL / TimescaleDB dual-compatibility), Uvicorn.
- **Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, TradingView Lightweight Charts, Lucide React.
- **Testing:** Pytest with 100% passing unit and integration tests across statutory charges, market data, trading engine, and REST endpoints.

---

## 🚀 Quickstart Guide

### 1. Start Backend API Server
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation available at: `http://127.0.0.1:8000/docs`

### 2. Start Frontend Next.js Terminal
```bash
cd frontend
npm run dev
```
Open terminal in your browser: `http://localhost:3000`

### 3. Run Automated Tests
```bash
PYTHONPATH=. .venv/bin/pytest backend/tests/ -v
```

---

## ⚖️ Financial Disclaimer
This application is strictly for personal investment research, educational learning, and simulated paper trading. It does not execute real-money financial transactions or offer SEBI-registered investment advisory services.
