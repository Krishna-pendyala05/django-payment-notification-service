from django.db import models
from payments.models import Payment

class NotificationLog(models.Model):
    class Outcome(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAILURE = 'FAILURE', 'Failure'

    id = models.BigAutoField(primary_key=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='notification_logs')
    attempt_number = models.IntegerField()
    outcome = models.CharField(max_length=10, choices=Outcome.choices)
    duration_ms = models.IntegerField()
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Log for {self.payment.payment_id} - Attempt {self.attempt_number} ({self.outcome})"
