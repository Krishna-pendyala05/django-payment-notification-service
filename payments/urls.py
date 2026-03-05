from django.urls import path
from .views import PaymentListCreateView, PaymentDetailView

urlpatterns = [
    path('', PaymentListCreateView.as_view(), name='payment_list_create'),
    path('<uuid:payment_id>/', PaymentDetailView.as_view(), name='payment_detail'),
]
