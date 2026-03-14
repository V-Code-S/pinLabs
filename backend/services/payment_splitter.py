from dataclasses import dataclass

from app.config import get_settings


@dataclass
class PaymentSplit:
    supplier_payment: float
    savings: float
    working_capital: float


@dataclass
class TransactionAllocation:
    emi: float
    savings: float
    grocery: float
    cash_reserve: float


class PaymentSplitter:
    def __init__(self) -> None:
        self.settings = get_settings()

    def split(self, incoming_payment: float) -> PaymentSplit:
        supplier_payment = round(incoming_payment * self.settings.supplier_split_ratio, 2)
        savings = round(incoming_payment * self.settings.savings_split_ratio, 2)
        working_capital = round(incoming_payment - supplier_payment - savings, 2)
        return PaymentSplit(
            supplier_payment=supplier_payment,
            savings=savings,
            working_capital=working_capital,
        )

    def allocate_transaction(self, incoming_payment: float) -> TransactionAllocation:
        emi = round(incoming_payment * self.settings.emi_allocation_ratio, 2)
        savings = round(incoming_payment * self.settings.savings_allocation_ratio, 2)
        grocery = round(incoming_payment * self.settings.grocery_allocation_ratio, 2)
        cash_reserve = round(incoming_payment - emi - savings - grocery, 2)
        return TransactionAllocation(
            emi=emi,
            savings=savings,
            grocery=grocery,
            cash_reserve=cash_reserve,
        )
