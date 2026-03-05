from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Payment
from .serializers import PaymentSerializer

from notifications.services import SQSPublisher

class PaymentListCreateView(generics.ListCreateAPIView):
    # Register the publisher (Dependency Inversion principle)
    # In a more advanced setup, this could be injected via a factory or middleware
    publisher = SQSPublisher()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # We explicitly set the user from request
            payment = serializer.save(user=self.request.user, status=Payment.Status.QUEUED)
            
            # Phase 5 - Publish to SQS here
            try:
                self.publisher.publish(str(payment.payment_id))
            except Exception:
                # In production, we might want to handle this differently (e.g., mark as FAILED or use a separate retry)
                # For now, we continue since the record is saved and Celery/SQS will pick it up or it can be manually re-queued
                pass
            
            return Response({
                "payment_id": payment.payment_id,
                "status": payment.status,
                "message": "Payment accepted and queued for processing."
            }, status=status.HTTP_202_ACCEPTED)
            
        except IntegrityError:
            # Handle duplicate payment_id (idempotency)
            existing_payment = Payment.objects.get(payment_id=request.data.get('payment_id'))
            return Response({
                "payment_id": existing_payment.payment_id,
                "status": existing_payment.status,
                "message": "Payment ID already exists.",
                "current_status": existing_payment.status
            }, status=status.HTTP_409_CONFLICT)

class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'payment_id'

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # FR-02: Returns notification outcome. 
        # We can add notification info from NotificationLog if it exists
        last_notification = instance.notification_logs.order_by('-created_at').first()
        if last_notification:
            data['notification'] = {
                "outcome": last_notification.outcome,
                "attempt_number": last_notification.attempt_number,
                "duration_ms": last_notification.duration_ms,
                "processed_at": last_notification.created_at
            }
        else:
            data['notification'] = None
            
        return Response(data)
