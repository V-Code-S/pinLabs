from integrations.sms_service import MockSMSService
from utils.helpers import format_currency


class NotificationService:
    def __init__(self) -> None:
        self.sms = MockSMSService()

    def build_message(self, summary: dict, split: dict, forecast: dict, language: str = "en") -> str:
        safe_days = forecast.get("risk_window_days") or "5+"
        english = (
            f"Sales today {format_currency(summary['daily_sales'])}. "
            f"{format_currency(split['supplier_payment'])} supplier paid. "
            f"{format_currency(split['savings'])} moved to savings. "
            f"Cash flow safe for {safe_days} days."
        )
        hindi = (
            f"आज की बिक्री {format_currency(summary['daily_sales'])}. "
            f"{format_currency(split['supplier_payment'])} supplier को भेजा गया. "
            f"{format_currency(split['savings'])} savings में डाला गया. "
            f"Cash flow {safe_days} दिनों तक सुरक्षित है."
        )
        kannada = (
            f"ಇಂದಿನ ಮಾರಾಟ {format_currency(summary['daily_sales'])}. "
            f"{format_currency(split['supplier_payment'])} supplier ಗೆ ಕಳುಹಿಸಲಾಗಿದೆ. "
            f"{format_currency(split['savings'])} savings ಗೆ ಹಾಕಲಾಗಿದೆ. "
            f"Cash flow ಮುಂದಿನ {safe_days} ದಿನಗಳಿಗೆ ಸುರಕ್ಷಿತವಾಗಿದೆ."
        )
        translations = {"en": english, "hi": hindi, "kn": kannada}
        return translations.get(language, english)

    def send_summary(self, phone_number: str, message: str) -> dict:
        return self.sms.send(phone_number, message)
