import json
from typing import Optional

from sqlalchemy.orm import Session

from agents.decision_engine import DecisionEngine
from app.config import get_settings
from database.models import AgentDecisionLog, MerchantProfile, MerchantSnapshot
from integrations.pinelabs_api import PineLabsAPI
from services.loan_predictor import LoanPredictor
from services.notification_service import NotificationService
from services.payment_splitter import PaymentSplitter
from services.sales_monitor import SalesMonitor
from ml.cashflow_forecast import CashflowForecaster


class CashflowAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.sales_monitor = SalesMonitor()
        self.payment_splitter = PaymentSplitter()
        self.forecaster = CashflowForecaster()
        self.loan_predictor = LoanPredictor()
        self.decision_engine = DecisionEngine()
        self.pinelabs = PineLabsAPI()
        self.notifications = NotificationService()

    def evaluate(
        self,
        db: Session,
        merchant_id: str,
        language: Optional[str] = None,
        execute_actions: bool = False,
    ) -> dict:
        summary = self.sales_monitor.summarize_today(db, merchant_id)
        forecast = self.forecaster.forecast(db, merchant_id)
        loan_signal = self.loan_predictor.should_trigger(forecast)
        split = self.payment_splitter.split(summary["daily_sales"] or 0.0)

        snapshot = (
            db.query(MerchantSnapshot)
            .filter(MerchantSnapshot.merchant_id == merchant_id)
            .first()
        )
        if snapshot is None:
            snapshot = MerchantSnapshot(merchant_id=merchant_id)
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
        profile = (
            db.query(MerchantProfile)
            .filter(MerchantProfile.merchant_id == merchant_id)
            .first()
        )

        snapshot_data = {
            "current_balance": snapshot.current_balance,
            "supplier_due": snapshot.supplier_due,
            "savings_balance": snapshot.savings_balance,
        }
        decision = self.decision_engine.decide(summary, forecast, loan_signal, snapshot_data)

        actions = []
        if execute_actions and decision["decision"] == "pay_supplier":
            payout_amount = min(split.supplier_payment, snapshot.supplier_due)
            response = self.pinelabs.pay_supplier(merchant_id, payout_amount)
            snapshot.current_balance = max(snapshot.current_balance - payout_amount, 0.0)
            snapshot.supplier_due = max(snapshot.supplier_due - payout_amount, 0.0)
            actions.append(response)
        elif execute_actions and decision["decision"] == "trigger_loan":
            response = self.pinelabs.trigger_loan(merchant_id, loan_signal["recommended_amount"])
            snapshot.current_balance += loan_signal["recommended_amount"]
            snapshot.working_capital_available += loan_signal["recommended_amount"]
            actions.append(response)

        split_response = self.pinelabs.split_payment(
            merchant_id=merchant_id,
            supplier_amount=split.supplier_payment,
            savings_amount=split.savings,
            working_capital_amount=split.working_capital,
        )
        if execute_actions:
            snapshot.savings_balance += split.savings
            snapshot.current_balance += split.working_capital
        actions.append(split_response)

        message = self.notifications.build_message(
            summary=summary,
            split={
                "supplier_payment": split.supplier_payment,
                "savings": split.savings,
                "working_capital": split.working_capital,
            },
            forecast=forecast,
            language=language or (profile.preferred_language if profile else self.settings.default_language),
        )
        sms_response = self.notifications.send_summary(
            profile.phone_number if profile else "+919999999999",
            message,
        )

        log = AgentDecisionLog(
            merchant_id=merchant_id,
            decision=decision["decision"],
            rationale=decision["rationale"],
            action_payload=json.dumps({"actions": actions, "sms": sms_response}),
        )
        db.add(log)
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        return {
            "summary": summary,
            "forecast": forecast,
            "loan_signal": loan_signal,
            "decision": decision,
            "actions": actions,
            "notification": sms_response,
            "message": message,
            "snapshot": {
                "current_balance": snapshot.current_balance,
                "supplier_due": snapshot.supplier_due,
                "savings_balance": snapshot.savings_balance,
                "working_capital_available": snapshot.working_capital_available,
            },
            "profile": {
                "owner_name": profile.owner_name if profile else "Demo Merchant",
                "business_name": profile.business_name if profile else "FinFlow Store",
                "phone_number": profile.phone_number if profile else "+919999999999",
                "preferred_language": profile.preferred_language if profile else self.settings.default_language,
                "auto_automation_enabled": profile.auto_automation_enabled if profile else True,
            },
        }
