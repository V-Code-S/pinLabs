import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import AgentDecisionLog, MerchantProfile, MerchantSnapshot, Transaction
from services.payment_splitter import PaymentSplitter
from services.sales_monitor import SalesMonitor
from ml.cashflow_forecast import CashflowForecaster


router = APIRouter(prefix="/cashflow", tags=["cashflow"])


@router.get("/{merchant_id}")
def get_cashflow_overview(merchant_id: str, db: Session = Depends(get_db)):
    sales_monitor = SalesMonitor()
    forecaster = CashflowForecaster()
    payment_splitter = PaymentSplitter()
    summary = sales_monitor.summarize_today(db, merchant_id)
    forecast = forecaster.forecast(db, merchant_id)
    snapshot = (
        db.query(MerchantSnapshot)
        .filter(MerchantSnapshot.merchant_id == merchant_id)
        .first()
    )
    profile = (
        db.query(MerchantProfile)
        .filter(MerchantProfile.merchant_id == merchant_id)
        .first()
    )
    decisions = (
        db.query(AgentDecisionLog)
        .filter(AgentDecisionLog.merchant_id == merchant_id)
        .order_by(AgentDecisionLog.created_at.desc())
        .limit(5)
        .all()
    )
    transactions = (
        db.query(Transaction)
        .filter(Transaction.merchant_id == merchant_id)
        .order_by(Transaction.created_at.desc())
        .limit(8)
        .all()
    )

    return {
        "merchant_id": merchant_id,
        "profile": {
            "owner_name": profile.owner_name if profile else "Demo Merchant",
            "business_name": profile.business_name if profile else "FinFlow Store",
            "phone_number": profile.phone_number if profile else "+919999999999",
            "preferred_language": profile.preferred_language if profile else "en",
            "auto_automation_enabled": profile.auto_automation_enabled if profile else True,
        },
        "summary": summary,
        "forecast": forecast,
        "live_metrics": {
            "updated_at": summary["updated_at"],
            "last_transaction_at": summary["last_transaction_at"],
            "allocation_preview": {
                "payment_amount": 500,
                **payment_splitter.allocate_transaction(500).__dict__,
            },
        },
        "snapshot": {
            "current_balance": snapshot.current_balance if snapshot else 0.0,
            "supplier_due": snapshot.supplier_due if snapshot else 0.0,
            "savings_balance": snapshot.savings_balance if snapshot else 0.0,
            "working_capital_available": snapshot.working_capital_available if snapshot else 0.0,
        },
        "recent_decisions": [
            {
                "decision": item.decision,
                "rationale": item.rationale,
                "created_at": item.created_at.isoformat(),
                "action_payload": json.loads(item.action_payload),
            }
            for item in decisions
        ],
        "recent_transactions": [
            {
                "id": item.id,
                "amount": item.amount,
                "category": item.category,
                "channel": item.channel,
                "created_at": item.created_at.isoformat(),
                "allocation": payment_splitter.allocate_transaction(item.amount).__dict__,
            }
            for item in transactions
        ],
    }
