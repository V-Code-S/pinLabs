from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    merchant_id: Mapped[str] = mapped_column(String(64), index=True, default="merchant-demo")
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="sale")
    channel: Mapped[str] = mapped_column(String(50), default="pos")
    customer_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class MerchantSnapshot(Base):
    __tablename__ = "merchant_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    merchant_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    current_balance: Mapped[float] = mapped_column(Float, default=50000.0)
    supplier_due: Mapped[float] = mapped_column(Float, default=60000.0)
    savings_balance: Mapped[float] = mapped_column(Float, default=10000.0)
    working_capital_available: Mapped[float] = mapped_column(Float, default=15000.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MerchantProfile(Base):
    __tablename__ = "merchant_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    merchant_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    owner_name: Mapped[str] = mapped_column(String(120), default="Demo Merchant")
    business_name: Mapped[str] = mapped_column(String(160), default="FinFlow Store")
    phone_number: Mapped[str] = mapped_column(String(20), default="+919999999999")
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    auto_automation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentDecisionLog(Base):
    __tablename__ = "agent_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    merchant_id: Mapped[str] = mapped_column(String(64), index=True)
    decision: Mapped[str] = mapped_column(String(100))
    rationale: Mapped[str] = mapped_column(Text)
    action_payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
