from collections import defaultdict
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import Transaction


class SalesMonitor:
    def summarize_today(self, db: Session, merchant_id: str) -> dict:
        today = datetime.utcnow().date()
        transactions = (
            db.query(Transaction)
            .filter(
                Transaction.merchant_id == merchant_id,
                func.date(Transaction.created_at) == today.isoformat(),
            )
            .all()
        )
        total_sales = round(sum(item.amount for item in transactions), 2)
        hourly_revenue = defaultdict(float)
        last_transaction_at = None
        for item in transactions:
            hourly_revenue[item.created_at.strftime("%H:00")] += item.amount
            if last_transaction_at is None or item.created_at > last_transaction_at:
                last_transaction_at = item.created_at

        trend = "stable"
        if len(transactions) >= 3:
            early = sum(item.amount for item in transactions[: len(transactions) // 2 or 1])
            late = sum(item.amount for item in transactions[len(transactions) // 2 :])
            if late > early * 1.1:
                trend = "up"
            elif late < early * 0.9:
                trend = "down"

        return {
            "transaction_count": len(transactions),
            "daily_sales": total_sales,
            "hourly_revenue": dict(sorted(hourly_revenue.items())),
            "trend": trend,
            "last_transaction_at": last_transaction_at.isoformat() if last_transaction_at else None,
            "updated_at": datetime.utcnow().isoformat(),
        }
