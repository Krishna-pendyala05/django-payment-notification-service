import pytest
import uuid
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from payments.models import Payment

@pytest.mark.django_db
class TestPaymentViews:
    def test_intake_success(self, auth_client):
        url = reverse('payment_list_create')
        data = {
            'payment_id': str(uuid.uuid4()),
            'amount': '150.00',
            'currency': 'USD',
            'recipient_email': 'vendor@example.com',
            'description': 'Purchase order 1'
        }
        
        with patch('payments.views.process_payment_notification.delay') as mock_delay:
            response = auth_client.post(url, data)
            
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data['status'] == 'QUEUED'
        assert mock_delay.called

    def test_intake_idempotency_sequential(self, auth_client):
        url = reverse('payment_list_create')
        payment_id = str(uuid.uuid4())
        data = {
            'payment_id': payment_id,
            'amount': '150.00',
            'currency': 'USD',
            'recipient_email': 'vendor@example.com'
        }
        
        # First request
        with patch('payments.views.process_payment_notification.delay'):
            auth_client.post(url, data)
        
        # Second identical request
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert str(response.data['payment_id']) == payment_id

    def test_payment_detail_success(self, auth_client, test_user):
        payment_id = uuid.uuid4()
        Payment.objects.create(
            payment_id=payment_id,
            user=test_user,
            amount=50.00,
            currency='USD',
            recipient_email='test@test.com'
        )
        
        url = reverse('payment_detail', kwargs={'payment_id': payment_id})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['payment_id'] == str(payment_id)

    def test_payment_list_only_returns_own_payments(self, auth_client, test_user, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create_user(username='other', password='pass')
        
        # Own payment
        Payment.objects.create(
            payment_id=uuid.uuid4(),
            user=test_user,
            amount=10.00,
            currency='USD',
            recipient_email='me@test.com'
        )
        # Other's payment
        Payment.objects.create(
            payment_id=uuid.uuid4(),
            user=other_user,
            amount=10.00,
            currency='USD',
            recipient_email='other@test.com'
        )
        
        url = reverse('payment_list_create')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should only see 1 payment
        assert len(response.data['results']) == 1
