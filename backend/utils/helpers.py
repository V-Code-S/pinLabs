from datetime import datetime


def format_currency(amount: float) -> str:
    return f"Rs. {amount:,.0f}"


def iso_now() -> str:
    return datetime.utcnow().isoformat() + "Z"
