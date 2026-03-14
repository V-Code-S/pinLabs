from app.config import get_settings


class LoanPredictor:
    def __init__(self) -> None:
        self.settings = get_settings()

    def should_trigger(self, forecast: dict) -> dict:
        breach = forecast.get("threshold_breach", False)
        projected_balance = forecast.get("projected_balance", 0.0)
        amount = 0.0
        if breach:
            amount = max(self.settings.cash_buffer_threshold - projected_balance, 25000.0)
        return {
            "should_trigger": breach,
            "recommended_amount": round(amount, 2),
            "risk_window_days": forecast.get("risk_window_days"),
        }
