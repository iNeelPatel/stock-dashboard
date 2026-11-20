import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import engine, Base

@pytest.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.anyio
async def test_health_and_indices_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Health check
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["primary_provider"] == "UPSTOX"

        # Market Indices
        res_idx = await client.get("/api/v1/market/indices")
        assert res_idx.status_code == 200
        indices = res_idx.json()
        assert len(indices) >= 5

        # Stock Search
        res_search = await client.get("/api/v1/market/search?q=tata")
        assert res_search.status_code == 200
        results = res_search.json()
        assert any(r["symbol"] == "TATAMOTORS" for r in results)

@pytest.mark.anyio
async def test_ai_scanner_and_recommendation_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # AI Scanner
        res_scan = await client.get("/api/v1/ai/scanner?mode=INVESTMENT")
        assert res_scan.status_code == 200
        scans = res_scan.json()
        assert len(scans) > 0
        assert scans[0]["opportunity_score"] > 0

        # AI Performance
        res_perf = await client.get("/api/v1/ai/performance")
        assert res_perf.status_code == 200
        perf = res_perf.json()
        assert perf["total_recommendations"] > 0
        assert perf["win_rate_pct"] > 50.0

@pytest.mark.anyio
async def test_trading_summary_and_tax_preview():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Summary
        res_sum = await client.get("/api/v1/trading/summary?mode=INVESTMENT")
        assert res_sum.status_code == 200
        summary = res_sum.json()
        assert summary["initial_capital"] == 1000000.0

        # Charges Preview
        res_charges = await client.get("/api/v1/trading/preview-charges?direction=BUY&order_mode=INVESTMENT&quantity=10&price=2500")
        assert res_charges.status_code == 200
        charges = res_charges.json()
        assert float(charges["turnover"]) == 25000.0
        assert float(charges["stt"]) > 0

@pytest.mark.anyio
async def test_analytics_heatmap_and_benchmarks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Heatmap
        res_heat = await client.get("/api/v1/analytics/heatmap?mode=INVESTMENT")
        assert res_heat.status_code == 200
        heat = res_heat.json()
        assert "calendar_days" in heat
        assert len(heat["calendar_days"]) >= 365

        # Benchmarks
        res_bench = await client.get("/api/v1/analytics/benchmarks?period_days=90")
        assert res_bench.status_code == 200
        bench = res_bench.json()
        assert "time_series" in bench
        assert len(bench["time_series"]) > 0
