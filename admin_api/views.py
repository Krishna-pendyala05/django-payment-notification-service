from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db import connections
from django.db.utils import OperationalError
from payments.models import Payment
from payments.serializers import PaymentSerializer

class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        db_conn = connections['default']
        try:
            db_conn.cursor()
        except OperationalError:
            return Response({"status": "error", "database": "disconnected"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({"status": "ok", "database": "connected"}, status=status.HTTP_200_OK)

class AdminSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        # Counts by status
        total_queued = Payment.objects.filter(status=Payment.Status.QUEUED).count()
        total_processed = Payment.objects.filter(status=Payment.Status.PROCESSED).count()
        total_failed = Payment.objects.filter(status=Payment.Status.FAILED).count()
        
        # Last 5 failed payments
        last_failed = Payment.objects.filter(status=Payment.Status.FAILED).order_by('-updated_at')[:5]
        serializer = PaymentSerializer(last_failed, many=True)
        
        return Response({
            "summary": {
                "QUEUED": total_queued,
                "PROCESSED": total_processed,
                "FAILED": total_failed
            },
            "last_5_failed": serializer.data
        })
