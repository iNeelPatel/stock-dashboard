import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.router_market import router as market_router
from backend.app.api.v1.router_stocks import router as stocks_router
from backend.app.api.v1.router_trading import router as trading_router
from backend.app.api.v1.router_ai import router as ai_router
from backend.app.api.v1.router_analytics import router as analytics_router
from backend.app.api.v1.router_alerts import router as alerts_router
from backend.app.api.v1.router_learning import router as learning_router
from backend.app.services.market_data.service import market_data_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables created
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI-powered Indian stock market research, analysis, and paper trading terminal.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(market_router, prefix=settings.API_V1_STR)
app.include_router(stocks_router, prefix=settings.API_V1_STR)
app.include_router(trading_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(learning_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "primary_provider": settings.PRIMARY_MARKET_PROVIDER
    }

@app.websocket("/ws/market-stream")
async def websocket_market_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Broadcast live quotes for primary indices every 2 seconds
            indices = await market_data_service.get_market_indices()
            data = [i.model_dump(mode="json") for i in indices]
            await websocket.send_json({"type": "MARKET_INDICES", "data": data})
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close()
