import time
from celery import shared_task
from django.db import transaction
from payments.models import Payment
from .models import NotificationLog
from .handlers import LoggingNotificationHandler
import structlog

logger = structlog.get_logger(__name__)

@shared_task(
    bind=True, 
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=2,  # 2, 4, 8 seconds
    retry_backoff_max=60,
    retry_jitter=False
)
def process_payment_notification(self, payment_uuid):
    """
    Core task to process payment notifications.
    Fetches payment, executes handler, logs result, and updates status.
    """
    start_time = time.time()
    
    try:
        payment = Payment.objects.get(payment_id=payment_uuid)
    except Payment.DoesNotExist:
        logger.error("Payment not found", payment_id=payment_uuid)
        return False

    # FR-07: Idempotency at Worker Level
    if payment.status == Payment.Status.PROCESSED:
        logger.info("Payment already processed, skipping", payment_id=payment_uuid)
        return True

    handler = LoggingNotificationHandler()
    payment_data = {
        'payment_id': payment.payment_id,
        'amount': payment.amount,
        'currency': payment.currency,
        'recipient_email': payment.recipient_email
    }
    
    success = False
    error_msg = None
    
    try:
        success = handler.send(payment_data)
        if not success:
            raise Exception("Notification handler returned False")
    except Exception as e:
        error_msg = str(e)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log the failure attempt
        with transaction.atomic():
            NotificationLog.objects.create(
                payment=payment,
                attempt_number=self.request.retries + 1,
                outcome=NotificationLog.Outcome.FAILURE,
                duration_ms=duration_ms,
                error_message=error_msg
            )
            
            # If this was the last attempt, mark payment as FAILED
            if self.request.retries >= self.max_retries:
                payment.status = Payment.Status.FAILED
                payment.save()
                logger.error("All retries exhausted. Payment marked as FAILED.", payment_id=payment_uuid)
        
        # Re-raise to trigger Celery retry
        raise e

    duration_ms = int((time.time() - start_time) * 1000)
    
    with transaction.atomic():
        # Create success log entry
        NotificationLog.objects.create(
            payment=payment,
            attempt_number=self.request.retries + 1,
            outcome=NotificationLog.Outcome.SUCCESS,
            duration_ms=duration_ms,
            error_message=None
        )
        
        payment.status = Payment.Status.PROCESSED
        payment.save()
        logger.info("Payment processed successfully", payment_id=payment_uuid)
    
    return True
