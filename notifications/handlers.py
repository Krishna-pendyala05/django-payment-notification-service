from abc import ABC, abstractmethod
import structlog
import time

logger = structlog.get_logger(__name__)

class BaseNotificationHandler(ABC):
    @abstractmethod
    def send(self, payment_data: dict) -> bool:
        pass

class LoggingNotificationHandler(BaseNotificationHandler):
    def send(self, payment_data: dict) -> bool:
        # Simulate notification processing with a small delay
        time.sleep(0.1)
        
        logger.info(
            "Notification event",
            event_type="payment_notification",
            payment_id=str(payment_data.get('payment_id')),
            recipient=payment_data.get('recipient_email'),
            amount=str(payment_data.get('amount')),
            currency=payment_data.get('currency')
        )
        return True
