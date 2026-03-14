from utils.helpers import format_currency


class DecisionEngine:
    def decide(self, summary: dict, forecast: dict, loan_signal: dict, snapshot: dict) -> dict:
        daily_sales = summary["daily_sales"]
        supplier_due = snapshot["supplier_due"]
        balance = snapshot["current_balance"]

        if loan_signal["should_trigger"]:
            decision = "trigger_loan"
            rationale = (
                f"Cash shortage predicted in {loan_signal['risk_window_days']} days. "
                f"Projected balance falls below safety threshold, so request {format_currency(loan_signal['recommended_amount'])}."
            )
        elif balance > supplier_due * 0.6 and daily_sales > 20000:
            decision = "pay_supplier"
            rationale = "Healthy inflows and balance support supplier settlement without stressing liquidity."
        else:
            decision = "delay_payment"
            rationale = "Hold supplier payout and preserve working capital until revenue improves."

        return {
            "decision": decision,
            "rationale": rationale,
            "inputs": {
                "daily_revenue": daily_sales,
                "supplier_due": supplier_due,
                "balance": balance,
                "projected_balance": forecast["projected_balance"],
            },
        }
