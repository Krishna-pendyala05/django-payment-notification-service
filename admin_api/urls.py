from django.urls import path
from .views import HealthCheckView, AdminSummaryView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('admin/summary/', AdminSummaryView.as_view(), name='admin_summary'),
]
