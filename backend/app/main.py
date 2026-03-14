from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_agent import router as agent_router
from api.routes_cashflow import router as cashflow_router
from api.routes_merchant import router as merchant_router
from api.routes_pinelabs import router as pinelabs_router
from api.routes_transactions import router as transactions_router
from database.db import Base, engine, SessionLocal
from database.models import MerchantProfile, MerchantSnapshot
from utils.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        snapshot = db.query(MerchantSnapshot).filter(MerchantSnapshot.merchant_id == "merchant-demo").first()
        if snapshot is None:
            db.add(MerchantSnapshot(merchant_id="merchant-demo"))
        profile = db.query(MerchantProfile).filter(MerchantProfile.merchant_id == "merchant-demo").first()
        if profile is None:
            db.add(MerchantProfile(merchant_id="merchant-demo"))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="FinFlow Agent API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router, prefix="/api")
app.include_router(cashflow_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(merchant_router, prefix="/api")
app.include_router(pinelabs_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "name": "FinFlow Agent API",
        "status": "running",
        "health": "/health",
        "docs": "/docs",
        "merchant_profile": "/api/merchant/merchant-demo/profile",
        "webhook": "/api/transactions/webhooks/pinelabs",
    }
