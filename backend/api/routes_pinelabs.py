from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import MerchantProfile
from integrations.pinelabs_api import PineLabsAPI


router = APIRouter(prefix="/pinelabs", tags=["pinelabs"])


class CreatePaymentRequest(BaseModel):
    merchant_id: str
    amount: float = Field(gt=0)
    description: str = "FinFlow Merchant Payment"
    order_id: Optional[str] = None


def _merchant_email(profile: MerchantProfile) -> str:
    normalized = profile.business_name.lower().replace(" ", "-")
    return f"{normalized}@finflow.test"


@router.post("/payments/create")
def create_payment(payload: CreatePaymentRequest, db: Session = Depends(get_db)):
    profile = (
        db.query(MerchantProfile)
        .filter(MerchantProfile.merchant_id == payload.merchant_id)
        .first()
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Merchant profile not found")

    order_id = payload.order_id or f"FINFLOW-{payload.merchant_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    pinelabs = PineLabsAPI()
    result = pinelabs.create_payment(
        merchant_id=payload.merchant_id,
        amount=payload.amount,
        order_id=order_id,
        description=payload.description,
        customer_email=_merchant_email(profile),
        customer_contact=profile.phone_number[-10:],
    )

    response_payload = result.get("response", {})
    checkout_url = result.get("checkout_url") or response_payload.get("checkout_url")
    payment_id = result.get("payment_id") or response_payload.get("payment_id")
    status = result.get("status") or response_payload.get("status") or "created"

    return {
        "merchant_id": payload.merchant_id,
        "amount": payload.amount,
        "order_id": order_id,
        "payment_id": payment_id,
        "status": status,
        "checkout_url": checkout_url,
        "provider_result": result,
    }
