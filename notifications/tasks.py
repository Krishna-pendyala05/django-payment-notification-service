import time
from celery import shared_task
from django.db import transaction
from payments.models import Payment
from .models import NotificationLog
from .handlers import LoggingNotificationHandler
import structlog

logger = structlog.get_logger(__name__)

@shared_task(bind=True, max_retries=3)
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

    # Skip if already processed (Idempotency - Part of Phase 7 but good to have)
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
    except Exception as e:
        error_msg = str(e)
        logger.error("Notification handler failed", error=error_msg, payment_id=payment_uuid)

    duration_ms = int((time.time() - start_time) * 1000)
    
    with transaction.atomic():
        # Create log entry
        NotificationLog.objects.create(
            payment=payment,
            attempt_number=self.request.retries + 1,
            outcome=NotificationLog.Outcome.SUCCESS if success else NotificationLog.Outcome.FAILURE,
            duration_ms=duration_ms,
            error_message=error_msg
        )
        
        if success:
            payment.status = Payment.Status.PROCESSED
            payment.save()
            logger.info("Payment processed successfully", payment_id=payment_uuid)
        else:
            # If failed, we will handle retry in Phase 7 logic
            # For now, just mark as failed if last attempt
            if self.request.retries >= self.max_retries:
                payment.status = Payment.Status.FAILED
                payment.save()
    
    return success
