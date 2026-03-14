import hashlib
import hmac
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import get_cashflow_agent
from app.config import get_settings
from api.routes_agent import manager
from database.db import get_db
from database.models import MerchantProfile, MerchantSnapshot, Transaction
from integrations.pinelabs_api import PineLabsAPI


router = APIRouter(prefix="/transactions", tags=["transactions"])
settings = get_settings()


class TransactionIn(BaseModel):
    merchant_id: str = "merchant-demo"
    amount: float = Field(gt=0)
    category: str = "sale"
    channel: str = "pos"
    customer_ref: Optional[str] = None
    created_at: Optional[datetime] = None
    language: Optional[str] = None


class PineLabsWebhookData(BaseModel):
    payment_id: str
    merchant_id: Optional[str] = None
    amount: float
    currency: str = "INR"
    payment_method: Optional[str] = None
    status: str
    timestamp: datetime
    metadata: Optional[dict] = None


class PineLabsWebhookEvent(BaseModel):
    event: str
    data: PineLabsWebhookData


SUCCESS_EVENT_NAMES = {
    "payment_captured",
    "order_processed",
    "order_captured",
    "payment_success",
    "transaction.captured",
    "charge.succeeded",
}

SUCCESS_STATUSES = {
    "captured",
    "processed",
    "paid",
    "success",
    "charged",
    "completed",
}


async def process_transaction(
    payload: TransactionIn,
    db: Session,
    cashflow_agent,
):
    transaction = Transaction(
        merchant_id=payload.merchant_id,
        amount=payload.amount,
        category=payload.category,
        channel=payload.channel,
        customer_ref=payload.customer_ref,
        created_at=payload.created_at or datetime.utcnow(),
    )
    db.add(transaction)

    snapshot = (
        db.query(MerchantSnapshot)
        .filter(MerchantSnapshot.merchant_id == payload.merchant_id)
        .first()
    )
    if snapshot is None:
        snapshot = MerchantSnapshot(merchant_id=payload.merchant_id)
        db.add(snapshot)
    snapshot.current_balance += payload.amount
    db.commit()
    db.refresh(transaction)

    evaluation = cashflow_agent.evaluate(
        db,
        payload.merchant_id,
        payload.language,
        execute_actions=_should_auto_execute(db, payload.merchant_id),
    )
    await manager.broadcast(
        {
            "type": "transaction_update",
            "merchant_id": payload.merchant_id,
            "payload": evaluation,
        }
    )
    return {
        "transaction_id": transaction.id,
        "status": "accepted",
        "evaluation": evaluation,
    }


def _should_auto_execute(db: Session, merchant_id: str) -> bool:
    profile = (
        db.query(MerchantProfile)
        .filter(MerchantProfile.merchant_id == merchant_id)
        .first()
    )
    return profile.auto_automation_enabled if profile else True


def _nested_get(payload: dict, *keys):
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _parse_timestamp(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if not value:
        return datetime.utcnow()
    normalized = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return datetime.utcnow()


def _verify_webhook_signature(raw_body: bytes, signature: Optional[str]) -> None:
    if not settings.pine_labs_webhook_secret:
        return
    if not signature:
        raise HTTPException(status_code=401, detail="Missing Pine Labs signature")
    digest = hmac.new(
        settings.pine_labs_webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(digest, signature):
        raise HTTPException(status_code=401, detail="Invalid Pine Labs signature")


def _normalize_pinelabs_webhook(payload: dict) -> dict:
    event_name = str(payload.get("event") or payload.get("event_name") or payload.get("type") or "").lower()
    data = payload.get("data") or payload.get("payload") or payload
    if isinstance(data, list):
        data = data[0] if data else {}

    merchant_metadata = _nested_get(data, "merchant_metadata") or _nested_get(payload, "merchant_metadata") or {}
    order_amount = _nested_get(data, "order_amount") or {}
    purchase_customer = _nested_get(data, "purchase_details", "customer") or {}

    order_id = (
        data.get("order_id")
        or data.get("payment_id")
        or data.get("id")
        or payload.get("order_id")
    )
    merchant_id = (
        merchant_metadata.get("finflow_merchant_id")
        or merchant_metadata.get("merchant_id")
        or data.get("merchant_id")
        or payload.get("merchant_id")
    )
    amount = (
        data.get("amount")
        or order_amount.get("value")
        or _nested_get(data, "amount", "value")
        or payload.get("amount")
    )
    status = str(
        data.get("status")
        or payload.get("status")
        or payload.get("response_message")
        or event_name
        or ""
    ).lower()
    payment_method = (
        data.get("payment_method")
        or data.get("payment_method_type")
        or data.get("payment_mode")
        or payload.get("payment_method")
    )
    timestamp = _parse_timestamp(
        data.get("timestamp")
        or data.get("created_at")
        or data.get("updated_at")
        or payload.get("timestamp")
    )

    return {
        "event_name": event_name,
        "merchant_id": merchant_id,
        "order_id": order_id,
        "amount": float(amount) if amount is not None else None,
        "status": status,
        "payment_method": payment_method,
        "timestamp": timestamp,
        "customer_id": purchase_customer.get("customer_id"),
        "raw": payload,
    }


def _hydrate_with_order_status(event: dict) -> dict:
    if not event.get("order_id"):
        return event
    if event.get("amount") is not None and event.get("status"):
        return event

    provider = PineLabsAPI()
    order_result = provider.get_order(event["order_id"])
    order_data = order_result.get("response", {}).get("data") or order_result.get("response", {})
    order_amount = order_data.get("order_amount") or {}
    merchant_metadata = order_data.get("merchant_metadata") or {}

    if event.get("amount") is None:
        value = order_amount.get("value")
        if value is not None:
            event["amount"] = float(value)
    if not event.get("merchant_id"):
        event["merchant_id"] = merchant_metadata.get("finflow_merchant_id") or order_data.get("merchant_id")
    if not event.get("status"):
        event["status"] = str(order_data.get("status") or "").lower()
    if not event.get("payment_method"):
        event["payment_method"] = order_data.get("payment_method")
    return event


def _is_successful_event(event: dict) -> bool:
    event_name = event.get("event_name", "")
    status = event.get("status", "")
    return event_name in SUCCESS_EVENT_NAMES or status in SUCCESS_STATUSES


@router.post("")
async def create_transaction(
    payload: TransactionIn,
    db: Session = Depends(get_db),
    cashflow_agent=Depends(get_cashflow_agent),
):
    return await process_transaction(payload, db, cashflow_agent)


@router.post("/webhooks/pinelabs")
async def receive_pinelabs_webhook(
    request: Request,
    db: Session = Depends(get_db),
    cashflow_agent=Depends(get_cashflow_agent),
    x_webhook_secret: Optional[str] = Header(default=None),
    x_signature: Optional[str] = Header(default=None),
    x_pl_signature: Optional[str] = Header(default=None),
):
    raw_body = await request.body()
    if settings.pine_labs_webhook_secret and x_webhook_secret and x_webhook_secret != settings.pine_labs_webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    _verify_webhook_signature(raw_body, x_pl_signature or x_signature)

    try:
        payload = json.loads(raw_body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    normalized = _normalize_pinelabs_webhook(payload)
    normalized = _hydrate_with_order_status(normalized)

    if not _is_successful_event(normalized):
        return {"status": "ignored", "event": normalized.get("event_name"), "payload": normalized}
    if normalized.get("amount") is None:
        raise HTTPException(status_code=400, detail="Webhook missing transaction amount")
    merchant_id = normalized.get("merchant_id") or normalized.get("customer_id") or "merchant-demo"

    transaction_payload = TransactionIn(
        merchant_id=merchant_id,
        amount=normalized["amount"],
        category="sale",
        channel=normalized["payment_method"].lower() if normalized.get("payment_method") else "pinelabs",
        customer_ref=normalized.get("order_id"),
        created_at=normalized["timestamp"],
        language="en",
    )
    result = await process_transaction(transaction_payload, db, cashflow_agent)
    return {
        "status": "processed",
        "event": normalized.get("event_name"),
        "payment_id": normalized.get("order_id"),
        "result": result,
    }
