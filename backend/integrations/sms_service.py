from utils.logger import get_logger


logger = get_logger(__name__)


class MockSMSService:
    def send(self, phone_number: str, message: str) -> dict:
        logger.info("Mock SMS -> %s | %s", phone_number, message)
        return {
            "provider": "mock",
            "status": "queued",
            "phone_number": phone_number,
            "message": message,
        }
