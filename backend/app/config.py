from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinFlow Agent"
    api_prefix: str = "/api"
    database_url: str = Field(
        default="sqlite:///./finflow.db",
        description="SQLite default keeps the hackathon setup simple.",
    )
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    pine_labs_mid: str = "121523"
    pine_labs_client_id: str = "80b85ede-7d73-496b-ac86-4717b56d6cd9"
    pine_labs_client_secret: str = "6b521a9ac6f34ea1b1c3274f41d725f8"
    pine_labs_base_url: str = "https://api.pluralonline.com"
    pine_labs_uat_base_url: str = "https://pluraluat.v2.pinepg.in"
    pine_labs_prod_base_url: str = "https://api.pluralpay.in"
    pine_labs_auth_path: str = "/api/auth/v1/token"
    pine_labs_payments_path: str = "/v3/payments"
    pine_labs_checkout_orders_path: str = "/api/checkout/v1/orders"
    pine_labs_refunds_path: str = "/v3/refunds"
    pine_labs_payment_split_path: str = "/v3/payment-splits"
    pine_labs_loan_request_path: str = "/v3/loans"
    pine_labs_webhook_secret: Optional[str] = None
    pine_labs_timeout_seconds: float = 10.0
    pine_labs_environment: str = "uat"
    pine_labs_use_mock: bool = False
    public_webhook_base_url: str = "https://eight-animals-drop.loca.lt"
    forecast_horizon_days: int = 5
    supplier_split_ratio: float = 0.5
    savings_split_ratio: float = 0.3
    working_capital_split_ratio: float = 0.2
    emi_allocation_ratio: float = 0.3
    savings_allocation_ratio: float = 0.2
    grocery_allocation_ratio: float = 0.4
    cash_reserve_allocation_ratio: float = 0.1
    cash_buffer_threshold: float = 25000.0
    loan_trigger_threshold: float = 15000.0
    default_language: str = "en"
    sms_provider: str = "mock"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
