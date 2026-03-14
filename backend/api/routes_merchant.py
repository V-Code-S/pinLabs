from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import MerchantProfile, MerchantSnapshot


router = APIRouter(prefix="/merchant", tags=["merchant"])


class MerchantSignInRequest(BaseModel):
    owner_name: str
    business_name: str
    phone_number: str
    preferred_language: str = "en"
    merchant_id: Optional[str] = None


class MerchantProfileUpdateRequest(BaseModel):
    owner_name: str
    business_name: str
    phone_number: str
    preferred_language: str = "en"
    auto_automation_enabled: bool = True
    current_balance: float = 50000.0
    supplier_due: float = 60000.0
    savings_balance: float = 10000.0
    working_capital_available: float = 15000.0


def serialize_profile(profile: MerchantProfile, snapshot: MerchantSnapshot) -> dict:
    return {
        "merchant_id": profile.merchant_id,
        "owner_name": profile.owner_name,
        "business_name": profile.business_name,
        "phone_number": profile.phone_number,
        "preferred_language": profile.preferred_language,
        "auto_automation_enabled": profile.auto_automation_enabled,
        "current_balance": snapshot.current_balance,
        "supplier_due": snapshot.supplier_due,
        "savings_balance": snapshot.savings_balance,
        "working_capital_available": snapshot.working_capital_available,
    }


def ensure_merchant_records(
    db: Session,
    merchant_id: str,
    owner_name: str,
    business_name: str,
    phone_number: str,
    preferred_language: str,
) -> tuple[MerchantProfile, MerchantSnapshot]:
    profile = (
        db.query(MerchantProfile)
        .filter(MerchantProfile.merchant_id == merchant_id)
        .first()
    )
    if profile is None:
        profile = MerchantProfile(
            merchant_id=merchant_id,
            owner_name=owner_name,
            business_name=business_name,
            phone_number=phone_number,
            preferred_language=preferred_language,
        )
        db.add(profile)

    snapshot = (
        db.query(MerchantSnapshot)
        .filter(MerchantSnapshot.merchant_id == merchant_id)
        .first()
    )
    if snapshot is None:
        snapshot = MerchantSnapshot(merchant_id=merchant_id)
        db.add(snapshot)

    return profile, snapshot


@router.post("/sign-in")
def sign_in(payload: MerchantSignInRequest, db: Session = Depends(get_db)):
    merchant_id = payload.merchant_id or payload.phone_number[-10:] or payload.business_name.lower().replace(" ", "-")
    merchant_id = f"merchant-{merchant_id}"
    profile, snapshot = ensure_merchant_records(
        db=db,
        merchant_id=merchant_id,
        owner_name=payload.owner_name,
        business_name=payload.business_name,
        phone_number=payload.phone_number,
        preferred_language=payload.preferred_language,
    )
    profile.owner_name = payload.owner_name
    profile.business_name = payload.business_name
    profile.phone_number = payload.phone_number
    profile.preferred_language = payload.preferred_language
    db.add(profile)
    db.add(snapshot)
    db.commit()
    db.refresh(profile)
    db.refresh(snapshot)
    return serialize_profile(profile, snapshot)


@router.get("/{merchant_id}/profile")
def get_profile(merchant_id: str, db: Session = Depends(get_db)):
    profile = (
        db.query(MerchantProfile)
        .filter(MerchantProfile.merchant_id == merchant_id)
        .first()
    )
    snapshot = (
        db.query(MerchantSnapshot)
        .filter(MerchantSnapshot.merchant_id == merchant_id)
        .first()
    )
    if profile is None or snapshot is None:
        profile, snapshot = ensure_merchant_records(
            db=db,
            merchant_id=merchant_id,
            owner_name="Demo Merchant",
            business_name="FinFlow Store",
            phone_number="+919999999999",
            preferred_language="en",
        )
        db.commit()
        db.refresh(profile)
        db.refresh(snapshot)
    return serialize_profile(profile, snapshot)


@router.put("/{merchant_id}/profile")
def update_profile(
    merchant_id: str,
    payload: MerchantProfileUpdateRequest,
    db: Session = Depends(get_db),
):
    profile, snapshot = ensure_merchant_records(
        db=db,
        merchant_id=merchant_id,
        owner_name=payload.owner_name,
        business_name=payload.business_name,
        phone_number=payload.phone_number,
        preferred_language=payload.preferred_language,
    )
    profile.owner_name = payload.owner_name
    profile.business_name = payload.business_name
    profile.phone_number = payload.phone_number
    profile.preferred_language = payload.preferred_language
    profile.auto_automation_enabled = payload.auto_automation_enabled

    snapshot.current_balance = payload.current_balance
    snapshot.supplier_due = payload.supplier_due
    snapshot.savings_balance = payload.savings_balance
    snapshot.working_capital_available = payload.working_capital_available

    db.add(profile)
    db.add(snapshot)
    db.commit()
    db.refresh(profile)
    db.refresh(snapshot)
    return serialize_profile(profile, snapshot)
