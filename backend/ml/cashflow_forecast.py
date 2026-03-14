from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from database.models import MerchantSnapshot, Transaction
from ml.model_utils import moving_average


class CashflowForecaster:
    def __init__(self) -> None:
        self.settings = get_settings()

    def forecast(self, db: Session, merchant_id: str) -> dict:
        daily_rows = (
            db.query(func.date(Transaction.created_at), func.sum(Transaction.amount))
            .filter(Transaction.merchant_id == merchant_id)
            .group_by(func.date(Transaction.created_at))
            .order_by(func.date(Transaction.created_at))
            .all()
        )
        sales_history = [float(row[1]) for row in daily_rows][-7:]
        expected_daily_sales = moving_average(sales_history, window=3)

        snapshot = (
            db.query(MerchantSnapshot)
            .filter(MerchantSnapshot.merchant_id == merchant_id)
            .first()
        )
        current_balance = snapshot.current_balance if snapshot else 0.0
        supplier_due = snapshot.supplier_due if snapshot else 0.0
        daily_expense = supplier_due / 7 if supplier_due else 12000.0

        points = []
        future_balance = current_balance
        low_balance_day = None
        for day in range(1, self.settings.forecast_horizon_days + 1):
            future_balance = round(future_balance + expected_daily_sales - daily_expense, 2)
            forecast_date = (datetime.utcnow().date() + timedelta(days=day)).isoformat()
            if future_balance < self.settings.loan_trigger_threshold and low_balance_day is None:
                low_balance_day = day
            points.append({"date": forecast_date, "projected_balance": future_balance})

        return {
            "expected_daily_sales": round(expected_daily_sales, 2),
            "projected_balance": future_balance,
            "forecast_points": points,
            "risk_window_days": low_balance_day,
            "threshold_breach": low_balance_day is not None,
        }
