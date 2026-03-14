import requests
from typing import Optional
from uuid import uuid4

from app.config import get_settings
from utils.helpers import iso_now
from utils.logger import get_logger


logger = get_logger(__name__)


class PineLabsMockAPI:
    def create_payment(self, merchant_id: str, amount: float, order_id: str, description: str) -> dict:
        return {
            "action": "create_payment",
            "merchant_id": merchant_id,
            "amount": amount,
            "order_id": order_id,
            "status": "created",
            "payment_id": f"pay_{merchant_id}_{int(amount)}",
            "checkout_url": f"https://checkout.pluralonline.com/pay_{merchant_id}_{int(amount)}",
            "description": description,
            "timestamp": iso_now(),
        }

    def fetch_payment(self, payment_id: str) -> dict:
        return {
            "action": "fetch_payment",
            "payment_id": payment_id,
            "status": "captured",
            "timestamp": iso_now(),
        }

    def refund_payment(self, payment_id: str, amount: float) -> dict:
        return {
            "action": "refund",
            "payment_id": payment_id,
            "amount": amount,
            "status": "created",
            "refund_id": f"refund_{payment_id}",
            "timestamp": iso_now(),
        }

    def pay_supplier(self, merchant_id: str, amount: float) -> dict:
        return self.create_payment(
            merchant_id=merchant_id,
            amount=amount,
            order_id=f"SUPPLIER_{merchant_id}_{int(amount)}",
            description="FinFlow Supplier Payment",
        )

    def trigger_loan(self, merchant_id: str, amount: float) -> dict:
        return {
            "action": "loan_request",
            "merchant_id": merchant_id,
            "amount": amount,
            "status": "approved",
            "reference": f"PL-LOAN-{merchant_id}-{int(amount)}",
            "timestamp": iso_now(),
        }

    def split_payment(self, merchant_id: str, supplier_amount: float, savings_amount: float, working_capital_amount: float) -> dict:
        return {
            "action": "payment_split",
            "merchant_id": merchant_id,
            "supplier_amount": supplier_amount,
            "savings_amount": savings_amount,
            "working_capital_amount": working_capital_amount,
            "status": "processed",
            "timestamp": iso_now(),
        }


class PineLabsAPI:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = PineLabsMockAPI()

    def _base_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _should_mock(self) -> bool:
        return self.settings.pine_labs_use_mock or not self.settings.pine_labs_base_url

    def _service_base_url(self) -> str:
        if self.settings.pine_labs_environment.lower() == "prod":
            return self.settings.pine_labs_prod_base_url.rstrip("/")
        return self.settings.pine_labs_uat_base_url.rstrip("/")

    def _request_headers(self) -> dict:
        headers = self._headers()
        headers["Request-ID"] = str(uuid4())
        headers["Request-Timestamp"] = iso_now()
        return headers

    def _authenticate(self) -> Optional[str]:
        if self._should_mock():
            return "mock-access-token"

        url = f"{self._service_base_url()}{self.settings.pine_labs_auth_path}"
        payload = {
            "client_id": self.settings.pine_labs_client_id,
            "client_secret": self.settings.pine_labs_client_secret,
            "grant_type": "client_credentials",
        }
        try:
            auth_headers = self._base_headers()
            auth_headers["Request-ID"] = str(uuid4())
            auth_headers["Request-Timestamp"] = iso_now()
            response = requests.post(
                url,
                json=payload,
                headers=auth_headers,
                timeout=self.settings.pine_labs_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            return data.get("access_token")
        except requests.RequestException as exc:
            logger.warning("Pine Labs auth failed: %s. Falling back to mock mode.", exc)
            return None

    def _headers(self) -> dict:
        headers = self._base_headers()
        token = self._authenticate()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _post(self, path: str, action: str, payload: dict, fallback: dict) -> dict:
        if self._should_mock():
            result = dict(fallback)
            result["mode"] = "mock"
            return result

        url = f"{self._service_base_url()}{path}"
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._request_headers(),
                timeout=self.settings.pine_labs_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            return {
                "action": action,
                "status": "processed",
                "mode": "live",
                "endpoint": url,
                "payload": payload,
                "response": data,
                "timestamp": iso_now(),
            }
        except requests.RequestException as exc:
            logger.warning("Pine Labs live call failed for %s: %s. Falling back to mock.", action, exc)
            result = dict(fallback)
            result["mode"] = "mock_fallback"
            result["error"] = str(exc)
            return result

    def _get(self, path: str, action: str, fallback: dict) -> dict:
        if self._should_mock():
            result = dict(fallback)
            result["mode"] = "mock"
            return result

        url = f"{self._service_base_url()}{path}"
        try:
            response = requests.get(
                url,
                headers=self._request_headers(),
                timeout=self.settings.pine_labs_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            return {
                "action": action,
                "status": "processed",
                "mode": "live",
                "endpoint": url,
                "response": data,
                "timestamp": iso_now(),
            }
        except requests.RequestException as exc:
            logger.warning("Pine Labs live GET failed for %s: %s. Falling back to mock.", action, exc)
            result = dict(fallback)
            result["mode"] = "mock_fallback"
            result["error"] = str(exc)
            return result

    def create_payment(
        self,
        merchant_id: str,
        amount: float,
        order_id: str,
        description: str,
        customer_email: str = "merchant@test.com",
        customer_contact: str = "9999999999",
    ) -> dict:
        if not self._should_mock():
            payload = {
                "merchant_order_reference": order_id,
                "order_amount": {
                    "value": int(round(amount)),
                    "currency": "INR",
                },
                "pre_auth": False,
                "notes": description,
                "purchase_details": {
                    "customer": {
                        "email_id": customer_email,
                        "first_name": "FinFlow",
                        "last_name": "Merchant",
                        "customer_id": merchant_id,
                        "mobile_number": customer_contact[-10:],
                        "country_code": "91",
                    }
                },
                "callback_url": f"{self.settings.public_webhook_base_url.rstrip('/')}/api/transactions/webhooks/pinelabs",
                "failure_callback_url": f"{self.settings.public_webhook_base_url.rstrip('/')}/api/transactions/webhooks/pinelabs",
                "merchant_metadata": {
                    "finflow_merchant_id": merchant_id,
                },
            }
            result = self._post(
                self.settings.pine_labs_checkout_orders_path,
                "create_hosted_checkout",
                payload,
                self.mock.create_payment(merchant_id, amount, order_id, description),
            )
            response_data = result.get("response", {})
            redirect_url = (
                response_data.get("redirect_url")
            )
            order_token = (
                response_data.get("token")
                or response_data.get("order_token")
            )
            if redirect_url is None and order_token:
                redirect_url = f"{self._service_base_url()}/api/v3/checkout-bff/redirect/checkout?token={order_token}"
            result["checkout_url"] = redirect_url
            result["payment_id"] = response_data.get("order_id")
            result["status"] = response_data.get("response_message") or response_data.get("status", result.get("status", "created"))
            return result

        payload = {
            "merchant_id": self.settings.pine_labs_mid,
            "amount": int(round(amount)),
            "currency": "INR",
            "order_id": order_id,
            "description": description,
            "customer": {
                "email": customer_email,
                "contact": customer_contact,
            },
            "metadata": {
                "finflow_merchant_id": merchant_id,
            },
        }
        return self._post(
            self.settings.pine_labs_payments_path,
            "create_payment",
            payload,
            self.mock.create_payment(merchant_id, amount, order_id, description),
        )

    def fetch_payment(self, payment_id: str) -> dict:
        return self._get(
            f"{self.settings.pine_labs_payments_path}/{payment_id}",
            "fetch_payment",
            self.mock.fetch_payment(payment_id),
        )

    def get_order(self, order_id: str) -> dict:
        fallback = {
            "action": "get_order",
            "order_id": order_id,
            "status": "unknown",
            "timestamp": iso_now(),
        }
        return self._get(
            f"/api/pay/v1/orders/{order_id}",
            "get_order",
            fallback,
        )

    def refund_payment(self, payment_id: str, amount: float) -> dict:
        payload = {
            "payment_id": payment_id,
            "amount": int(round(amount)),
            "merchant_id": self.settings.pine_labs_mid,
        }
        return self._post(
            self.settings.pine_labs_refunds_path,
            "refund",
            payload,
            self.mock.refund_payment(payment_id, amount),
        )

    def pay_supplier(self, merchant_id: str, amount: float) -> dict:
        # Keep hackathon automation safe until supplier settlement contract is finalized.
        return self.mock.pay_supplier(merchant_id, amount)

    def trigger_loan(self, merchant_id: str, amount: float) -> dict:
        if self._should_mock():
            return self.mock.trigger_loan(merchant_id, amount)
        payload = {
            "mid": self.settings.pine_labs_mid,
            "merchant_id": merchant_id,
            "amount": amount,
        }
        return self._post(
            self.settings.pine_labs_loan_request_path,
            "loan_request",
            payload,
            self.mock.trigger_loan(merchant_id, amount),
        )

    def split_payment(
        self,
        merchant_id: str,
        supplier_amount: float,
        savings_amount: float,
        working_capital_amount: float,
    ) -> dict:
        if not self._should_mock():
            # Keep live checkout enabled while internal split actions remain demo-safe.
            result = self.mock.split_payment(
                merchant_id,
                supplier_amount,
                savings_amount,
                working_capital_amount,
            )
            result["mode"] = "mock_safety"
            return result
        payload = {
            "mid": self.settings.pine_labs_mid,
            "merchant_id": merchant_id,
            "supplier_amount": supplier_amount,
            "savings_amount": savings_amount,
            "working_capital_amount": working_capital_amount,
        }
        return self._post(
            self.settings.pine_labs_payment_split_path,
            "payment_split",
            payload,
            self.mock.split_payment(
                merchant_id,
                supplier_amount,
                savings_amount,
                working_capital_amount,
            ),
        )
